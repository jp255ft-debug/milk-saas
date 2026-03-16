# Milk SaaS

## Configuração do Ambiente

### Backend
1. Criar ambiente virtual: python -m venv venv
2. Ativar: env\Scripts\activate (Windows) ou source venv/bin/activate (Linux/macOS)
3. Instalar dependências: pip install -r requirements.txt
4. Copiar .env.example para .env e ajustar as variáveis
5. Iniciar: uvicorn app.main:app --reload

### Frontend
1. Instalar dependências: 
pm install
2. Iniciar: 
pm run dev

Acesse http://localhost:3000
