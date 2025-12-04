import asyncio
from sqlalchemy import text
from db import engine
import sys

# Disable echo if possible, or just ignore it in our logic
engine.echo = False

async def add_img_column():
    results = []
    try:
        async with engine.connect() as conn:
            results.append("Checking columns in pelicula table...")
            result = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'pelicula';"))
            columns = [row[0] for row in result.fetchall()]
            results.append(f"Found columns: {columns}")
            
            if 'img' in columns:
                results.append("IMG column ALREADY EXISTS.")
            else:
                results.append("IMG column MISSING. Attempting to add...")
                await conn.execute(text("ALTER TABLE pelicula ADD COLUMN img VARCHAR;"))
                await conn.commit()
                results.append("IMG column ADDED successfully.")
                
    except Exception as e:
        results.append(f"ERROR: {str(e)}")
        
    # Print to console
    for line in results:
        print(line)
    
    # Also save to file
    with open("add_img_result.txt", "w") as f:
        f.write("\n".join(results))

if __name__ == "__main__":
    asyncio.run(add_img_column())
