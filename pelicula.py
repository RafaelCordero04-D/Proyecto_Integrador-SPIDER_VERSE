from db import SessionDep
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Request
from models import Pelicula, peliculaCreate, peliculaUpdate, SpiderMan, SpiderManPeliculaLink
from sqlmodel import select
from fastapi.templating import Jinja2Templates
from typing import Optional, List
import time

from SupaBase.Supa import upload_to_bucket

router = APIRouter()

Templates = Jinja2Templates(directory="TemplatesHTML")

# MOSTRAR FORMULARIO PARA CREAR PELÍCULA
@router.get("/newPelicula", response_class=HTMLResponse)
async def show_create_pelicula(request: Request, session: SessionDep):
    # Fetch all active Spider-Mans
    result = await session.execute(select(SpiderMan).where(SpiderMan.status == True))
    all_spidermans = result.scalars().all()
    
    return Templates.TemplateResponse("new_pelicula.html", {
        "request": request,
        "all_spidermans": all_spidermans
    })

# CREAR PELÍCULA
@router.post("/", response_model=Pelicula, status_code=201)
async def create_pelicula(
    request: Request,
    session: SessionDep,
    titulo: str = Form(..., alias="titulo"),
    año: int = Form(..., alias="año"),
    taquilla: float = Form(..., alias="taquilla"),
    director: str = Form(..., alias="director"),
    characters: str = Form(..., alias="characters"),
    img: Optional[UploadFile] = File(None),
    spiderman_ids: List[int] = Form([])
):
    print(f"Received data: titulo={titulo}, año={año}, director={director}")
    
    img_url = None
    
    if img and img.filename:
        print(f"Uploading image: {img.filename}")
        try:
            # Append timestamp to filename to avoid duplicates
            timestamp = int(time.time())
            file_extension = img.filename.split('.')[-1] if '.' in img.filename else 'jpg'
            new_filename = f"{img.filename.split('.')[0]}_{timestamp}.{file_extension}"
            img.filename = new_filename
            
            img_url = await upload_to_bucket(img)
            print(f"Image uploaded: {img_url}")
        except Exception as e:
            print(f"Error uploading image: {e}")
            # If upload fails, we log it but don't stop the DB save.
            pass
    
    try:
        new_pelicula = peliculaCreate(
            titulo=titulo,
            año=año,
            taquilla=taquilla,
            director=director,
            characters=characters,
            img=img_url
        )
        print(f"Creating Pelicula object: {new_pelicula}")
        
        pelicula = Pelicula.model_validate(new_pelicula)
        session.add(pelicula)
        await session.commit()
        await session.refresh(pelicula)
        print(f"Pelicula saved with ID: {pelicula.id}")
        
        # Add selected Spider-Mans
        if spiderman_ids:
            for spiderman_id in spiderman_ids:
                link = SpiderManPeliculaLink(pelicula_id=pelicula.id, spiderMan_id=spiderman_id)
                session.add(link)
            await session.commit()
            
    except Exception as e:
        print(f"Error DB: {e}")
        raise HTTPException(status_code=400, detail=f"Error al guardar datos: {str(e)}")
    
    return RedirectResponse(url=f"/peliculas/{pelicula.id}", status_code=302)

# BUSCAR UNA PELÍCULA POR ID
@router.get("/{pelicula_id}", response_class=HTMLResponse)
async def get_one_pelicula(request: Request, pelicula_id: int, session: SessionDep):
    pelicula_db = await session.get(Pelicula, pelicula_id)
    if not pelicula_db:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    
    # Load the SpiderMans relationships
    await session.refresh(pelicula_db, ["spiderMans"])
    
    # Get all available SpiderMans for the dropdown (optional, but good for consistency)
    result = await session.execute(select(SpiderMan).where(SpiderMan.status == True))
    all_spidermans = result.scalars().all()
    
    return Templates.TemplateResponse("pelicula.html", {
        "request": request,
        "pelicula": pelicula_db,
        "spiderMans": pelicula_db.spiderMans,
        "all_spidermans": all_spidermans
    })

# FORMULARIO PARA EDITAR PELÍCULA
@router.get("/{pelicula_id}/edit", response_class=HTMLResponse)
async def edit_pelicula_form(request: Request, pelicula_id: int, session: SessionDep):
    pelicula_db = await session.get(Pelicula, pelicula_id)
    if not pelicula_db:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    
    # Load current relationships
    await session.refresh(pelicula_db, ["spiderMans"])
    
    # Fetch all active Spider-Mans
    result = await session.execute(select(SpiderMan).where(SpiderMan.status == True))
    all_spidermans = result.scalars().all()
    
    return Templates.TemplateResponse("edit_pelicula.html", {
        "request": request,
        "pelicula": pelicula_db,
        "all_spidermans": all_spidermans
    })

# ACTUALIZAR INFORMACIÓN DE LA PELÍCULA
@router.post("/{pelicula_id}/update", response_class=HTMLResponse)
async def update_pelicula(
    request: Request,
    pelicula_id: int,
    session: SessionDep,
    titulo: str = Form(..., alias="titulo"),
    año: int = Form(..., alias="año"),
    taquilla: float = Form(..., alias="taquilla"),
    director: str = Form(..., alias="director"),
    characters: str = Form(..., alias="characters"),
    img: Optional[UploadFile] = File(None),
    spiderman_ids: List[int] = Form([])
):
    pelicula_db = await session.get(Pelicula, pelicula_id)
    if not pelicula_db:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    
    pelicula_db.titulo = titulo
    pelicula_db.año = año
    pelicula_db.taquilla = taquilla
    pelicula_db.director = director
    pelicula_db.characters = characters
    
    if img and img.filename:
        try:
            # Append timestamp to filename to avoid duplicates
            timestamp = int(time.time())
            file_extension = img.filename.split('.')[-1] if '.' in img.filename else 'jpg'
            new_filename = f"{img.filename.split('.')[0]}_{timestamp}.{file_extension}"
            img.filename = new_filename
            
            img_url = await upload_to_bucket(img)
            pelicula_db.img = img_url
        except Exception as e:
            print(f"Error uploading image: {e}")
            # Continue updating other fields even if image upload fails
    
    session.add(pelicula_db)
    await session.commit()
    await session.refresh(pelicula_db)
    
    # Update Spider-Man relationships
    # Get current links
    statement = select(SpiderManPeliculaLink).where(SpiderManPeliculaLink.pelicula_id == pelicula_id)
    results = await session.execute(statement)
    current_links = results.scalars().all()
    current_spiderman_ids = {link.spiderMan_id for link in current_links}
    
    new_spiderman_ids = set(spiderman_ids)
    
    # Remove links that are not in the new list
    for link in current_links:
        if link.spiderMan_id not in new_spiderman_ids:
            await session.delete(link)
            
    # Add new links
    for spiderman_id in new_spiderman_ids:
        if spiderman_id not in current_spiderman_ids:
            link = SpiderManPeliculaLink(pelicula_id=pelicula_id, spiderMan_id=spiderman_id)
            session.add(link)
            
    await session.commit()
    await session.refresh(pelicula_db)
    
    return RedirectResponse(url=f"/peliculas/{pelicula_db.id}", status_code=302)

# ELIMINAR PELÍCULA
@router.post("/{pelicula_id}/delete", response_class=HTMLResponse)
async def delete_pelicula(pelicula_id: int, session: SessionDep):
    pelicula_db = await session.get(Pelicula, pelicula_id)
    if not pelicula_db:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    
    await session.delete(pelicula_db)
    await session.commit()
    
    return RedirectResponse(url="/peliculas/", status_code=302)

# AGREGAR SPIDERMAN A PELÍCULA
@router.post("/{pelicula_id}/add-spiderman", response_class=HTMLResponse)
async def add_spiderman_to_pelicula(
    pelicula_id: int,
    session: SessionDep,
    spiderman_id: int = Form(..., alias="spiderman_id")
):
    pelicula = await session.get(Pelicula, pelicula_id)
    spiderman = await session.get(SpiderMan, spiderman_id)
    
    if not pelicula or not spiderman:
        raise HTTPException(status_code=404, detail="Película o SpiderMan no encontrado")
    
    # Verificar si ya existe la relación
    statement = select(SpiderManPeliculaLink).where(
        (SpiderManPeliculaLink.pelicula_id == pelicula_id) &
        (SpiderManPeliculaLink.spiderMan_id == spiderman_id)
    )
    existing_link = (await session.execute(statement)).first()
    
    if existing_link:
        raise HTTPException(status_code=400, detail="Este SpiderMan ya está en la película")
    
    # Crear la relación
    link = SpiderManPeliculaLink(pelicula_id=pelicula_id, spiderMan_id=spiderman_id)
    session.add(link)
    await session.commit()
    
    return RedirectResponse(url=f"/peliculas/{pelicula_id}", status_code=302)

# QUITAR SPIDERMAN DE PELÍCULA
@router.post("/{pelicula_id}/remove-spiderman/{spiderman_id}", response_class=HTMLResponse)
async def remove_spiderman_from_pelicula(
    pelicula_id: int,
    spiderman_id: int,
    session: SessionDep
):
    # Buscar la relación
    statement = select(SpiderManPeliculaLink).where(
        (SpiderManPeliculaLink.pelicula_id == pelicula_id) &
        (SpiderManPeliculaLink.spiderMan_id == spiderman_id)
    )
    result = await session.execute(statement)
    link = result.scalar_one_or_none()
    
    if not link:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    
    await session.delete(link)
    await session.commit()
    
    return RedirectResponse(url=f"/peliculas/{pelicula_id}", status_code=302)

# LISTAR TODAS LAS PELÍCULAS
@router.get("/", response_class=HTMLResponse)
async def get_all_peliculas(request: Request, session: SessionDep):
    result = await session.execute(select(Pelicula))
    peliculas = result.scalars().all()
    
    # Cargar las relaciones con SpiderMans para cada película
    for pelicula in peliculas:
        await session.refresh(pelicula, ["spiderMans"])
    
    return Templates.TemplateResponse("pelicula_list.html", {
        "request": request,
        "peliculas": peliculas
    })

# ENDPOINT API: Agregar película a SpiderMan (mantener para API)
@router.post("/api/SpiderMans/{spiderMan_id}/peliculas/{pelicula_id}")
async def add_pelicula_to_spiderMan(spiderMan_id: int, pelicula_id: int, session: SessionDep):
    spiderman = await session.get(SpiderMan, spiderMan_id)
    pelicula = await session.get(Pelicula, pelicula_id)

    if not spiderman or not pelicula:
        raise HTTPException(status_code=404, detail="Spider_Man or Pelicula not found")

    statement = select(SpiderManPeliculaLink).where(
        (SpiderManPeliculaLink.spiderMan_id == spiderMan_id) &
        (SpiderManPeliculaLink.pelicula_id == pelicula_id)
    )

    existing_link = (await session.execute(statement)).first()
    if existing_link:
        raise HTTPException(status_code=400, detail="The relationship with Spider_Man to Pelicula already exists")

    link = SpiderManPeliculaLink(spiderMan_id=spiderMan_id, pelicula_id=pelicula_id)
    session.add(link)
    await session.commit()
    return {"message": "Relación creada exitosamente"}