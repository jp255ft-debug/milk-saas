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
# Isso garante que o banco de dados seja estruturado assim que a API ligar
@app.on_event("startup")
def startup():
    print("Conectando ao banco de dados e criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

# 2. HANDLER GLOBAL DE EXCEÇÕES
# Se algo der errado (Erro 500), ele vai te mostrar o motivo real no navegador
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

# 3. CONFIGURAÇÃO DE CORS (SEGURANÇA)
# Puxa a URL do frontend da variável de ambiente ou usa o padrão local
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

origins = [
    "http://localhost:3000",
    frontend_url,
    # Aqui usamos um "hack" para aceitar qualquer subdomínio do seu Vercel
    "https://frontend-sandy-six-24.vercel.app", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Troque por 'origins' se quiser restrição total, '*' libera para testes
    allow_credentials=True,
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
    return {
        "status": "online",
        "message": "API do Milk SaaS funcionando!",
        "database": "conectado"
    }