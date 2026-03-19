import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Farm(Base):
    __tablename__ = "farms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_name = Column(String, nullable=False)
    farm_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    animals = relationship("Animal", back_populates="farm", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="farm", cascade="all, delete-orphan")
    categories = relationship("FinancialCategory", back_populates="farm", cascade="all, delete-orphan")


class Animal(Base):
    __tablename__ = "animals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(String, nullable=False)
    name = Column(String)
    breed = Column(String)
    birth_date = Column(Date)
    status = Column(String, nullable=False)  # 'lactation', 'dry', 'heifer', 'calf'
    last_calving_date = Column(Date)

    __table_args__ = (
        CheckConstraint(status.in_(['lactation', 'dry', 'heifer', 'calf']), name='check_animal_status'),
        UniqueConstraint('farm_id', 'tag_id', name='uq_farm_animal_tag')
    )

    farm = relationship("Farm", back_populates="animals")
    milk_productions = relationship("MilkProduction", back_populates="animal", cascade="all, delete-orphan")


class MilkProduction(Base):
    __tablename__ = "milk_productions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    animal_id = Column(UUID(as_uuid=True), ForeignKey("animals.id", ondelete="CASCADE"), nullable=False)
    production_date = Column(Date, nullable=False, server_default=func.current_date())
    liters_produced = Column(Numeric(10, 2), nullable=False)
    period = Column(String)  # 'morning', 'afternoon', 'night'
    fat_content = Column(Numeric(5, 2), default=0)
    protein_content = Column(Numeric(5, 2), default=0)

    __table_args__ = (
        CheckConstraint(period.in_(['morning', 'afternoon', 'night']), name='check_period'),
    )

    animal = relationship("Animal", back_populates="milk_productions")


class FinancialCategory(Base):
    __tablename__ = "financial_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'variable_cost', 'fixed_cost', 'revenue'

    __table_args__ = (
        CheckConstraint(type.in_(['variable_cost', 'fixed_cost', 'revenue']), name='check_category_type'),
    )

    farm = relationship("Farm", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("financial_categories.id", ondelete="RESTRICT"), nullable=False)
    description = Column(String)
    amount = Column(Numeric(12, 2), nullable=False)
    transaction_date = Column(Date, nullable=False, server_default=func.current_date())
    is_paid = Column(Boolean, default=True)

    farm = relationship("Farm", back_populates="transactions")
    category = relationship("FinancialCategory", back_populates="transactions")