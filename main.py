from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

import Spiderman
import universe
import pelicula
from db import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables(app)
    yield
app = FastAPI(lifespan= lifespan, title="Spiderman API")

app.mount("/TemplatesHTML", StaticFiles(directory="TemplatesHTML"), name="TemplatesHTML")
app.include_router(Spiderman.router, tags=["SpiderMan"], prefix="/SpiderMans")
app.include_router(universe.router, tags=["universe"], prefix="/universes")
app.include_router(pelicula.router, tags=["pelicula"], prefix="/peliculas")


Templates = Jinja2Templates(directory="TemplatesHTML")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/nombre/{name]")
async def say_yourName(name: str):
    return {"presentation": f"Mi nombre es {name}"}


