#!/usr/bin/env python3

import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from prisma import Prisma


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    return normalized


def parse_identifier(value: str):
    try:
        return int(value)
    except (TypeError, ValueError):
        return str(value).strip()


async def create_client() -> Prisma:
    prisma = Prisma()
    await prisma.connect()
    return prisma


async def resolve_sector(prisma: Prisma, identifier):
    if isinstance(identifier, int):
        return await prisma.sector.find_unique(where={"id": identifier})
    return await prisma.sector.find_unique(where={"slug": str(identifier)})