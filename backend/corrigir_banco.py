import os
from sqlalchemy import create_engine, text

# URL completa do banco (copiei do seu print)
DATABASE_URL = "postgresql://milk_saas_db_user:dR289vh2SOsBhojmNOohdrZ8IIxoi6sy@dpg-d6sm96vafjfc73f2gf90-a.oregon-postgres.render.com/milk_saas_db"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("🔧 Conectando ao banco...")
    
    # Atualiza os planos dos usuários antigos
    conn.execute(text("UPDATE farms SET plan_type = 'free', subscription_status = 'active' WHERE plan_type IS NULL;"))
    
    # Insere as categorias padrão para cada fazenda que ainda não as possui
    conn.execute(text("""
        INSERT INTO financial_categories (id, farm_id, name, type)
        SELECT gen_random_uuid(), id, 'Venda de Leite', 'revenue' FROM farms
        WHERE NOT EXISTS (SELECT 1 FROM financial_categories WHERE farm_id = farms.id AND name = 'Venda de Leite');
    """))
    conn.execute(text("""
        INSERT INTO financial_categories (id, farm_id, name, type)
        SELECT gen_random_uuid(), id, 'Venda de Animais', 'revenue' FROM farms
        WHERE NOT EXISTS (SELECT 1 FROM financial_categories WHERE farm_id = farms.id AND name = 'Venda de Animais');
    """))
    conn.execute(text("""
        INSERT INTO financial_categories (id, farm_id, name, type)
        SELECT gen_random_uuid(), id, 'Ração e Concentrados', 'variable_cost' FROM farms
        WHERE NOT EXISTS (SELECT 1 FROM financial_categories WHERE farm_id = farms.id AND name = 'Ração e Concentrados');
    """))
    conn.execute(text("""
        INSERT INTO financial_categories (id, farm_id, name, type)
        SELECT gen_random_uuid(), id, 'Medicamentos/Vacinas', 'variable_cost' FROM farms
        WHERE NOT EXISTS (SELECT 1 FROM financial_categories WHERE farm_id = farms.id AND name = 'Medicamentos/Vacinas');
    """))
    conn.execute(text("""
        INSERT INTO financial_categories (id, farm_id, name, type)
        SELECT gen_random_uuid(), id, 'Energia/Água', 'fixed_cost' FROM farms
        WHERE NOT EXISTS (SELECT 1 FROM financial_categories WHERE farm_id = farms.id AND name = 'Energia/Água');
    """))
    conn.execute(text("""
        INSERT INTO financial_categories (id, farm_id, name, type)
        SELECT gen_random_uuid(), id, 'Mão de Obra', 'fixed_cost' FROM farms
        WHERE NOT EXISTS (SELECT 1 FROM financial_categories WHERE farm_id = farms.id AND name = 'Mão de Obra');
    """))

    conn.commit()
    print("✅ Correção concluída com sucesso!")