from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict

app = FastAPI()

# 1. CORS - LIBERAÇÃO TOTAL PARA SEU FRONTEND
# Adicionei a URL oficial que aparece no seu navegador (milk-saas.vercel.app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://frontend-mu-eight-30.vercel.app",
        "https://milk-saas.vercel.app"  # URL DO SEU PRINT
    ],
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, PUT, DELETE, OPTIONS
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

# ---------- Dados em memória (Mock DB) ----------
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
    }
]

categories_db = [
    {"id": "1", "name": "Venda de Leite In Natura", "type": "revenue"},
    {"id": "2", "name": "Milho (Grão/Moído)", "type": "variable_cost"},
]

transactions_db = [
    {
        "id": "1",
        "category_id": "1",
        "description": "Venda do dia",
        "amount": 1500.00,
        "transaction_date": datetime.now().strftime("%Y-%m-%d"),
        "is_paid": True,
    },
    {
        "id": "2",
        "category_id": "2",
        "description": "Compra de ração",
        "amount": 85.00,
        "transaction_date": datetime.now().strftime("%Y-%m-%d"),
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
            "farm_name": "Fazenda Cedro",
            "owner_name": "Produtor"
        }
    }

@app.get("/auth/me")
async def get_me():
    return {
        "id": 1,
        "email": "usuario@teste.com",
        "farm_name": "Fazenda Cedro",
        "owner_name": "Produtor"
    }

# ---------- Rotas de Animais ----------
@app.get("/")
def root():
    return {"message": "API do Milk SaaS está rodando!"}

@app.get("/animals/")
def get_animals():
    return animals_db

@app.delete("/animals/{animal_id}")
def delete_animal(animal_id: str):
    for idx, a in enumerate(animals_db):
        if a["id"] == animal_id:
            del animals_db[idx]
            return {"message": f"Animal {animal_id} removido"}
    raise HTTPException(status_code=404, detail="Animal não encontrado")

# ---------- Rotas de Finanças ----------

@app.get("/finance/categories")
def get_categories():
    return categories_db

@app.get("/finance/transactions")
def get_transactions(start_date: Optional[str] = None, end_date: Optional[str] = None, type: Optional[str] = None):
    result = transactions_db
    if start_date:
        result = [t for t in result if t["transaction_date"] >= start_date]
    if end_date:
        result = [t for t in result if t["transaction_date"] <= end_date]
    
    enriched = []
    for t in result:
        cat = next((c for c in categories_db if c["id"] == t["category_id"]), None)
        enriched.append({**t, "category": cat})
    return enriched

@app.get("/finance/summary")
def get_summary(year: int, month: int):
    # Filtra transações do mês selecionado
    prefix = f"{year}-{month:02d}"
    filtered = [t for t in transactions_db if t["transaction_date"].startswith(prefix)]
    
    revenues = 0.0
    expenses = 0.0
    for t in filtered:
        cat = next((c for c in categories_db if c["id"] == t["category_id"]), None)
        # Considera 'revenue' como entrada, o resto como saída
        if cat and cat["type"] == "revenue":
            revenues += t["amount"]
        else:
            expenses += t["amount"]
            
    # AJUSTADO: Nomes das chaves para bater com o Frontend (Vercel)
    return {
        "receitas": revenues,
        "despesas": expenses,
        "saldo_liquido": revenues - expenses,
    }

@app.put("/finance/transactions/{transaction_id}")
def update_transaction(transaction_id: str, trans: FinanceTransaction):
    for idx, t in enumerate(transactions_db):
        if t["id"] == transaction_id:
            updated = {"id": transaction_id, **trans.model_dump()}
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

# ---------- Rotas de Relatório (PDF) ----------

# AJUSTADO: Rota agora é /report/pdf para coincidir com o Frontend
@app.get("/finance/report/pdf")
async def finance_report(start_date: str, end_date: str):
    # PDF Mock para teste de download
    pdf_falso = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    return Response(
        content=pdf_falso, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=relatorio_financeiro.pdf"}
    )