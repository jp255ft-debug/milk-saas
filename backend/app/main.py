import os
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.api.endpoints import auth
from app.api.routers import animals, milk, finance

app = FastAPI(title="Milk SaaS API")

# Handler global de exceções (para debug)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = {
        "error": str(exc),
        "traceback": traceback.format_exc()
    }
    print("ERRO GLOBAL:", error_detail)
    return JSONResponse(
        status_code=500,
        content=error_detail
    )

# AJUSTE: Permite puxar a URL do frontend por variável de ambiente
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Configuração CORS
origins = [
    "http://localhost:3000",
    frontend_url,
    "https://frontend-72o2zf32t-joao-paulo-limas-projects.vercel.app",
    "https://frontend-sandy-six-24.vercel.app",
    "https://frontend-mu-eight-30.vercel.app",
    "https://frontend-chy9q7t0u-joao-paulo-limas-projects.vercel.app",
    "https://frontend-l6mksi77k-joao-paulo-limas-projects.vercel.app",
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