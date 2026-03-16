from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Farm (existente) ----------
class FarmBase(BaseModel):
    owner_name: str
    farm_name: str
    email: EmailStr

class FarmCreate(FarmBase):
    password: str = Field(..., min_length=6)

class FarmResponse(FarmBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ---------- Token ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    farm_id: str | None = None

# ---------- Animal ----------
class AnimalBase(BaseModel):
    tag_id: str
    name: str | None = None
    breed: str | None = None
    birth_date: date | None = None
    status: str = Field(..., pattern='^(lactation|dry|heifer|calf)$')
    last_calving_date: date | None = None

class AnimalCreate(AnimalBase):
    farm_id: UUID

class Animal(AnimalBase):
    id: UUID
    farm_id: UUID
    model_config = ConfigDict(from_attributes=True)

# ---------- MilkProduction ----------
class MilkProductionBase(BaseModel):
    production_date: date | None = Field(default_factory=date.today)
    liters_produced: Decimal = Field(..., gt=0, decimal_places=2)
    period: str | None = Field(None, pattern='^(morning|afternoon|night)$')
    fat_content: Decimal | None = Field(0, ge=0, le=100, decimal_places=2)
    protein_content: Decimal | None = Field(0, ge=0, le=100, decimal_places=2)

class MilkProductionCreate(MilkProductionBase):
    animal_id: UUID

class MilkProduction(MilkProductionBase):
    id: UUID
    animal_id: UUID
    model_config = ConfigDict(from_attributes=True)

# ---------- FinancialCategory ----------
class FinancialCategoryBase(BaseModel):
    name: str
    type: str = Field(..., pattern='^(variable_cost|fixed_cost|revenue)$')

class FinancialCategoryCreate(FinancialCategoryBase):
    pass

class FinancialCategory(FinancialCategoryBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

# ---------- Transaction ----------
class TransactionBase(BaseModel):
    description: str | None = None
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    transaction_date: date | None = Field(default_factory=date.today)
    is_paid: bool = True

class TransactionCreate(TransactionBase):
    farm_id: UUID
    category_id: UUID

class Transaction(TransactionBase):
    id: UUID
    farm_id: UUID
    category_id: UUID
    model_config = ConfigDict(from_attributes=True)