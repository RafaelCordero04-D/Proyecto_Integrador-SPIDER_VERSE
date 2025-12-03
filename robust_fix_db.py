import asyncio
from sqlalchemy import text
from db import engine
import sys

# Disable echo if possible, or just ignore it in our logic
engine.echo = False

async def fix_schema():
    results = []
    try:
        async with engine.connect() as conn:
            results.append("Checking columns...")
            result = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'universe';"))
            columns = [row[0] for row in result.fetchall()]
            results.append(f"Found columns: {columns}")
            
            if 'status' in columns:
                results.append("Status column ALREADY EXISTS.")
            else:
                results.append("Status column MISSING. Attempting to add...")
                await conn.execute(text("ALTER TABLE universe ADD COLUMN status BOOLEAN DEFAULT TRUE;"))
                await conn.commit()
                results.append("Status column ADDED successfully.")
                
    except Exception as e:
        results.append(f"ERROR: {str(e)}")
        
    with open("db_result.txt", "w") as f:
        f.write("\n".join(results))

if __name__ == "__main__":
    asyncio.run(fix_schema())
