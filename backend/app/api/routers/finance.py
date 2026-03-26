from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.schemas import finance as finance_schema

router = APIRouter(tags=["financeiro"])

# ========== CATEGORIAS ==========

@router.get("/categories", response_model=list[finance_schema.FinancialCategoryResponse])
def get_categories(
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    return db.query(models.FinancialCategory).filter(
        models.FinancialCategory.farm_id == current_farm.id
    ).all()

@router.delete("/categories/reset")
def reset_finance(
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    db.query(models.Transaction).filter(models.Transaction.farm_id == current_farm.id).delete()
    db.query(models.FinancialCategory).filter(models.FinancialCategory.farm_id == current_farm.id).delete()
    db.commit()
    return {"message": "Faxina concluída!"}

@router.post("/categories/seed")
def seed_default_categories(
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    CATEGORIAS_PADRAO = [
        {"name": "Venda de Leite In Natura", "type": "revenue"},
        {"name": "Venda de Animais", "type": "revenue"},
        {"name": "Milho (Grão/Moído)", "type": "variable_cost"},
        {"name": "Farelo de Soja", "type": "variable_cost"},
        {"name": "Medicamentos e Vacinas", "type": "variable_cost"},
        {"name": "Mão de Obra", "type": "fixed_cost"},
        {"name": "Energia Elétrica e Água", "type": "fixed_cost"}
    ]
    inseridas = 0
    for cat in CATEGORIAS_PADRAO:
        existe = db.query(models.FinancialCategory).filter(
            models.FinancialCategory.farm_id == current_farm.id,
            models.FinancialCategory.name == cat["name"]
        ).first()
        if not existe:
            nova = models.FinancialCategory(farm_id=current_farm.id, **cat)
            db.add(nova)
            inseridas += 1
    db.commit()
    return {"status": "sucesso", "message": f"{inseridas} categorias plantadas!"}

# ========== TRANSAÇÕES (CRUD COMPLETO) ==========

@router.post("/transactions", response_model=finance_schema.TransactionResponse)
def create_transaction(
    trans_in: finance_schema.TransactionCreate,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    transaction = models.Transaction(farm_id=current_farm.id, **trans_in.dict())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.get("/transactions", response_model=list[finance_schema.TransactionResponse])
def get_transactions(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    query = db.query(models.Transaction).filter(models.Transaction.farm_id == current_farm.id)
    if start_date: query = query.filter(models.Transaction.transaction_date >= start_date)
    if end_date: query = query.filter(models.Transaction.transaction_date <= end_date)
    return query.order_by(models.Transaction.transaction_date.desc()).all()

# NOVA ROTA: Buscar uma transação (Resolve o 404 da Edição)
@router.get("/transactions/{transaction_id}", response_model=finance_schema.TransactionResponse)
def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.farm_id == current_farm.id
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return transaction

# NOVA ROTA: Excluir (Resolve o 404 do botão Excluir)
@router.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: UUID,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.farm_id == current_farm.id
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    db.delete(transaction)
    db.commit()
    return {"message": "Transação removida com sucesso"}

# ========== RESUMO E PDF ==========

@router.get("/summary")
def get_financial_summary(
    year: int = Query(date.today().year),
    month: int = Query(date.today().month),
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    start = date(year, month, 1)
    end = (date(year + (1 if month == 12 else 0), (month % 12) + 1, 1) - timedelta(days=1))
    
    rev = db.query(func.sum(models.Transaction.amount)).join(models.FinancialCategory).filter(
        models.Transaction.farm_id == current_farm.id,
        models.Transaction.transaction_date.between(start, end),
        models.FinancialCategory.type == 'revenue'
    ).scalar() or 0
    
    exp = db.query(func.sum(models.Transaction.amount)).join(models.FinancialCategory).filter(
        models.Transaction.farm_id == current_farm.id,
        models.Transaction.transaction_date.between(start, end),
        models.FinancialCategory.type.in_(['variable_cost', 'fixed_cost'])
    ).scalar() or 0
    
    return {"receitas": float(rev), "despesas": float(exp), "saldo_liquido": float(rev - exp)}

@router.get("/report/pdf")
def get_financial_report_pdf(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    import io
    from fastapi.responses import StreamingResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    transactions = db.query(models.Transaction).filter(
        models.Transaction.farm_id == current_farm.id,
        models.Transaction.transaction_date.between(start_date, end_date)
    ).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # CORREÇÃO AQUI: farm_name em vez de name
    farm_title = getattr(current_farm, 'farm_name', 'Minha Fazenda')
    story.append(Paragraph(f"Relatório Financeiro: {farm_title}", styles['Title']))
    story.append(Spacer(1, 12))
    
    data = [["Data", "Categoria", "Descrição", "Valor"]]
    for t in transactions:
        data.append([t.transaction_date.strftime("%d/%m/%Y"), t.category.name, t.description or "-", f"R$ {t.amount:.2f}"])

    table = Table(data, colWidths=[80, 150, 150, 80])
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.darkblue), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=relatorio.pdf"})