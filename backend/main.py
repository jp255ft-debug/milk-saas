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
            "name": "Usuário Teste"
        }
    }

# Rota de registro (mock)
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

@app.post("/auth/register")
async def register(register_data: RegisterRequest):
    # Aceita qualquer cadastro para teste
    return {
        "id": 2,
        "email": register_data.email,
        "name": register_data.name
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