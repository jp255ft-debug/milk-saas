from sqlalchemy import Column, String, Date, Numeric, Boolean, ForeignKey, CheckConstraint, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base
from sqlalchemy_utils import UUIDType

class Farm(Base):
    __tablename__ = "farms"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    owner_name = Column(String, nullable=False)
    farm_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    animals = relationship("Animal", back_populates="farm", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="farm", cascade="all, delete-orphan")

class Animal(Base):
    __tablename__ = "animals"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUIDType(binary=False), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(String, nullable=False)
    name = Column(String)
    breed = Column(String)
    birth_date = Column(Date)
    status = Column(String, nullable=False)  # lactation, dry, heifer, calf
    last_calving_date = Column(Date)

    __table_args__ = (
        CheckConstraint(status.in_(['lactation', 'dry', 'heifer', 'calf']), name='check_animal_status'),
        UniqueConstraint('farm_id', 'tag_id', name='uq_farm_animal_tag')
    )

    farm = relationship("Farm", back_populates="animals")
    milk_productions = relationship("MilkProduction", back_populates="animal", cascade="all, delete-orphan")

class MilkProduction(Base):
    __tablename__ = "milk_productions"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    animal_id = Column(UUIDType(binary=False), ForeignKey("animals.id", ondelete="CASCADE"), nullable=False)
    production_date = Column(Date, nullable=False, server_default=func.current_date())
    liters_produced = Column(Numeric(10, 2), nullable=False)
    period = Column(String)  # morning, afternoon, night
    fat_content = Column(Numeric(5, 2))
    protein_content = Column(Numeric(5, 2))

    animal = relationship("Animal", back_populates="milk_productions")

class FinancialCategory(Base):
    __tablename__ = "financial_categories"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # variable_cost, fixed_cost, revenue

    __table_args__ = (
        CheckConstraint(type.in_(['variable_cost', 'fixed_cost', 'revenue']), name='check_category_type'),
    )

    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUIDType(binary=False), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUIDType(binary=False), ForeignKey("financial_categories.id", ondelete="RESTRICT"), nullable=False)
    description = Column(String)
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_date = Column(Date, nullable=False, server_default=func.current_date())
    is_paid = Column(Boolean, nullable=False, default=True)

    farm = relationship("Farm", back_populates="transactions")
    category = relationship("FinancialCategory", back_populates="transactions")
