from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship


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


class spiderManCreate(spiderManBase):
    universe_id:int = Field(foreign_key = "universe.id")

class spiderManUpdate(spiderManBase):
    pass
