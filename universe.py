from db import SessionDep
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Request
from models import universe, universeCreate, universeUpdate
from sqlmodel import select
from fastapi.templating import Jinja2Templates
from typing import Optional

from SupaBase.Supa import upload_to_bucket
router = APIRouter()

Templates = Jinja2Templates(directory="TemplatesHTML")

@router.get("/newUniverse", response_class=HTMLResponse)
async def show_create(request: Request):
    return Templates.TemplateResponse("new_Universe.html", {"request": request})
@router.post("/", response_model=universe, status_code = 201)
async def create_universe(request: Request,
                          session: SessionDep,
                          name: str = Form(..., alias="nameUniverse"),
                          description: str = Form(..., alias="descriptionUniverse"),
                          characters: str = Form(..., alias="personajesUniverse"),
                          ):
    try:
        new_universe = universeCreate(name=name, description=description, characters=characters)
        Universe = universe.model_validate(new_universe)
        session.add(Universe)
        await session.commit()
        await session.refresh(Universe)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return RedirectResponse(url=f"/universes/{Universe.id}", status_code=302)



@router.get("/{universe_id}", response_class=HTMLResponse)
async def get_one_universe(request: Request, universe_id: int, session: SessionDep):
    universe_db = await session.get(universe, universe_id)
    if not universe_db:
        raise HTTPException(status_code=404, detail="Universe not found")
    await session.refresh(universe_db, ["spiderMans"])
    return Templates.TemplateResponse("universe_detail.html", {"request": request, "universe": universe_db})

@router.get("/", response_class=HTMLResponse)
async def get_all_universes(request: Request, session:SessionDep):
    result = await session.execute(select(universe))
    universes = result.scalars().all()
    return Templates.TemplateResponse("universe_list.html", {"request": request, "universes": universes})

@router.get("/{universe_id}/spiderMans", response_class=HTMLResponse)
async def get_universe_SpiderMans(request: Request, universe_id: int, session: SessionDep):
    Universe = await session.get(universe, universe_id)
    if not Universe:
        raise HTTPException(status_code=404, detail="Universe not found")

    await session.refresh(Universe, ["spiderMans"])

    return Templates.TemplateResponse("universe_spiderMans.html", {"request": request, "universe": Universe, "spiderMans": Universe.spiderMans})

##Formulario para editar Universo

@router.get("/{universe_id}/edit", response_class=HTMLResponse)
async def edit_universe_form(request: Request, universe_id: int, session: SessionDep):
    Universe_db = await session.get(universe, universe_id)
    if not Universe_db:
        raise HTTPException(status_code=404, detail="Universe not found")
    return Templates.TemplateResponse("edit_universe.html", {"request": request, "universe": Universe_db})

##Actualizar informacion de universos
@router.post("/{universe_id}/update", response_class=HTMLResponse)
async def update_universe(
        request: Request,
        universe_id: int,
        session: SessionDep,
        name: str = Form(..., alias="nameUniverse"),
        description: str = Form(..., alias="descriptionUniverse"),
        characters: str = Form(..., alias="personajesUniverse"),

):
    Universe_db = await session.get(universe, universe_id)
    if not Universe_db:
        raise HTTPException(status_code=404, detail="Universe not found")


    Universe_db.name = name
    Universe_db.description = description
    Universe_db.characters = characters

    session.add(Universe_db)
    await session.commit()
    await session.refresh(Universe_db)

    return RedirectResponse(url=f"/universes/{Universe_db.id}", status_code=302)