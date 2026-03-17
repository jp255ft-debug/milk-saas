from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MilkProductionBase(BaseModel):
    animal_id: UUID
    production_date: date = Field(default_factory=date.today)
    liters_produced: Decimal = Field(..., gt=0)
    period: str | None = Field(None, pattern='^(morning|afternoon|night)$')
    fat_content: Decimal | None = Field(0, ge=0, le=100)
    protein_content: Decimal | None = Field(0, ge=0, le=100)

class MilkProductionCreate(MilkProductionBase):
    pass

class MilkProductionUpdate(BaseModel):
    animal_id: UUID | None = None
    production_date: date | None = None
    liters_produced: Decimal | None = Field(None, gt=0)
    period: str | None = Field(None, pattern='^(morning|afternoon|night)$')
    fat_content: Decimal | None = Field(None, ge=0, le=100)
    protein_content: Decimal | None = Field(None, ge=0, le=100)

class MilkProductionResponse(MilkProductionBase):
    id: UUID
    animal_id: UUID

    model_config = ConfigDict(from_attributes=True)
