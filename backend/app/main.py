import os
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Imports do seu sistema
from app.database import engine, Base
from app.api.endpoints import auth
from app.api.routers import animals, milk, finance

app = FastAPI(title="Milk SaaS API")

# 1. CRIAÇÃO AUTOMÁTICA DE TABELAS
@app.on_event("startup")
def startup():
    print("Conectando ao banco de dados e criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

# 2. HANDLER GLOBAL DE EXCEÇÕES (Para Auditoria)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = {
        "error": str(exc),
        "traceback": traceback.format_exc()
    }
    print("ERRO DETECTADO:", error_detail)
    return JSONResponse(
        status_code=500,
        content=error_detail
    )

# 3. CONFIGURAÇÃO DE CORS (CORRIGIDA PARA PERMITIR COOKIES)
origins = [
    "https://milk-saas.vercel.app",                                         # produção
    "https://milk-saas-git-main-joao-paulo-limas-projects.vercel.app",    # preview (se houver)
    "http://localhost:3000",                                                # desenvolvimento local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # lista específica (não "*")
    allow_credentials=True,         # necessário para cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. INCLUSÃO DAS ROTAS
app.include_router(auth.router, prefix="/auth", tags=["autenticação"])
app.include_router(animals.router, prefix="/animals", tags=["animais"])
app.include_router(milk.router, prefix="/milk", tags=["produção de leite"])
app.include_router(finance.router, prefix="/finance", tags=["financeiro"])

@app.get("/")
def root():
    return {"status": "online", "message": "API do Milk SaaS funcionando!"}