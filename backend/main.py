from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

app = FastAPI()

# CORS – permitir chamadas do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-mu-eight-30.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Modelos ----------
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    farm_name: str
    owner_name: str

class AnimalCreate(BaseModel):
    tag_id: str
    name: str
    breed: str
    status: str

class MilkRecord(BaseModel):
    animal_id: str
    date: str
    morning: float = 0
    afternoon: float = 0
    evening: float = 0

# Modelos para finanças
class FinanceCategory(BaseModel):
    name: str
    type: str  # 'revenue' ou 'expense'

class FinanceTransaction(BaseModel):
    category_id: str
    description: str
    amount: float
    transaction_date: str
    is_paid: bool = True

# ---------- Dados em memória (mock) ----------
animals_db = [
    {"id": "1", "tag_id": "001", "name": "Mimosa", "breed": "Girolando", "status": "lactation"},
    {"id": "2", "tag_id": "002", "name": "Estrela", "breed": "Holandês", "status": "dry"},
]

# Dados mockados para finanças
categories_db = [
    {"id": "1", "name": "Venda de Leite", "type": "revenue"},
    {"id": "2", "name": "Ração", "type": "expense"},
    {"id": "3", "name": "Medicamentos", "type": "expense"},
    {"id": "4", "name": "Energia", "type": "expense"},
]

transactions_db = [
    {
        "id": "1",
        "category_id": "1",
        "description": "Venda de leite da semana",
        "amount": 1500.00,
        "transaction_date": "2026-03-22",
        "is_paid": True,
    },
    {
        "id": "2",
        "category_id": "2",
        "description": "Ração concentrada",
        "amount": 800.00,
        "transaction_date": "2026-03-21",
        "is_paid": True,
    },
]

# ---------- Rotas de Autenticação ----------
@app.post("/auth/login")
async def login(login_data: LoginRequest):
    return {
        "access_token": "mock-jwt-token",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": login_data.email,
            "farm_name": "Fazenda Teste",
            "owner_name": "Usuário Teste"
        }
    }

@app.post("/auth/register")
async def register(register_data: RegisterRequest):
    return {
        "id": 2,
        "email": register_data.email,
        "farm_name": register_data.farm_name,
        "owner_name": register_data.owner_name
    }

@app.get("/auth/me")
async def get_me():
    return {
        "id": 1,
        "email": "usuario@teste.com",
        "farm_name": "Fazenda Teste",
        "owner_name": "Usuário Teste"
    }

# ---------- Rotas de Animais (CRUD) ----------
@app.get("/")
def root():
    return {"message": "API do Milk SaaS"}

@app.get("/animals/")
def get_animals():
    return animals_db

@app.post("/animals/")
def create_animal(animal: AnimalCreate):
    new_id = str(len(animals_db) + 1)
    new_animal = {"id": new_id, **animal.dict()}
    animals_db.append(new_animal)
    return new_animal

@app.put("/animals/{animal_id}")
def update_animal(animal_id: str, animal: AnimalCreate):
    for idx, a in enumerate(animals_db):
        if a["id"] == animal_id:
            updated = {"id": animal_id, **animal.dict()}
            animals_db[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail="Animal não encontrado")

@app.delete("/animals/{animal_id}")
def delete_animal(animal_id: str):
    for idx, a in enumerate(animals_db):
        if a["id"] == animal_id:
            del animals_db[idx]
            return {"message": f"Animal {animal_id} removido"}
    raise HTTPException(status_code=404, detail="Animal não encontrado")

# ---------- Rotas de Produção de Leite ----------
@app.get("/milk/dashboard")
async def milk_dashboard():
    return {
        "total_today": 125.5,
        "total_week": 845.2,
        "total_month": 3450.0,
        "average_per_animal": 12.5,
        "last_records": [
            {"date": "2026-03-22", "animal": "001", "amount": 15.2},
            {"date": "2026-03-21", "animal": "002", "amount": 14.8},
            {"date": "2026-03-20", "animal": "001", "amount": 16.0},
        ]
    }

@app.get("/milk/")
async def list_milk():
    return [
        {"id": 1, "animal_id": "1", "date": "2026-03-22", "morning": 5.2, "afternoon": 4.5, "evening": 3.8},
        {"id": 2, "animal_id": "2", "date": "2026-03-22", "morning": 6.0, "afternoon": 5.5, "evening": 4.2},
    ]

@app.post("/milk/")
async def create_milk(record: MilkRecord):
    return {"id": 3, **record.dict()}

@app.put("/milk/{record_id}")
async def update_milk(record_id: int, record: MilkRecord):
    return {"id": record_id, **record.dict()}

@app.delete("/milk/{record_id}")
async def delete_milk(record_id: int):
    return {"message": f"Registro {record_id} excluído"}

# ---------- Rotas de Finanças (mock) ----------
@app.get("/finance/categories")
def get_categories():
    return categories_db

@app.post("/finance/categories")
def create_category(cat: FinanceCategory):
    new_id = str(len(categories_db) + 1)
    new_cat = {"id": new_id, **cat.dict()}
    categories_db.append(new_cat)
    return new_cat

@app.get("/finance/transactions")
def get_transactions(start_date: Optional[str] = None, end_date: Optional[str] = None, type: Optional[str] = None):
    result = transactions_db
    if start_date:
        result = [t for t in result if t["transaction_date"] >= start_date]
    if end_date:
        result = [t for t in result if t["transaction_date"] <= end_date]
    if type:
        cat_ids = [c["id"] for c in categories_db if c["type"] == type]
        result = [t for t in result if t["category_id"] in cat_ids]
    # Enriquecer com a categoria completa
    enriched = []
    for t in result:
        cat = next((c for c in categories_db if c["id"] == t["category_id"]), None)
        enriched.append({**t, "category": cat})
    return enriched

@app.post("/finance/transactions")
def create_transaction(trans: FinanceTransaction):
    new_id = str(len(transactions_db) + 1)
    new_trans = {"id": new_id, **trans.dict()}
    transactions_db.append(new_trans)
    cat = next((c for c in categories_db if c["id"] == new_trans["category_id"]), None)
    return {**new_trans, "category": cat}

@app.put("/finance/transactions/{transaction_id}")
def update_transaction(transaction_id: str, trans: FinanceTransaction):
    for idx, t in enumerate(transactions_db):
        if t["id"] == transaction_id:
            updated = {"id": transaction_id, **trans.dict()}
            transactions_db[idx] = updated
            cat = next((c for c in categories_db if c["id"] == updated["category_id"]), None)
            return {**updated, "category": cat}
    raise HTTPException(status_code=404, detail="Transação não encontrada")

@app.delete("/finance/transactions/{transaction_id}")
def delete_transaction(transaction_id: str):
    for idx, t in enumerate(transactions_db):
        if t["id"] == transaction_id:
            del transactions_db[idx]
            return {"message": f"Transação {transaction_id} removida"}
    raise HTTPException(status_code=404, detail="Transação não encontrada")

@app.get("/finance/summary")
def get_summary(year: int, month: int):
    filtered = [
        t for t in transactions_db
        if t["transaction_date"].startswith(f"{year}-{month:02d}")
    ]
    revenues = 0.0
    expenses = 0.0
    for t in filtered:
        cat = next((c for c in categories_db if c["id"] == t["category_id"]), None)
        if cat and cat["type"] == "revenue":
            revenues += t["amount"]
        else:
            expenses += t["amount"]
    return {
        "revenues": revenues,
        "expenses": expenses,
        "balance": revenues - expenses,
    }