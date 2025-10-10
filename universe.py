from db import SessionDep
from fastapi import APIRouter, HTTPException
from models import universe, universeCreate

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
