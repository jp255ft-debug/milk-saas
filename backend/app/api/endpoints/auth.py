from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.core import security

router = APIRouter()

@router.post("/register", response_model=schemas.FarmResponse)
def register(
    farm_in: schemas.FarmCreate,
    db: Session = Depends(deps.get_db)
):
    existing_farm = db.query(models.Farm).filter(
        models.Farm.email == farm_in.email
    ).first()
    if existing_farm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = security.get_password_hash(farm_in.password)
    db_farm = models.Farm(
        owner_name=farm_in.owner_name,
        farm_name=farm_in.farm_name,
        email=farm_in.email,
        hashed_password=hashed_password
    )
    
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    return db_farm

@router.post("/login", response_model=schemas.Token)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db)
):
    farm = db.query(models.Farm).filter(
        models.Farm.email == form_data.username
    ).first()
    
    if not farm or not security.verify_password(form_data.password, farm.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(days=security.ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = security.create_access_token(
        data={"sub": str(farm.id)},
        expires_delta=access_token_expires
    )
    
    # AJUSTE CRUCIAL: secure=True e samesite="none" para cruzar domínios
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=security.ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=security.ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        secure=True,
        samesite="none",
        path="/",
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(response: Response):
    # AJUSTE CRUCIAL: O logout precisa das mesmas tags para conseguir limpar o cookie de produção
    response.delete_cookie("access_token", path="/", secure=True, samesite="none")
    return {"message": "Logged out"}

@router.get("/me", response_model=schemas.FarmResponse)
def read_current_farm(
    current_farm: models.Farm = Depends(deps.get_current_farm)
):
    return current_farm