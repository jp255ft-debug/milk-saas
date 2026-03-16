from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import auth
from app.api.routers import animals, finance, milk
from app.database import Base, engine

app = FastAPI(title="Milk SaaS API")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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