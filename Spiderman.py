from db import SessionDep
from fastapi import APIRouter, HTTPException
from models import SpiderMan, spiderManCreate, universe

router = APIRouter()

@router.post("/", response_model=SpiderMan)
async def create_SpiderMan(new_SpiderMan, sesssion: SessionDep):
    spiderMan_data = new_SpiderMan.model_dump()
    universe_db = session.get_one(universe, spiderMan_data.get("universe_id"))
    if not universe_db:
        raise HTTPException(status_code=404, detail="Universe not found")
    spiderMan = SpiderMan.model_validate(spiderMan_data)
    session.add(spiderMan)
    session.commit()
    session.refresh(spiderMan)
    return spiderMan

@router.get("/{spiderMan_id}", response_model=SpiderMan)
async def get_one_SpiderMan(spiderMan_id: int, session: SessionDep):
    spiderMan_db = session.get_one(SpiderMan, spiderMan_id)
    if not spiderMan_db:
        raise HTTPException(status_code=404, detail= "SpiderMan not found")
    return spiderMan_db

@router.get("/", response_model=list[SpiderMan], summary="Get all SpiderMans from the DB")
async def get_all_SpiderMan(session: SessionDep):
    spiderMans = session.query(SpiderMan).all()
    return spiderMans

