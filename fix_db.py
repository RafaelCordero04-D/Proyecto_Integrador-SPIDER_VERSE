import asyncio
from sqlalchemy import text
from db import engine

async def fix_schema():
    async with engine.begin() as conn:
        print("Adding status column to universe table...")
        try:
            await conn.execute(text("ALTER TABLE universe ADD COLUMN status BOOLEAN DEFAULT TRUE;"))
            print("Column added successfully.")
        except Exception as e:
            print(f"Error (maybe column already exists?): {e}")

if __name__ == "__main__":
    asyncio.run(fix_schema())
