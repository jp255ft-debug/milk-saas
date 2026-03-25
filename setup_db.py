import sys
import os

# Adiciona o diretório atual ao caminho do Python
sys.path.append(os.getcwd())

from app.database import engine
from app.models import Base

print("Tentando criar as tabelas no banco de dados...")
try:
    Base.metadata.create_all(bind=engine)
    print("Sucesso! Tabelas criadas ou já existentes.")
except Exception as e:
    print(f"Erro ao criar tabelas: {e}")