from fastapi import FastAPI

import Spiderman
import universe
from db import create_tables

app = FastAPI(lifespan= create_tables, title="Spiderman API")
app.include_router(Spiderman.router, tags=["SpiderMan"], prefix="/SpiderMans")
app.include_router(universe.router, tags=["universe"], prefix="/universes")


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/nombre/{name]")
async def say_yourName(name: str):
    return {"presentation": f"Mi nombre es {name}"}
