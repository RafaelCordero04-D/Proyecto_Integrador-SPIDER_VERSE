import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine, Session
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine

load_dotenv()

SUPABASE_DB = (
    f"postgresql+asyncpg://{os.getenv('POSTGRESQL_ADDON_USER')}:"
    f"{os.getenv('POSTGRESQL_ADDON_PASSWORD')}@"
    f"{os.getenv('POSTGRESQL_ADDON_HOST')}:"
    f"{os.getenv('POSTGRESQL_ADDON_PORT')}/"
    f"{os.getenv('POSTGRESQL_ADDON_DB')}"
)

##db_name = "SpiderMans.sqlite3"
##db_url = f"sqlite:///{db_name}"

engine : AsyncEngine = create_async_engine(SUPABASE_DB, echo=True, pool_pre_ping=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

##Engine con SQL
##engine = create_engine(db_url)

async def create_tables(app:FastAPI):
    print("Iniciando creación de tablas (Alembic o SQLModel)...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async with async_session() as session:
        yield session

SessionDep= Annotated[async_session, Depends(get_session)]

