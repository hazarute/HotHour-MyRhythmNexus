#!/usr/bin/env python3
"""
Basit Postgres yedekleme helper.

Kullanım:
  - Ortam değişkeni olarak `DATABASE_URL` tanımlıysa:
      python scripts/backup_db.py
  - Veya doğrudan URL ver:
      python scripts/backup_db.py "postgresql://user:pass@host:5432/dbname"

Script `pg_dump` aracını çağırır — çalıştırılacak makinede `pg_dump` yüklü olmalıdır.
"""

import os
import sys
import subprocess
from datetime import datetime
from urllib.parse import urlparse, unquote


def parse_database_url(url: str):
    p = urlparse(url)
    if p.scheme not in ("postgres", "postgresql"):
        raise ValueError("Unsupported scheme: %s" % p.scheme)
    user = unquote(p.username) if p.username else None
    password = unquote(p.password) if p.password else None
    host = p.hostname or "localhost"
    port = p.port or 5432
    db = p.path.lstrip("/")
    return user, password, host, port, db


def main():
    if len(sys.argv) > 1:
        database_url = sys.argv[1]
    else:
        database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        print("Error: DATABASE_URL env not found and no URL argument provided.")
        sys.exit(2)

    try:
        user, password, host, port, db = parse_database_url(database_url)
    except Exception as e:
        print("Error parsing DATABASE_URL:", e)
        sys.exit(2)

    now = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
    out_file = f"hothour_backup_{now}.dump"

    cmd = [
        "pg_dump",
        f"--host={host}",
        f"--port={port}",
        f"--username={user}",
        "--format=custom",
        f"--file={out_file}",
        db,
    ]

    env = os.environ.copy()
    if password:
        env["PGPASSWORD"] = password

    print("Running:", " ".join(cmd))
    try:
        subprocess.check_call(cmd, env=env)
    except FileNotFoundError:
        print("Error: pg_dump not found. Install Postgres client tools on this machine.")
        sys.exit(3)
    except subprocess.CalledProcessError as e:
        print("pg_dump failed with exit code", e.returncode)
        sys.exit(e.returncode)

    print("Backup complete:", out_file)


if __name__ == "__main__":
    main()
