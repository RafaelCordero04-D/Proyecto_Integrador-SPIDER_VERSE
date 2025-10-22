from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship



class SpiderManPeliculaLink (SQLModel, table=True):
    pelicula_id: int =  Field(primary_key=True, foreign_key = "pelicula.id")
    spiderMan_id: int = Field(primary_key= True, foreign_key = "spiderman.id")
    quantity: int | None = Field(default = 1)


class universeBase(SQLModel):
    name:str | None= Field(description= "Universe name")
    description:str | None= Field(description= "Universe description")
    characters: str | None = Field(description = "Universe characters")

class universe(universeBase, table=True):
    id: int | None = Field(default = None, primary_key=True)
    spiderMans: list["SpiderMan"] = Relationship(back_populates="Universe")

class universeCreate(universeBase):
    pass

class universeUpdate(universeBase):
    pass



class spiderManBase(SQLModel):
    name: str | None = Field(description= "Spider name")
    alias: str | None = Field(description = "Spider alias" )
    skills: str | None = Field(description= "Spider skills")
    status : bool | None = Field(description = "Spider status", default = True)


class SpiderMan(spiderManBase, table=True):
    id: int | None = Field(default = None, primary_key=True)
    universe_id:int =Field(foreign_key = "universe.id")
    Universe: universe = Relationship(back_populates="spiderMans")

    peliculas: list["Pelicula"] = Relationship(back_populates = "spiderMans", link_model = SpiderManPeliculaLink)


class spiderManCreate(spiderManBase):
    universe_id:int = Field(foreign_key = "universe.id")

class spiderManUpdate(spiderManBase):
    pass



class peliculaBase(SQLModel):
    titulo: str | None = Field(description= "Pelicula titulo")
    año: int | None = Field(description= "Pelicula año")
    taquilla: float | None = Field(description = "Pelicula taquilla")
    director: str | None = Field(description = "Pelicula director")
    characters: str | None = Field(description = "Pelicula characters")

class Pelicula(peliculaBase, table=True):
    id: int | None = Field (primary_key=True, default = None)
    spiderMans: list["SpiderMan"] = Relationship(back_populates="peliculas", link_model=SpiderManPeliculaLink)

class peliculaCreate(peliculaBase):
    pass

class peliculaUpdate(peliculaBase):
    pass