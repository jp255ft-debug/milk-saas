from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api.endpoints import auth
from app.api.routers import animals, milk, finance
from app.api import deps
import os

app = FastAPI(title="Milk SaaS API")

# Configuração CORS
origins = [
    "http://localhost:3000",
    "https://frontend-72o2zf32t-joao-paulo-limas-projects.vercel.app",
    "https://frontend-sandy-six-24.vercel.app",
    "https://frontend-mu-eight-30.vercel.app",
    "https://frontend-chy9q7t0u-joao-paulo-limas-projects.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir roteadores
app.include_router(auth.router, prefix="/auth", tags=["autenticação"])
app.include_router(animals.router, prefix="/animals", tags=["animais"])
app.include_router(milk.router, prefix="/milk", tags=["produção de leite"])
app.include_router(finance.router, prefix="/finance", tags=["financeiro"])

@app.get("/")
def root():
    return {"message": "API do Milk SaaS funcionando!"}

# Cria as tabelas no banco (apenas para desenvolvimento)
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)