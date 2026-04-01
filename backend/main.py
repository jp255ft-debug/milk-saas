import io
from fastapi import FastAPI, HTTPException, Response, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta
from typing import Optional, List

from app import models, database, schemas
from app.api import deps 

# Cria tabelas se não existirem
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Milk SaaS - Produção Real")

# 1. CORS - Configuração Específica para Produção (Resolve o erro de Wildcard)
# Adicionei sua URL da Vercel e o localhost para testes
origins = [
    "https://milk-saas.vercel.app",
    "https://milk-saas-emvf0mekk-joao-paulo-limas-projects.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Necessário para enviar/receber cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# Dependência do Banco
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- ROTAS DE FINANÇAS ----------

@app.get("/finance/categories")
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.FinancialCategory).all()

@app.get("/finance/transactions")
def list_transactions(db: Session = Depends(get_db)):
    return db.query(models.Transaction).order_by(models.Transaction.transaction_date.desc()).all()

@app.get("/finance/transactions/{transaction_id}")
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    trans = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not trans:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return trans

@app.delete("/finance/transactions/{transaction_id}")
def delete_transaction(transaction_id: str, db: Session = Depends(get_db)):
    trans = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not trans:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    db.delete(trans)
    db.commit()
    return {"message": "Removido com sucesso"}

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

# ---------- RELATÓRIO PDF ----------

@app.get("/finance/report/pdf")
def finance_report(start_date: str, end_date: str):
    try:
        pdf_falso = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        return Response(
            content=pdf_falso,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=relatorio_{start_date}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# ---------- ROTAS DE ANIMAIS ----------
@app.get("/animals/")
def get_animals(db: Session = Depends(get_db)):
    return db.query(models.Animal).all()

# ---------- ROTA RAIZ (já existente) ----------
@app.get("/")
def root():
    return {"status": "Online", "database": "Conectado ao PostgreSQL"}

# ---------- NOVAS ROTAS PARA MONITORAMENTO ----------
# Rota HEAD para compatibilidade com monitores (ex.: UptimeRobot)
@app.head("/")
def head_root():
    return Response(status_code=200)

# Rota de saúde (opcional, mais leve que a raiz)
@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}