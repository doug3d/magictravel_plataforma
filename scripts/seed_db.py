"""
Script CLI para executar seed do banco de dados manualmente.

Uso:
    poetry run python scripts/seed_db.py
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise
from src.configuration import TORTOISE_ORM
from src.seed import seed_database


async def main():
    print("\n🌱 Executando seed do banco de dados...\n")
    
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    
    try:
        await seed_database()
    except Exception as e:
        print(f"seed error: {e}")
        return 1
    finally:
        await Tortoise.close_connections()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

