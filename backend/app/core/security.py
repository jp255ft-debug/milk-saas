import os
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext

# Configurações extraídas do ambiente (Render) ou valores padrão
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_DAYS = 7

# AJUSTE CRÍTICO: Configura o passlib para usar o bcrypt moderno sem pânico de versão
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha coincide com o hash salvo."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # Se houver erro de hash antigo ou incompatível, logamos mas não derrubamos o app
        print(f"Erro na verificação de senha: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Gera um hash seguro a partir da senha em texto puro."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Gera o token JWT para o login."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decodifica e retorna o conteúdo do token."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])