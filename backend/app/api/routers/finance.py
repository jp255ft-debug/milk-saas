from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.schemas import finance as finance_schema

router = APIRouter(tags=["financeiro"])


# ========== CATEGORIAS (Gestão e Organização) ==========

@router.get("/categories", response_model=list[finance_schema.FinancialCategoryResponse])
def get_categories(
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    """Retorna todas as categorias cadastradas para a sua fazenda."""
    return db.query(models.FinancialCategory).filter(
        models.FinancialCategory.farm_id == current_farm.id
    ).all()


@router.delete("/categories/reset", summary="Limpar tudo (Faxina Total)")
def reset_finance(
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    """
    CUIDADO: Apaga todas as TRANSAÇÕES e CATEGORIAS da sua fazenda. 
    Limpamos os vínculos primeiro para evitar erros de integridade.
    """
    # 1. Apaga as transações primeiro (para liberar o vínculo)
    db.query(models.Transaction).filter(
        models.Transaction.farm_id == current_farm.id
    ).delete()

    # 2. Agora sim, apaga as categorias
    db.query(models.FinancialCategory).filter(
        models.FinancialCategory.farm_id == current_farm.id
    ).delete()

    db.commit()
    return {"message": "Faxina concluída! Transações e categorias removidas. O terreno está pronto para o novo Seed."}


@router.post("/categories/seed", summary="Plantar categorias financeiras padrão")
def seed_default_categories(
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    """
    Cadastra as categorias seguindo o modelo de gestão profissional:
    RECEITA, DESPESA VARIÁVEL e DESPESA FIXA.
    """
    
    CATEGORIAS_PADRAO = [
        # === RECEITAS (revenue) ===
        {"name": "Venda de Leite In Natura", "type": "revenue"},
        {"name": "Venda de Animais (Bezerros/Descarte)", "type": "revenue"},
        {"name": "Outras Receitas (Esterco/Serviços)", "type": "revenue"},

        # === DESPESAS VARIÁVEIS (variable_cost) ===
        {"name": "Milho (Grão/Moído)", "type": "variable_cost"},
        {"name": "Farelo de Soja", "type": "variable_cost"},
        {"name": "Torta de Algodão", "type": "variable_cost"},
        {"name": "Sal Mineral / Núcleo", "type": "variable_cost"},
        {"name": "Volumoso (Silagem/Pasto/Feno)", "type": "variable_cost"},
        {"name": "Medicamentos e Vacinas", "type": "variable_cost"},
        {"name": "Produtos de Limpeza (Ordenha)", "type": "variable_cost"},
        {"name": "Combustíveis e Lubrificantes", "type": "variable_cost"},

        # === DESPESAS FIXAS (fixed_cost) ===
        {"name": "Mão de Obra (Salários e Encargos)", "type": "fixed_cost"},
        {"name": "Energia Elétrica e Água", "type": "fixed_cost"},
        {"name": "Manutenção de Máquinas/Cercas", "type": "fixed_cost"},
        {"name": "Impostos e Taxas (ITR/Sindicato)", "type": "fixed_cost"},
        {"name": "Pró-labore (Retirada do Produtor)", "type": "fixed_cost"}
    ]

    inseridas = 0
    for cat in CATEGORIAS_PADRAO:
        existe = db.query(models.FinancialCategory).filter(
            models.FinancialCategory.farm_id == current_farm.id,
            models.FinancialCategory.name == cat["name"]
        ).first()

        if not existe:
            nova_categoria = models.FinancialCategory(
                farm_id=current_farm.id,
                name=cat["name"],
                type=cat["type"]
            )
            db.add(nova_categoria)
            inseridas += 1

    db.commit()
    return {
        "status": "sucesso",
        "message": f"{inseridas} categorias profissionais plantadas com sucesso!"
    }


# ========== TRANSAÇÕES (Lançamentos Diários) ==========

@router.post("/transactions", response_model=finance_schema.TransactionResponse)
def create_transaction(
    trans_in: finance_schema.TransactionCreate,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    """Lança uma nova movimentação financeira (Receita ou Despesa)."""
    category = db.query(models.FinancialCategory).filter(
        models.FinancialCategory.id == trans_in.category_id,
        models.FinancialCategory.farm_id == current_farm.id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
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
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    """Lista as transações com filtros de data e categoria."""
    query = db.query(models.Transaction).filter(models.Transaction.farm_id == current_farm.id)
    if start_date:
        query = query.filter(models.Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.transaction_date <= end_date)
    if category_id:
        query = query.filter(models.Transaction.category_id == category_id)
        
    return query.order_by(models.Transaction.transaction_date.desc()).all()


# ========== RESUMOS E PERFORMANCE (O Coração do Negócio) ==========

@router.get("/summary")
def get_financial_summary(
    year: int = Query(date.today().year),
    month: int = Query(date.today().month),
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    """Gera o resumo mensal: Receita, Despesa e o Saldo Líquido (Lucro)."""
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    revenues = db.query(func.sum(models.Transaction.amount)).join(models.FinancialCategory).filter(
        models.Transaction.farm_id == current_farm.id,
        models.Transaction.transaction_date.between(start_date, end_date),
        models.FinancialCategory.type == 'revenue'
    ).scalar() or 0
    
    expenses = db.query(func.sum(models.Transaction.amount)).join(models.FinancialCategory).filter(
        models.Transaction.farm_id == current_farm.id,
        models.Transaction.transaction_date.between(start_date, end_date),
        models.FinancialCategory.type.in_(['variable_cost', 'fixed_cost'])
    ).scalar() or 0
    
    return {
        "periodo": f"{month:02d}/{year}",
        "receitas": float(revenues),
        "despesas": float(expenses),
        "saldo_liquido": float(revenues - expenses)
    }


@router.get("/report/pdf")
def get_financial_report_pdf(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    """Gera relatório em PDF profissional para análise de custos."""
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

    story.append(Paragraph(f"Relatório Financeiro: {current_farm.name}", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Spacer(1, 20))

    data = [["Data", "Categoria", "Descrição", "Valor"]]
    for t in transactions:
        data.append([
            t.transaction_date.strftime("%d/%m/%Y"),
            t.category.name,
            t.description or "-",
            f"R$ {t.amount:.2f}"
        ])

    table = Table(data, colWidths=[80, 150, 150, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))
    
    story.append(table)
    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=relatorio_{start_date}.pdf"
    })