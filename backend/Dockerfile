FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema necessárias para psycopg2 (se for usar PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos
COPY requirements.txt .

# Instala as dependências Python usando --prefer-binary para priorizar wheels
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copia o código da aplicação
COPY . .

# Expõe a porta que o uvicorn usará (a porta será definida pelo Render via $PORT)
EXPOSE 8000

# Comando para iniciar a aplicação
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
