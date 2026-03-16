from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ---------- FinancialCategory ----------
class FinancialCategoryBase(BaseModel):
    name: str
    type: str = Field(..., pattern='^(variable_cost|fixed_cost|revenue)$')

class FinancialCategoryCreate(FinancialCategoryBase):
    pass

class FinancialCategoryResponse(FinancialCategoryBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

# ---------- Transaction ----------
class TransactionBase(BaseModel):
    category_id: UUID
    description: str | None = None
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    transaction_date: date = Field(default_factory=date.today)
    is_paid: bool = True

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    category_id: UUID | None = None
    description: str | None = None
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    transaction_date: date | None = None
    is_paid: bool | None = None

class TransactionResponse(TransactionBase):
    id: UUID
    farm_id: UUID
    category: FinancialCategoryResponse | None = None  # para incluir nome da categoria

    model_config = ConfigDict(from_attributes=True)

# ---------- Cálculos ----------
class CostPerLiterResponse(BaseModel):
    period_start: date
    period_end: date
    total_expenses: float
    total_liters: float
    cost_per_liter: float
    details: dict
