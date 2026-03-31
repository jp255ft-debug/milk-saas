import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega as variáveis do seu arquivo .env local
load_dotenv()

# Tenta buscar a URL do banco do seu arquivo de configuração
try:
    from app.database import SQLALCHEMY_DATABASE_URL
except ImportError:
    # Se não conseguir importar, busca direto do ambiente
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    print("❌ Erro: Não encontrei a URL do banco de dados. Verifique seu arquivo .env!")
    exit()

# Ajuste para o SQLAlchemy 2.0 (Render usa 'postgres://', mas o SQLAlchemy exige 'postgresql://')
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def migrate():
    # Comandos SQL para adicionar as colunas que seu novo código exige
    commands = [
        "ALTER TABLE farms ADD COLUMN IF NOT EXISTS plan_type VARCHAR DEFAULT 'free';",
        "ALTER TABLE farms ADD COLUMN IF NOT EXISTS subscription_status VARCHAR DEFAULT 'active';",
        "ALTER TABLE farms ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR;",
        "ALTER TABLE farms ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR;"
    ]
    
    with engine.connect() as conn:
        print("🔧 Conectado ao banco. Iniciando migração...")
        for cmd in commands:
            try:
                conn.execute(text(cmd))
                conn.commit() # Garante que a mudança seja salva
                print(f"✅ Sucesso no comando: {cmd[:40]}...")
            except Exception as e:
                print(f"⚠️ Aviso: {e}")
        print("🚀 Banco de dados do Milk SaaS atualizado!")

if __name__ == "__main__":
    migrate()