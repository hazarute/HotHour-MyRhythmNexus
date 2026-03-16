#!/usr/bin/env python3
"""
Lokal veritabanini sifirlayip varsayilan test verisini yeniden kurar.

Akis:
1. clear_db.py
2. taxonomy/seed_taxonomy.py --update-existing
3. seed_auctions.py
4. create_admin.py

Kullanim:
    python scripts/reset_and_seed.py
    python scripts/reset_and_seed.py --skip-admin
    python scripts/reset_and_seed.py --admin-studio-name "Neon Fit Academy"
"""

import argparse
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from prisma import Prisma

load_dotenv()


DEFAULT_ADMIN_EMAIL = "local.admin@example.com"
DEFAULT_ADMIN_PASSWORD = "TestPass123!"
DEFAULT_ADMIN_NAME = "Local Admin"
DEFAULT_ADMIN_PHONE = "+905550000001"
DEFAULT_ADMIN_GENDER = "MALE"
DEFAULT_ADMIN_STUDIO_NAME = "Neon Fit Academy"


def run_step(label: str, args: list[str], stdin_text: str | None = None) -> None:
    print(f"\n=== {label} ===")
    command = [sys.executable, *args]
    result = subprocess.run(
        command,
        cwd=project_root,
        input=stdin_text,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


async def find_studio_id_by_name(studio_name: str) -> int | None:
    prisma = Prisma()
    await prisma.connect()

    try:
        studio = await prisma.studio.find_first(where={"name": studio_name})
        return getattr(studio, "id", None)
    finally:
        await prisma.disconnect()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Lokal veritabanini sifirlayip seed eder")
    parser.add_argument("--skip-admin", action="store_true", help="Lokal admin hesabini yeniden olusturma")
    parser.add_argument("--admin-email", default=DEFAULT_ADMIN_EMAIL, help="Olusturulacak admin email")
    parser.add_argument("--admin-password", default=DEFAULT_ADMIN_PASSWORD, help="Olusturulacak admin sifresi")
    parser.add_argument("--admin-name", default=DEFAULT_ADMIN_NAME, help="Olusturulacak admin tam adi")
    parser.add_argument("--admin-phone", default=DEFAULT_ADMIN_PHONE, help="Olusturulacak admin telefon")
    parser.add_argument("--admin-gender", default=DEFAULT_ADMIN_GENDER, help="Olusturulacak admin cinsiyet")
    parser.add_argument(
        "--admin-studio-name",
        default=DEFAULT_ADMIN_STUDIO_NAME,
        help="Adminin baglanacagi studio adi",
    )
    args = parser.parse_args()

    run_step("Veritabani temizleniyor", ["scripts/clear_db.py"], stdin_text="evet\n")
    run_step("Taxonomy seed", ["scripts/taxonomy/seed_taxonomy.py", "--update-existing"])
    run_step("Mock veri seed", ["scripts/seed_auctions.py"])

    if args.skip_admin:
        print("\nAdmin olusturma adimi atlandi.")
        return

    studio_id = await find_studio_id_by_name(args.admin_studio_name)
    if studio_id is None:
        raise SystemExit(f"Admin studio bulunamadi: {args.admin_studio_name}")

    run_step(
        "Lokal admin olusturuluyor",
        [
            "scripts/create_admin.py",
            args.admin_email,
            args.admin_password,
            args.admin_name,
            args.admin_phone,
            args.admin_gender,
            str(studio_id),
        ],
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())