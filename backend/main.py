from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuração de CORS – permite chamadas do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-mu-eight-30.vercel.app",   # domínio do frontend
        "http://localhost:3000"                      # desenvolvimento local
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API do Milk SaaS"}

@app.get("/animals/")
def get_animals():
    # Mock para teste – depois substitua pela lógica real
    return [
        {"id": "1", "tag_id": "001", "name": "Mimosa", "breed": "Girolando", "status": "lactation"},
        {"id": "2", "tag_id": "002", "name": "Estrela", "breed": "Holandês", "status": "dry"},
    ]
