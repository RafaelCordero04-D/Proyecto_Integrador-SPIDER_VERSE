from db import SessionDep
from fastapi import APIRouter, HTTPException
from models import universe, universeCreate, universeUpdate

router = APIRouter()

@router.post("/", response_model=universe, status_code = 201)
async def create_universe(new_universe: universeCreate, session: SessionDep):
    Universe = universe.model_validate(new_universe)
    session.add(Universe)
    session.commit()
    session.refresh(Universe)
    return Universe

@router.get("/{universe_id}", response_model=universe)
async def get_one_universe(universe_id: int, session:SessionDep):
    universe_db = session.get(universe, universe_id)
    if not universe_db:
        raise HTTPException(status_code=404, detail="Universe not found")
    return universe_db

@router.get("/", response_model=list[universe])
async def get_all_users(session:SessionDep):
    users = session.query(universe).all()
    return users

@router.patch("/{universe_id}")
async def update_universe(new_universe: universeUpdate, universe_id:int, session:SessionDep):
    universe_db = session.get_one(universe, universe_id)
    if not universe_db:
        raise HTTPException(status_code=404, detail="Universe not found")
    universe_update = new_universe.model_dump(exclude_unset=True)
    universe_db.sqlmodel_update(universe_update)
    session.add(universe_db)
    session.commit()
    session.refresh(universe_db)
    return universe_db

@router.delete("/{universe_id}")
async def kill_one_universe(universe_id:int, session:SessionDep):
    universe_db = session.get_one(universe, universe_id)
    if not universe_db:
        raise HTTPException(status_code= 404, detail="Universe not found")
    session.delete(universe_db)
    session.commit()
    return {"Universe has been deleted"}