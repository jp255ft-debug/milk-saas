from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

# Modelo para requisição de login
class LoginRequest(BaseModel):
    email: str
    password: str

# Rota de login (mock)
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

# Modelo para requisição de registro
class RegisterRequest(BaseModel):
    email: str
    password: str
    farm_name: str
    owner_name: str

# Rota de registro (mock)
@app.post("/auth/register")
async def register(register_data: RegisterRequest):
    # Aceita qualquer cadastro para teste
    return {
        "id": 2,
        "email": register_data.email,
        "farm_name": register_data.farm_name,
        "owner_name": register_data.owner_name
    }

# Rota para obter dados do usuário autenticado (mock)
@app.get("/auth/me")
async def get_me():
    # Retorna um usuário mockado com os campos esperados pelo frontend
    return {
        "id": 1,
        "email": "usuario@teste.com",
        "farm_name": "Fazenda Teste",
        "owner_name": "Usuário Teste"
    }

# Suas rotas existentes
@app.get("/")
def root():
    return {"message": "API do Milk SaaS"}

@app.get("/animals/")
def get_animals():
    return [
        {"id": "1", "tag_id": "001", "name": "Mimosa", "breed": "Girolando", "status": "lactation"},
        {"id": "2", "tag_id": "002", "name": "Estrela", "breed": "Holandês", "status": "dry"},
    ]