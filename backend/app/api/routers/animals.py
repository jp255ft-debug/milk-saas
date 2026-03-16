
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.schemas import animal as animal_schema

# Removido o prefix="/animals" – agora será definido apenas no main.py
router = APIRouter(tags=["animais"])

@router.post("/", response_model=animal_schema.AnimalResponse)
def create_animal(
    animal_in: animal_schema.AnimalCreate,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    """
    Cria um novo animal associado à fazenda autenticada.
    """
    animal = models.Animal(
        farm_id=current_farm.id,
        **animal_in.model_dump()
    )
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal

@router.get("/", response_model=list[animal_schema.AnimalResponse])
def read_animals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    """
    Lista todos os animais da fazenda logada (com paginação).
    """
    animals = db.query(models.Animal).filter(
        models.Animal.farm_id == current_farm.id
    ).offset(skip).limit(limit).all()
    return animals

@router.get("/{animal_id}", response_model=animal_schema.AnimalResponse)
def read_animal(
    animal_id: str,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    """
    Retorna os detalhes de um animal específico (se pertencer à fazenda).
    """
    animal = db.query(models.Animal).filter(
        models.Animal.id == animal_id,
        models.Animal.farm_id == current_farm.id
    ).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    return animal

@router.put("/{animal_id}", response_model=animal_schema.AnimalResponse)
def update_animal(
    animal_id: str,
    animal_in: animal_schema.AnimalUpdate,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    """
    Atualiza os dados de um animal existente.
    """
    animal = db.query(models.Animal).filter(
        models.Animal.id == animal_id,
        models.Animal.farm_id == current_farm.id
    ).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    update_data = animal_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(animal, field, value)
    
    db.commit()
    db.refresh(animal)
    return animal

@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_animal(
    animal_id: str,
    db: Session = Depends(deps.get_db),
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    """
    Remove um animal da base.
    """
    animal = db.query(models.Animal).filter(
        models.Animal.id == animal_id,
        models.Animal.farm_id == current_farm.id
    ).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    db.delete(animal)
    db.commit()
    return None