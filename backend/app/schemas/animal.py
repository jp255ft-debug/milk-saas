from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AnimalBase(BaseModel):
    tag_id: str
    name: str | None = None
    breed: str | None = None
    birth_date: date | None = None
    status: str = Field(..., pattern='^(lactation|dry|heifer|calf)$')
    last_calving_date: date | None = None

class AnimalCreate(AnimalBase):
    pass

class AnimalUpdate(BaseModel):
    tag_id: str | None = None
    name: str | None = None
    breed: str | None = None
    birth_date: date | None = None
    status: str | None = Field(None, pattern='^(lactation|dry|heifer|calf)$')
    last_calving_date: date | None = None

class AnimalResponse(AnimalBase):
    id: UUID
    farm_id: UUID
    model_config = ConfigDict(from_attributes=True)
