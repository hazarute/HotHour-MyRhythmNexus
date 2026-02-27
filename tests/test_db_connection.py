#!/usr/bin/env python3
"""scripts/test_db_connection.py

Try to connect to the project's `DATABASE_URL` using several common methods
and print a clear success/failure message. The script will:
 - load `.env` from the repo root if present
 - read `DATABASE_URL`
 - try connectors in order: psycopg (psycopg3), psycopg2, system `psql`, prisma

Exit code: 0 on success, non-zero on failure.
"""
from __future__ import annotations
import os
import sys
import subprocess
import asyncio
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, unquote


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('\"').strip("\'")
        if key not in os.environ:
            os.environ[key] = val


def find_env_file() -> Optional[Path]:
    # script is in repo/scripts; env lives in repo root
    here = Path(__file__).resolve()
    repo_root = here.parents[1]
    env_path = repo_root / ".env"
    return env_path if env_path.exists() else None


def get_database_url() -> Optional[str]:
    env = find_env_file()
    if env:
        load_dotenv(env)
    return os.environ.get("DATABASE_URL")


def normalize_dsn(dsn: str) -> tuple[str, str]:
    """Return a tuple (uri_without_query, libpq_connection_string).

    Many DSNs include query params (e.g. connection_limit) which some
    drivers (psycopg/psycopg2) reject. We parse and return a cleaned URI
    plus a libpq-style connection string for drivers that prefer it.
    """
    try:
        p = urlparse(dsn)
    except Exception:
        return dsn, dsn

    if p.scheme not in ("postgresql", "postgres"):
        return dsn, dsn

    user = unquote(p.username) if p.username else ""
    password = unquote(p.password) if p.password else ""
    host = p.hostname or "localhost"
    port = str(p.port) if p.port else ""
    dbname = p.path.lstrip("/") if p.path else ""

    parts = []
    if host:
        parts.append(f"host={host}")
    if port:
        parts.append(f"port={port}")
    if dbname:
        parts.append(f"dbname={dbname}")
    if user:
        parts.append(f"user={user}")
    if password:
        parts.append(f"password={password}")

    libpq = " ".join(parts)

    # Rebuild a clean URI without query params
    uri = f"{p.scheme}://"
    if user:
        uri += user
        if password:
            uri += ":" + password
        uri += "@"
    uri += host
    if port:
        uri += f":{port}"
    if dbname:
        uri += f"/{dbname}"

    return uri, libpq


def try_psycopg(dsn: str) -> bool:
    try:
        import psycopg

        print("Trying psycopg (psycopg3)...")
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                print("psycopg: OK ->", cur.fetchone())
        return True
    except Exception as e:
        print("psycopg failed:", e)
        return False


def try_psycopg2(dsn: str) -> bool:
    try:
        import psycopg2

        print("Trying psycopg2...")
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        print("psycopg2: OK ->", cur.fetchone())
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("psycopg2 failed:", e)
        return False


def try_psql_cli(dsn: str) -> bool:
    try:
        print("Trying psql CLI...")
        # psql accepts a libpq connection string via PGPASSWORD env or embedded
        # We'll call: psql <dsn> -c "SELECT 1;"
        # If dsn contains special chars, invoking with -c and PG* env may be safer.
        env = os.environ.copy()
        # psql can accept a URI directly as the first arg
        cmd = ["psql", dsn, "-c", "SELECT 1;"]
        res = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=10)
        if res.returncode == 0:
            print("psql: OK")
            print(res.stdout.strip())
            return True
        else:
            print("psql failed:", res.stderr.strip() or res.stdout.strip())
            return False
    except FileNotFoundError:
        print("psql CLI not found on PATH")
        return False
    except Exception as e:
        print("psql attempt error:", e)
        return False


async def try_prisma_async(dsn: str) -> bool:
    try:
        from prisma import Prisma

        print("Trying prisma (python client)...")
        db = Prisma()
        await db.connect()
        # attempt a raw query - Prisma Python provides `query_raw`/`execute_raw`
        try:
            # Try several possible function names to be robust
            if hasattr(db, "execute_raw"):
                await db.execute_raw("SELECT 1;")
            elif hasattr(db, "query_raw"):
                await db.query_raw("SELECT 1;")
            else:
                print("prisma client connected but no execute method found")
            print("prisma: connected (query attempted)")
        finally:
            await db.disconnect()
        return True
    except Exception as e:
        print("prisma attempt failed:", e)
        return False


def main() -> int:
    dsn = get_database_url()
    if not dsn:
        print("DATABASE_URL not found. Please add it to a .env in the repo root or the environment.")
        print("Example: DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/hothour")
        return 2

    print("Using DATABASE_URL:", dsn)
    cleaned_uri, libpq = normalize_dsn(dsn)
    print("Cleaned URI:", cleaned_uri)
    print("Libpq string:", libpq)

    # Try psycopg (psycopg3) using cleaned URI
    if try_psycopg(cleaned_uri):
        return 0

    # Try psycopg2
    # psycopg2 may prefer a libpq style string
    if try_psycopg2(libpq or cleaned_uri):
        return 0

    # Try psql CLI
    # psql CLI accepts URI form
    if try_psql_cli(cleaned_uri):
        return 0

    # Try prisma async client
    try:
        ok = asyncio.run(try_prisma_async(dsn))
        if ok:
            return 0
    except Exception as e:
        print("prisma runtime error:", e)

    print("All connection attempts failed. See messages above for details.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
