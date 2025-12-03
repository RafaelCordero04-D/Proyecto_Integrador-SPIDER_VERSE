import asyncio
from sqlalchemy import text
from db import engine

async def check_schema():
    async with engine.connect() as conn:
        print("Checking columns in universe table...")
        result = await conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'universe';"))
        columns = result.fetchall()
        print("Columns found:")
        for col in columns:
            print(f"- {col[0]} ({col[1]})")
            
        has_status = any(col[0] == 'status' for col in columns)
        if has_status:
            print("\nSUCCESS: 'status' column exists.")
        else:
            print("\nFAILURE: 'status' column is MISSING.")

if __name__ == "__main__":
    asyncio.run(check_schema())
