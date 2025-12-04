from db import SessionDep
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Request
from models import SpiderMan, spiderManCreate, universe, spiderManUpdate
from sqlmodel import select
from fastapi.templating import Jinja2Templates
from typing import Optional
import time

from SupaBase.Supa import upload_to_bucket

router = APIRouter()

Templates = Jinja2Templates(directory="TemplatesHTML")

@router.get("/newSpider", response_class=HTMLResponse)
async def show_create(request: Request, universe_id: int):
    return Templates.TemplateResponse("new_spiderMan.html", {"request": request, "universe_id": universe_id})

#CREAR SPIDER-MAN
@router.post("/", response_model=SpiderMan, status_code=201)
async def create_SpiderMan(request:Request,
                           session: SessionDep,
                           name: str = Form(..., alias="name"),
                           alias:str = Form(..., alias="alias"),
                           skills:str = Form(..., alias="skills"),
                           alive_str:str = Form(..., alias="alive"),
                           universe_id: int = Form(..., alias="universe_id"),
                           img: Optional[UploadFile] = File(None)
                            ):

    print(f"Received data: name={name}, alias={alias}, universe_id={universe_id}, alive={alive_str}")
    
    is_alive = str(alive_str).lower() == "true"
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
            # If upload fails (e.g. duplicate or other error), we log it but don't stop the DB save.
            pass
            
    try:
        new_spider = spiderManCreate(name=name, alias=alias,skills=skills, alive=is_alive, img=img_url, universe_id=universe_id)
        print(f"Creating SpiderMan object: {new_spider}")

        spiderMan = SpiderMan.model_validate(new_spider)
        session.add(spiderMan)
        await session.commit()
        await session.refresh(spiderMan)
        print(f"SpiderMan saved with ID: {spiderMan.id}")
    except Exception as e:
        print(f"Error DB: {e}")
        raise HTTPException(status_code=400, detail=f"Error al guardar datos: {str(e)}")
    return RedirectResponse(url=f"/SpiderMans/{spiderMan.id}", status_code=302)


#BUSCAR UN SPIDERMAN POR ID
@router.get("/{spiderMan_id}", response_class=HTMLResponse)
async def get_one_SpiderMan(request: Request, spiderMan_id: int, session: SessionDep):
    spiderMan_db = await session.get(SpiderMan, spiderMan_id)
    if not spiderMan_db:
        raise HTTPException(status_code=404, detail= "SpiderMan not found")
    # Load the Universe and Peliculas relationships
    await session.refresh(spiderMan_db, ["Universe", "peliculas"])
    return Templates.TemplateResponse("spiderMan.html", {
        "request": request, 
        "SpiderMan": spiderMan_db, 
        "universe": spiderMan_db.Universe,
        "peliculas": spiderMan_db.peliculas
    })


#FORMULARIO PARA EDITAR SPIDERMAN
@router.get("/{spiderMan_id}/edit", response_class=HTMLResponse)
async def edit_spiderMan_form(request: Request, spiderMan_id: int, session: SessionDep):
    spiderMan_db = await session.get(SpiderMan, spiderMan_id)
    if not spiderMan_db:
        raise HTTPException(status_code=404, detail="SpiderMan not found")
    return Templates.TemplateResponse("edit_spiderMan.html", {"request": request, "SpiderMan": spiderMan_db, "universe_id": spiderMan_db.universe_id})

#ACTULIZAR INFORMACIÓN DEL SPIDERMAN
@router.post("/{spiderMan_id}/update", response_class=HTMLResponse)
async def update_spiderMan(
    request: Request,
    spiderMan_id: int,
    session: SessionDep,
    name: str = Form(..., alias="name"),
    alias: str = Form(..., alias="alias"),
    skills: str = Form(..., alias="skills"),
    alive_str: str = Form(..., alias="alive"),
    img: Optional[UploadFile] = File(None)
):
    spiderMan_db = await session.get(SpiderMan, spiderMan_id)
    if not spiderMan_db:
        raise HTTPException(status_code=404, detail="SpiderMan not found")

    is_alive = str(alive_str).lower() == "true"
    
    spiderMan_db.name = name
    spiderMan_db.alias = alias
    spiderMan_db.skills = skills
    spiderMan_db.alive = is_alive

    if img and img.filename:
        try:
            img_url = await upload_to_bucket(img)
            spiderMan_db.img = img_url
        except Exception as e:
            print(f"Error uploading image: {e}")
            # Continue updating other fields even if image upload fails

    session.add(spiderMan_db)
    await session.commit()
    await session.refresh(spiderMan_db)
    
    return RedirectResponse(url=f"/SpiderMans/{spiderMan_db.id}", status_code=302)

@router.post("/{spiderMan_id}/delete", response_class=HTMLResponse)
async def kill_one_spiderMan(spiderMan_id:int, session: SessionDep):
    spiderMan_db = await session.get(SpiderMan, spiderMan_id)
    if not spiderMan_db:
        raise HTTPException(status_code = 404, detail="SpiderMan not found")

    spiderMan_db.status = False 
    
    session.add(spiderMan_db)
    await session.commit()
    await session.refresh(spiderMan_db)
    
    return RedirectResponse(url=f"/universes/{spiderMan_db.universe_id}", status_code=302)

#BUSCAR TODOS LOS SPIDERMANS
@router.get("/", response_class=HTMLResponse)
async def get_all_SpiderMan(request: Request, session: SessionDep):
    result = await session.execute(select(SpiderMan).where(SpiderMan.status == True))
    spiderMans = result.scalars().all()
    for sm in spiderMans:
        print(f"SpiderMan: {sm.name}, Img: {sm.img}")
    return Templates.TemplateResponse("spiderMan_list.html", {"request": request, "spiderMans": spiderMans})