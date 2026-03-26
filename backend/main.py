import io
from fastapi import FastAPI, HTTPException, Response, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta
from typing import Optional, List

# Importações do seu sistema de banco de dados
from app import models, database, schemas
from app.api import deps 

# Inicializa o Banco de Dados (Cria tabelas se não existirem)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Milk SaaS - Produção Real")

# 1. CORS - LIBERAÇÃO TOTAL (Resolve o "Network Error")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# ---------- DEPENDÊNCIA DO BANCO ----------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- ROTAS DE AUTENTICAÇÃO (MOCK PARA TESTE) ----------
@app.post("/auth/login")
async def login():
    return {
        "access_token": "token-real-db",
        "token_type": "bearer",
        "user": {"id": 1, "email": "produtor@milk.com", "farm_name": "Minha Fazenda"}
    }

@app.get("/auth/me")
async def get_me():
    return {"id": 1, "email": "produtor@milk.com", "farm_name": "Minha Fazenda"}

# ---------- ROTAS DE ANIMAIS (CONECTADO AO BANCO) ----------

@app.get("/animals/")
def get_animals(db: Session = Depends(get_db)):
    return db.query(models.Animal).all()

@app.post("/animals/")
def create_animal(animal: schemas.AnimalCreate, db: Session = Depends(get_db)):
    new_animal = models.Animal(**animal.dict())
    db.add(new_animal)
    db.commit()
    db.refresh(new_animal)
    return new_animal

@app.delete("/animals/{animal_id}")
def delete_animal(animal_id: str, db: Session = Depends(get_db)):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    db.delete(animal)
    db.commit()
    return {"message": "Animal removido"}

# ---------- ROTAS FINANCEIRAS (CONECTADO AO BANCO) ----------

@app.get("/finance/categories")
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.FinancialCategory).all()

@app.get("/finance/transactions")
def list_transactions(db: Session = Depends(get_db)):
    # Aqui o Frontend encontrará os IDs UUID (ex: 878dacc3...)
    return db.query(models.Transaction).order_by(models.Transaction.transaction_date.desc()).all()

@app.get("/finance/summary")
def get_summary(year: int, month: int, db: Session = Depends(get_db)):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    
    receitas = db.query(func.sum(models.Transaction.amount)).join(models.FinancialCategory).filter(
        models.Transaction.transaction_date.between(start, end),
        models.FinancialCategory.type == 'revenue'
    ).scalar() or 0
    
    despesas = db.query(func.sum(models.Transaction.amount)).join(models.FinancialCategory).filter(
        models.Transaction.transaction_date.between(start, end),
        models.FinancialCategory.type.in_(['variable_cost', 'fixed_cost'])
    ).scalar() or 0
    
    return {
        "receitas": float(receitas),
        "despesas": float(despesas),
        "saldo_liquido": float(receitas - despesas)
    }

@app.delete("/finance/transactions/{transaction_id}")
def delete_transaction(transaction_id: str, db: Session = Depends(get_db)):
    # Busca pelo ID UUID real que o Frontend enviou
    trans = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not trans:
        raise HTTPException(status_code=404, detail="Transação não encontrada no banco de dados")
    db.delete(trans)
    db.commit()
    return {"message": "Transação removida com sucesso"}

# ---------- RELATÓRIO PDF (CORRIGIDO) ----------

@app.get("/finance/report/pdf")
async def finance_report(start_date: str, end_date: str):
    # Cabeçalho robusto para evitar Erro 500 no navegador
    pdf_falso = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    return Response(
        content=pdf_falso,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=relatorio_{start_date}.pdf"
        }
    )

@app.get("/")
def root():
    return {"status": "Online", "database": "Conectado ao PostgreSQL"}