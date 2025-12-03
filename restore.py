from db import SessionDep
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, HTTPException, Request, Form
from models import universe, SpiderMan
from sqlmodel import select
from fastapi.templating import Jinja2Templates

router = APIRouter()
Templates = Jinja2Templates(directory="TemplatesHTML")

# --- UNIVERSES ---

@router.get("/universes", response_class=HTMLResponse)
async def get_inactive_universes(request: Request, session: SessionDep):
    # Fetch universes where status is False
    result = await session.execute(select(universe).where(universe.status == False))
    universes = result.scalars().all()
    return Templates.TemplateResponse("inactive_universes.html", {"request": request, "universes": universes})

@router.post("/universes/{universe_id}/activate", response_class=HTMLResponse)
async def activate_universe(universe_id: int, session: SessionDep):
    universe_db = await session.get(universe, universe_id)
    if not universe_db:
        raise HTTPException(status_code=404, detail="Universe not found")
    
    # Ativa el universo
    universe_db.status = True
    session.add(universe_db)
    
    #Ativa todas las asociaciones con Spiderman
    await session.refresh(universe_db, ["spiderMans"])
    for spider in universe_db.spiderMans:
        spider.status = True
        session.add(spider)
        
    await session.commit()
    return RedirectResponse(url="/restore/universes", status_code=302)

# --- SPIDERMANS ---

@router.get("/spidermans", response_class=HTMLResponse)
async def get_inactive_spidermans(request: Request, session: SessionDep):
    # Fetch spidermans where status is False
    result = await session.execute(select(SpiderMan).where(SpiderMan.status == False))
    spidermans = result.scalars().all()
    

    return Templates.TemplateResponse("inactive_spidermans.html", {"request": request, "spidermans": spidermans})

@router.post("/spidermans/{spider_id}/activate", response_class=HTMLResponse)
async def activate_spiderman(spider_id: int, session: SessionDep):
    spider_db = await session.get(SpiderMan, spider_id)
    if not spider_db:
        raise HTTPException(status_code=404, detail="SpiderMan not found")
    

    universe_db = await session.get(universe, spider_db.universe_id)
    if not universe_db or not universe_db.status:

        raise HTTPException(status_code=400, detail="Cannot activate SpiderMan because its Universe is inactive.")
        
    spider_db.status = True
    session.add(spider_db)
    await session.commit()
    
    return RedirectResponse(url="/restore/spidermans", status_code=302)
