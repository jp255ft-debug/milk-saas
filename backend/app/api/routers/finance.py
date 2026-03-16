from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.schemas import finance as finance_schema

router = APIRouter(tags=["financeiro"])

@router.get("/categories", response_model=list[finance_schema.FinancialCategoryResponse])
def get_categories(
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    categories = db.query(models.FinancialCategory).all()
    return categories

@router.post("/transactions", response_model=finance_schema.TransactionResponse)
def create_transaction(
    trans_in: finance_schema.TransactionCreate,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    category = db.query(models.FinancialCategory).filter(models.FinancialCategory.id == trans_in.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    transaction = models.Transaction(
        farm_id=current_farm.id,
        category_id=trans_in.category_id,
        description=trans_in.description,
        amount=trans_in.amount,
        transaction_date=trans_in.transaction_date,
        is_paid=trans_in.is_paid
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.get("/transactions", response_model=list[finance_schema.TransactionResponse])
def get_transactions(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    category_id: UUID | None = Query(None),
    type: str | None = Query(None, regex='^(expense|revenue)$'),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    query = db.query(models.Transaction).filter(models.Transaction.farm_id == current_farm.id)
    if start_date:
        query = query.filter(models.Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.transaction_date <= end_date)
    if category_id:
        query = query.filter(models.Transaction.category_id == category_id)
    if type:
        query = query.join(models.Transaction.category).filter(models.FinancialCategory.type == type)
    transactions = query.order_by(models.Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
    return transactions

@router.get("/transactions/{transaction_id}", response_model=finance_schema.TransactionResponse)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.farm_id == current_farm.id
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.put("/transactions/{transaction_id}", response_model=finance_schema.TransactionResponse)
def update_transaction(
    transaction_id: str,
    trans_in: finance_schema.TransactionUpdate,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.farm_id == current_farm.id
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    update_data = trans_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
    
    db.commit()
    db.refresh(transaction)
    return transaction

@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: str,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.farm_id == current_farm.id
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    db.commit()
    return None

@router.get("/cost-per-liter", response_model=finance_schema.CostPerLiterResponse)
def get_cost_per_liter(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    liters = db.query(func.sum(models.MilkProduction.liters_produced)).join(models.Animal).filter(
        models.Animal.farm_id == current_farm.id,
        models.MilkProduction.production_date.between(start_date, end_date)
    ).scalar() or 0
    total_liters = float(liters)
    
    expenses = db.query(func.sum(models.Transaction.amount)).join(models.Transaction.category).filter(
        models.Transaction.farm_id == current_farm.id,
        models.Transaction.transaction_date.between(start_date, end_date),
        models.FinancialCategory.type.in_(['variable_cost', 'fixed_cost'])
    ).scalar() or 0
    total_expenses = float(expenses)
    
    cost_per_liter = total_expenses / total_liters if total_liters > 0 else 0
    
    category_expenses = db.query(
        models.FinancialCategory.name,
        func.sum(models.Transaction.amount).label('total')
    ).join(models.Transaction.category).filter(
        models.Transaction.farm_id == current_farm.id,
        models.Transaction.transaction_date.between(start_date, end_date),
        models.FinancialCategory.type.in_(['variable_cost', 'fixed_cost'])
    ).group_by(models.FinancialCategory.name).all()
    
    details = {cat.name: float(cat.total) for cat in category_expenses}
    
    return {
        "period_start": start_date,
        "period_end": end_date,
        "total_expenses": total_expenses,
        "total_liters": total_liters,
        "cost_per_liter": cost_per_liter,
        "details": details
    }

@router.get("/summary")
def get_financial_summary(
    year: int = Query(date.today().year),
    month: int = Query(date.today().month),
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year+1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month+1, 1) - timedelta(days=1)
    
    revenues = db.query(func.sum(models.Transaction.amount)).join(models.Transaction.category).filter(
        models.Transaction.farm_id == current_farm.id,
        models.Transaction.transaction_date.between(start_date, end_date),
        models.FinancialCategory.type == 'revenue'
    ).scalar() or 0
    
    expenses = db.query(func.sum(models.Transaction.amount)).join(models.Transaction.category).filter(
        models.Transaction.farm_id == current_farm.id,
        models.Transaction.transaction_date.between(start_date, end_date),
        models.FinancialCategory.type.in_(['variable_cost', 'fixed_cost'])
    ).scalar() or 0
    
    balance = revenues - expenses
    
    return {
        "period": f"{year}-{month:02d}",
        "revenues": float(revenues),
        "expenses": float(expenses),
        "balance": float(balance)
    }


@router.get("/report")
def get_financial_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    import io

    from fastapi.responses import StreamingResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    transactions = db.query(models.Transaction).filter(
        models.Transaction.farm_id == current_farm.id,
        models.Transaction.transaction_date.between(start_date, end_date)
    ).order_by(models.Transaction.transaction_date).all()

    revenues = sum(t.amount for t in transactions if t.category and t.category.type == 'revenue')
    expenses = sum(t.amount for t in transactions if t.category and t.category.type in ('variable_cost', 'fixed_cost'))
    balance = revenues - expenses

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title = Paragraph("Relatório Financeiro", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    period = Paragraph(f"Período: {start_date} a {end_date}", styles['Normal'])
    story.append(period)
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Receitas: R$ {revenues:.2f}", styles['Normal']))
    story.append(Paragraph(f"Despesas: R$ {expenses:.2f}", styles['Normal']))
    story.append(Paragraph(f"Saldo: R$ {balance:.2f}", styles['Normal']))
    story.append(Spacer(1, 12))

    data = [["Data", "Categoria", "Descrição", "Valor", "Pago"]]
    for t in transactions:
        cat_name = t.category.name if t.category else "N/A"
        data.append([
            t.transaction_date.strftime("%d/%m/%Y"),
            cat_name,
            t.description or "-",
            f"R$ {t.amount:.2f}",
            "Sim" if t.is_paid else "Não"
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(table)

    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=finance_report_{start_date}_{end_date}.pdf"
    })
