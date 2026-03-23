from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

app = FastAPI()

# CORS - CORRIGIDO e LIBERADO
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://frontend-mu-eight-30.vercel.app"
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
    liters_produced: Optional[float] = 0

class FinanceCategory(BaseModel):
    name: str
    type: str

class FinanceTransaction(BaseModel):
    category_id: str
    description: str
    amount: float
    transaction_date: str
    is_paid: bool = True

# ---------- Dados em memoria ----------
animals_db = [
    {"id": "1", "tag_id": "001", "name": "Mimosa", "breed": "Girolando", "status": "lactation"},
    {"id": "2", "tag_id": "002", "name": "Estrela", "breed": "Holandes", "status": "dry"},
]

milk_db = [
    {
        "id": 1,
        "animal_id": "1",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "morning": 5.2,
        "afternoon": 4.5,
        "evening": 3.8,
        "liters_produced": 13.5
    },
    {
        "id": 2,
        "animal_id": "2",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "morning": 6.0,
        "afternoon": 5.5,
        "evening": 4.2,
        "liters_produced": 15.7
    },
]

categories_db = [
    {"id": "1", "name": "Venda de Leite", "type": "revenue"},
    {"id": "2", "name": "Racao", "type": "expense"},
    {"id": "3", "name": "Medicamentos", "type": "expense"},
    {"id": "4", "name": "Energia", "type": "expense"},
]

transactions_db = [
    {
        "id": "1",
        "category_id": "1",
        "description": "Venda de leite da semana",
        "amount": 1500.00,
        "transaction_date": datetime.now().strftime("%Y-%m-%d"),
        "is_paid": True,
    },
    {
        "id": "2",
        "category_id": "2",
        "description": "Racao concentrada",
        "amount": 800.00,
        "transaction_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "is_paid": True,
    },
]

# ---------- Rotas de Autenticacao ----------
@app.post("/auth/login")
async def login(login_data: LoginRequest):
    return {
        "access_token": "mock-jwt-token",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": login_data.email,
            "farm_name": "Fazenda Teste",
            "owner_name": "Usuario Teste"
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
        "owner_name": "Usuario Teste"
    }

@app.post("/auth/logout")
async def logout():
    return {"message": "Logout realizado com sucesso"}

# ---------- Rotas de Animais ----------
@app.get("/")
def root():
    return {"message": "API do Milk SaaS"}

@app.get("/animals/")
def get_animals():
    return animals_db

@app.post("/animals/")
def create_animal(animal: AnimalCreate):
    new_id = str(len(animals_db) + 1)
    new_animal = {"id": new_id, **animal.model_dump()}
    animals_db.append(new_animal)
    return new_animal

@app.put("/animals/{animal_id}")
def update_animal(animal_id: str, animal: AnimalCreate):
    for idx, a in enumerate(animals_db):
        if a["id"] == animal_id:
            updated = {"id": animal_id, **animal.model_dump()}
            animals_db[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail="Animal nao encontrado")

@app.delete("/animals/{animal_id}")
def delete_animal(animal_id: str):
    for idx, a in enumerate(animals_db):
        if a["id"] == animal_id:
            del animals_db[idx]
            return {"message": f"Animal {animal_id} removido"}
    raise HTTPException(status_code=404, detail="Animal nao encontrado")

# ---------- Rotas de Producao de Leite ----------
@app.get("/milk/")
async def list_milk(animal_id: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
    result = milk_db
    if animal_id:
        result = [r for r in result if str(r["animal_id"]) == str(animal_id)]
    if start_date:
        result = [r for r in result if r["date"] >= start_date]
    if end_date:
        result = [r for r in result if r["date"] <= end_date]
    return result

@app.post("/milk/")
async def create_milk(record: MilkRecord):
    new_id = max([r["id"] for r in milk_db], default=0) + 1
    new_record = {"id": new_id, **record.model_dump()}
    
    if "liters_produced" not in new_record or not new_record["liters_produced"]:
         new_record["liters_produced"] = new_record["morning"] + new_record["afternoon"] + new_record["evening"]
         
    milk_db.append(new_record)
    return new_record

@app.put("/milk/{record_id}")
async def update_milk(record_id: int, record: MilkRecord):
    for idx, r in enumerate(milk_db):
        if r["id"] == record_id:
            updated = {"id": record_id, **record.model_dump()}
            updated["liters_produced"] = updated["morning"] + updated["afternoon"] + updated["evening"]
            milk_db[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail="Registro nao encontrado")

@app.delete("/milk/{record_id}")
async def delete_milk(record_id: int):
    for idx, r in enumerate(milk_db):
        if r["id"] == record_id:
            del milk_db[idx]
            return {"message": f"Registro {record_id} excluido"}
    raise HTTPException(status_code=404, detail="Registro nao encontrado")

@app.get("/milk/dashboard")
async def milk_dashboard():
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_start = today.replace(day=1)

    total_today = 0.0
    total_week = 0.0
    total_month = 0.0
    per_day = defaultdict(float)
    per_animal = defaultdict(float)

    for record in milk_db:
        record_date = datetime.strptime(record["date"], "%Y-%m-%d").date()
        total_liters = record.get("liters_produced", record["morning"] + record["afternoon"] + record["evening"])

        if record_date == today:
            total_today += total_liters
        if record_date >= week_ago:
            total_week += total_liters
        if record_date >= month_start:
            total_month += total_liters
            per_animal[record["animal_id"]] += total_liters

        per_day[record["date"]] += total_liters

    # Ultimos 7 dias
    last_7_days = []
    for i in range(7):
        d = today - timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        amount = per_day.get(d_str, 0)
        last_7_days.append({"date": d_str, "animal": "total", "amount": amount})
    last_7_days.reverse()

    # Top 5 animais do mes
    top_animals = sorted(
        [{"id": k, "name": f"Animal {k}", "total": v} for k, v in per_animal.items()],
        key=lambda x: x["total"],
        reverse=True,
    )[:5]

    avg_per_animal = total_month / len(per_animal) if per_animal else 0

    # NOVO: Conta total de animais e animais em lactação
    total_animais = len(animals_db)
    animais_lactacao = sum(1 for a in animals_db if a.get("status") == "lactation")

    return {
        "total_animals": total_animais,
        "lactating_animals": animais_lactacao,
        "total_today": total_today,
        "total_week": total_week,
        "total_month": total_month,
        "average_per_animal": avg_per_animal,
        "last_records": last_7_days,
        "top_animals": top_animals,
    }

# ---------- Rotas de Financas ----------
@app.get("/finance/categories")
def get_categories():
    return categories_db

@app.post("/finance/categories")
def create_category(cat: FinanceCategory):
    new_id = str(len(categories_db) + 1)
    new_cat = {"id": new_id, **cat.model_dump()}
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
    enriched = []
    for t in result:
        cat = next((c for c in categories_db if c["id"] == t["category_id"]), None)
        enriched.append({**t, "category": cat})
    return enriched

@app.post("/finance/transactions")
def create_transaction(trans: FinanceTransaction):
    new_id = str(len(transactions_db) + 1)
    new_trans = {"id": new_id, **trans.model_dump()}
    transactions_db.append(new_trans)
    cat = next((c for c in categories_db if c["id"] == new_trans["category_id"]), None)
    return {**new_trans, "category": cat}

@app.put("/finance/transactions/{transaction_id}")
def update_transaction(transaction_id: str, trans: FinanceTransaction):
    for idx, t in enumerate(transactions_db):
        if t["id"] == transaction_id:
            updated = {"id": transaction_id, **trans.model_dump()}
            transactions_db[idx] = updated
            cat = next((c for c in categories_db if c["id"] == updated["category_id"]), None)
            return {**updated, "category": cat}
    raise HTTPException(status_code=404, detail="Transacao nao encontrada")

@app.delete("/finance/transactions/{transaction_id}")
def delete_transaction(transaction_id: str):
    for idx, t in enumerate(transactions_db):
        if t["id"] == transaction_id:
            del transactions_db[idx]
            return {"message": f"Transacao {transaction_id} removida"}
    raise HTTPException(status_code=404, detail="Transacao nao encontrada")

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

# ---------- Rotas de Relatorio ----------
@app.get("/milk/report")
async def milk_report(start_date: str, end_date: str):
    pdf_falso = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    return Response(content=pdf_falso, media_type="application/pdf")

@app.get("/finance/report")
async def finance_report(start_date: str, end_date: str):
    pdf_falso = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    return Response(content=pdf_falso, media_type="application/pdf")