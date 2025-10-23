from db import SessionDep
from fastapi import APIRouter, HTTPException, Depends
from models import Pelicula, peliculaCreate, peliculaUpdate, SpiderMan, SpiderManPeliculaLink
from sqlmodel import select
router = APIRouter()

@router.get("/", response_model=list[Pelicula], summary="Get all Peliculas from the DB")
async def get_all_peliculas(session: SessionDep):
    Peliculas = session.query(Pelicula).all()
    return Peliculas
@router.post("/", response_model=Pelicula)
async def create_peliculas(new_peliculas: peliculaCreate, session:SessionDep):
    pelicula = Pelicula.model_validate(new_peliculas)
    session.add(pelicula)
    session.commit()
    session.refresh(pelicula)
    return pelicula

@router.post("/SpiderMans/{spiderMan_id}/peliculas/{pelicula_id}")
async def add_pelicula_to_spiderMan(spiderMan_id, pelicula_id: int, session: SessionDep):
    spiderman = session.get(SpiderMan, spiderMan_id)
    pelicula = session.get(Pelicula, pelicula_id)

    if not spiderman or not pelicula:
        raise HTTPException(status_code=404, detail="Spider_Man or Pelicula not found")

    statement = select(SpiderManPeliculaLink).where(
        (SpiderManPeliculaLink.spiderMan_id == spiderMan_id) &
        (SpiderManPeliculaLink.pelicula_id == pelicula_id)
    )

    existing_link = session.exec(statement).first()
    if existing_link:
        raise HTTPException(status_code=400, detail="The relationship with Spider_Man to Pelicula already exists")

    link = SpiderManPeliculaLink(spiderMan_id=spiderMan_id, pelicula_id=pelicula_id)
    session.add(link)
    session.commit()
    return {"message": "Relación creada exitosamente"}

@router.patch("/{pelicula_id}", response_model=Pelicula)
async def update_pelicula(new_pelicula: peliculaUpdate, pelicula_id:int, session: SessionDep):
    pelicula_db = session.get(Pelicula, pelicula_id)
    if not pelicula_db:
        raise HTTPException(status_code=404, detail="Pelicula not found")
    pelicula_Update = new_pelicula.model_dump(exclude_unset=True)
    pelicula_db.sqlmodel_update(pelicula_Update)
    session.add(pelicula_db)
    session.commit()
    session.refresh(pelicula_db)
    return pelicula_db


@router.get("/{pelicula_id}", response_model=Pelicula)
async def get_one_Pelicula(pelicula_id: int, session: SessionDep):
    pelicula_db = session.get(Pelicula, pelicula_id)
    if not pelicula_db:
        raise HTTPException(status_code=404, detail="Pelicula not found")
    return pelicula_db