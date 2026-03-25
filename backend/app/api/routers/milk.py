from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.schemas.milk import MilkProductionCreate, MilkProductionResponse, MilkProductionUpdate

router = APIRouter(tags=["produção de leite"])

@router.post("/", response_model=MilkProductionResponse)
def create_milk_production(
    milk_in: MilkProductionCreate,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    animal = db.query(models.Animal).filter(
        models.Animal.id == milk_in.animal_id,
        models.Animal.farm_id == current_farm.id
    ).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found or does not belong to your farm")
    
    milk = models.MilkProduction(
        animal_id=milk_in.animal_id,
        production_date=milk_in.production_date,
        liters_produced=milk_in.liters_produced,
        period=milk_in.period,
        fat_content=milk_in.fat_content,
        protein_content=milk_in.protein_content
    )
    db.add(milk)
    db.commit()
    db.refresh(milk)
    return milk

@router.get("/", response_model=list[MilkProductionResponse])
def read_milk_productions(
    animal_id: UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    query = db.query(models.MilkProduction).join(models.Animal).filter(
        models.Animal.farm_id == current_farm.id
    )
    if animal_id:
        query = query.filter(models.MilkProduction.animal_id == animal_id)
    if start_date:
        query = query.filter(models.MilkProduction.production_date >= start_date)
    if end_date:
        query = query.filter(models.MilkProduction.production_date <= end_date)
    
    productions = query.order_by(models.MilkProduction.production_date.desc()).offset(skip).limit(limit).all()
    return productions

@router.get("/summary/totals")
def get_production_summary(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    query = db.query(models.MilkProduction).join(models.Animal).filter(
        models.Animal.farm_id == current_farm.id
    )
    if start_date:
        query = query.filter(models.MilkProduction.production_date >= start_date)
    if end_date:
        query = query.filter(models.MilkProduction.production_date <= end_date)
    
    total_liters = db.query(func.sum(models.MilkProduction.liters_produced)).filter(
        models.MilkProduction.id.in_(query.with_entities(models.MilkProduction.id))
    ).scalar() or 0
    
    per_animal = db.query(
        models.Animal.id,
        models.Animal.name,
        models.Animal.tag_id,
        func.sum(models.MilkProduction.liters_produced).label('total')
    ).join(models.MilkProduction).filter(
        models.Animal.farm_id == current_farm.id,
        models.MilkProduction.production_date >= (date.today() - timedelta(days=30))
    ).group_by(models.Animal.id).all()
    
    return {
        "total_liters": float(total_liters),
        "per_animal": [
            {
                "animal_id": str(a.id),
                "animal_name": a.name,
                "tag_id": a.tag_id,
                "total": float(a.total)
            } for a in per_animal
        ]
    }

@router.get("/dashboard")
def get_dashboard_data(
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    try:
        total_animals = db.query(models.Animal).filter(models.Animal.farm_id == current_farm.id).count()
        lactating_animals = db.query(models.Animal).filter(
            models.Animal.farm_id == current_farm.id,
            models.Animal.status == "lactation"
        ).count()
        
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        daily_production = db.query(
            models.MilkProduction.production_date,
            func.sum(models.MilkProduction.liters_produced).label('total')
        ).join(models.Animal).filter(
            models.Animal.farm_id == current_farm.id,
            models.MilkProduction.production_date.between(start_date, end_date)
        ).group_by(models.MilkProduction.production_date).order_by(models.MilkProduction.production_date).all()
        
        production_by_day = []
        current = start_date
        while current <= end_date:
            day_data = next((item for item in daily_production if item.production_date == current), None)
            production_by_day.append({
                "date": current.isoformat(),
                "total": float(day_data.total) if day_data else 0.0
            })
            current += timedelta(days=1)
        
        last_30_days_start = end_date - timedelta(days=29)
        
        per_animal = db.query(
            models.Animal.id,
            models.Animal.name,
            models.Animal.tag_id,
            func.sum(models.MilkProduction.liters_produced).label('total')
        ).join(models.MilkProduction).filter(
            models.Animal.farm_id == current_farm.id,
            models.MilkProduction.production_date >= last_30_days_start
        ).group_by(models.Animal.id).order_by(func.sum(models.MilkProduction.liters_produced).desc()).limit(5).all()
        
        animal_production = db.query(
            models.Animal.id,
            func.sum(models.MilkProduction.liters_produced).label('total'),
            func.count(func.distinct(models.MilkProduction.production_date)).label('days')
        ).join(models.MilkProduction).filter(
            models.Animal.farm_id == current_farm.id,
            models.MilkProduction.production_date >= last_30_days_start
        ).group_by(models.Animal.id).all()

        if animal_production:
            soma_medias = sum(item.total / item.days for item in animal_production)
            avg_production = soma_medias / len(animal_production)
        else:
            avg_production = 0.0
        
        return {
            "total_animals": total_animals,
            "lactating_animals": lactating_animals,
            "avg_production_per_animal": float(avg_production),
            "production_last_7_days": production_by_day,
            "top_5_animals": [
                {
                    "id": str(a.id),
                    "name": a.name or a.tag_id,
                    "total": float(a.total)
                } for a in per_animal
            ]
        }
    except Exception as e:
        import traceback
        print("ERRO NO DASHBOARD:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/report")
def get_milk_report(
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

    productions = db.query(models.MilkProduction).join(models.Animal).filter(
        models.Animal.farm_id == current_farm.id,
        models.MilkProduction.production_date.between(start_date, end_date)
    ).order_by(models.MilkProduction.production_date).all()

    total_liters = sum(p.liters_produced for p in productions)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title = Paragraph("Relatório de Produção de Leite", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    period = Paragraph(f"Período: {start_date} a {end_date}", styles['Normal'])
    story.append(period)
    story.append(Spacer(1, 12))

    data = [["Data", "Animal", "Litros", "Período"]]
    for p in productions:
        animal = db.query(models.Animal).filter(models.Animal.id == p.animal_id).first()
        animal_name = animal.name or animal.tag_id
        data.append([
            p.production_date.strftime("%d/%m/%Y"),
            animal_name,
            f"{p.liters_produced:.2f}",
            p.period or "-"
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
    story.append(Spacer(1, 12))

    total_para = Paragraph(f"Total de litros: {total_liters:.2f}", styles['Normal'])
    story.append(total_para)

    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=milk_report_{start_date}_{end_date}.pdf"
    })

@router.get("/{milk_id}", response_model=MilkProductionResponse)
def read_milk_production(
    milk_id: str,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    milk = db.query(models.MilkProduction).join(models.Animal).filter(
        models.MilkProduction.id == milk_id,
        models.Animal.farm_id == current_farm.id
    ).first()
    if not milk:
        raise HTTPException(status_code=404, detail="Milk production not found")
    return milk

@router.put("/{milk_id}", response_model=MilkProductionResponse)
def update_milk_production(
    milk_id: str,
    milk_in: MilkProductionUpdate,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    milk = db.query(models.MilkProduction).join(models.Animal).filter(
        models.MilkProduction.id == milk_id,
        models.Animal.farm_id == current_farm.id
    ).first()
    if not milk:
        raise HTTPException(status_code=404, detail="Milk production not found")
    
    update_data = milk_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(milk, field, value)
    
    db.commit()
    db.refresh(milk)
    return milk

@router.delete("/{milk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_milk_production(
    milk_id: str,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    milk = db.query(models.MilkProduction).join(models.Animal).filter(
        models.MilkProduction.id == milk_id,
        models.Animal.farm_id == current_farm.id
    ).first()
    if not milk:
        raise HTTPException(status_code=404, detail="Milk production not found")
    db.delete(milk)
    db.commit()
    return None