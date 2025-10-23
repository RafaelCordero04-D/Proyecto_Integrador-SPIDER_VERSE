from db import SessionDep
from fastapi import APIRouter, HTTPException
from models import SpiderMan, spiderManCreate, universe, spiderManUpdate

router = APIRouter()

#CREAR SPIDER-MAN
@router.post("/spider-mans", response_model=SpiderMan)
async def create_SpiderMan(new_SpiderMan: spiderManCreate, session: SessionDep):
    spiderMan_data = new_SpiderMan.model_dump()
    universe_db = session.get_one(universe, spiderMan_data.get("universe_id"))
    if not universe_db:
        raise HTTPException(status_code=404, detail="Universe not found")
    spiderMan = SpiderMan.model_validate(spiderMan_data)
    session.add(spiderMan)
    session.commit()
    session.refresh(spiderMan)
    return spiderMan


#BUSCAR UN SPIDERMAN POR ID
@router.get("/spider-mans/{spiderMan_id}", response_model=SpiderMan)
async def get_one_SpiderMan(spiderMan_id: int, session: SessionDep):
    spiderMan_db = session.get(SpiderMan, spiderMan_id)
    if not spiderMan_db:
        raise HTTPException(status_code=404, detail= "SpiderMan not found")
    return spiderMan_db


#BUSCAR TODOS LOS SPIDERMANS
@router.get("/spider-mans", response_model=list[SpiderMan], summary="Get all SpiderMans from the DB")
async def get_all_SpiderMan(session: SessionDep):
    spiderMans = session.query(SpiderMan).all()
    return spiderMans

#ACTULIZAR INFORMACIÓN DEL SPIDERMAN
@router.patch("/spider-mans/{spiderMan_id}", response_model=SpiderMan)
async def update_spiderMan(new_spiderMan: spiderManUpdate, spiderMan_id: int, session: SessionDep):
    spiderMan_db = session.get(SpiderMan, spiderMan_id)
    if not spiderMan_db:
        raise HTTPException(status_code= 404, detail= "SpiderMan not found")
    spiderMan_update = new_spiderMan.model_dump(exclude_unset=True)
    spiderMan_db.sqlmodel_update(spiderMan_update)
    session.add(spiderMan_db)
    session.commit()
    session.refresh(spiderMan_db)
    return spiderMan_db

@router.delete("/spider-mans/{spiderMan_id}")
async def kill_one_spiderMan(spiderMan_id:int, session: SessionDep):
    spiderMan_db = session.get(SpiderMan, spiderMan_id)
    if not spiderMan_db:
        raise HTTPException(status_code = 404, detail="SpiderMan not found")
    session.delete(spiderMan_db)
    session.commit()
    return {"Spider-Man has been deleted"}