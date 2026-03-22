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

class MilkRecord(BaseModel):
    animal_id: str
    date: str
    morning: float = 0
    afternoon: float = 0
    evening: float = 0

# ---------- Rotas de Autenticação ----------
@app.post("/auth/login")
async def login(login_data: LoginRequest):
    # Aceita qualquer email/senha para teste
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
    # Aceita qualquer cadastro para teste
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

# ---------- Rotas de Animais ----------
@app.get("/")
def root():
    return {"message": "API do Milk SaaS"}

@app.get("/animals/")
def get_animals():
    return [
        {"id": "1", "tag_id": "001", "name": "Mimosa", "breed": "Girolando", "status": "lactation"},
        {"id": "2", "tag_id": "002", "name": "Estrela", "breed": "Holandês", "status": "dry"},
    ]

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