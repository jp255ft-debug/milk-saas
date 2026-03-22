import psycopg2
from datetime import datetime, timedelta
import sys
from collections import defaultdict

db_url = 'postgresql://milk_saas_db_user:dR289vh2SOsBhojmNOohdrZ8IIxoi6sy@dpg-d6sm96vafjfc73f2gf90-a/milk_saas_db'

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    hoje = datetime.now().date()
    inicio = hoje - timedelta(days=29)
    print(f"Período analisado: {inicio} a {hoje}\n")

    cur.execute("""
        SELECT a.id, a.name, a.tag_id, mp.production_date, mp.liters_produced
        FROM milk_productions mp
        JOIN animals a ON mp.animal_id = a.id
        WHERE mp.production_date BETWEEN %s AND %s
        ORDER BY a.id, mp.production_date
    """, (inicio, hoje))

    rows = cur.fetchall()
    if not rows:
        print("Nenhuma produção encontrada.")
        sys.exit(0)

    animais = defaultdict(lambda: {'datas': set(), 'total': 0.0, 'producoes': []})

    for row in rows:
        animal_id = row[0]
        nome = row[1] or row[2]
        data = row[3]
        litros = row[4]
        animais[animal_id]['datas'].add(data)
        animais[animal_id]['total'] += litros
        animais[animal_id]['producoes'].append((data, litros))

    soma_medias = 0.0
    for animal_id, dados in animais.items():
        dias = len(dados['datas'])
        total = dados['total']
        media_animal = total / dias
        soma_medias += media_animal
        print(f"Animal {animal_id[:8]}... ({dados['producoes'][0][1]}):")
        print(f"  Total: {total:.2f} L em {dias} dia(s) -> média {media_animal:.2f} L/dia")
        for data, litros in dados['producoes']:
            print(f"    {data.strftime('%d/%m')}: {litros:.1f} L")

    media_geral = soma_medias / len(animais)
    print("-" * 50)
    print(f"MÉDIA POR ANIMAL: {media_geral:.2f} L/dia")
    print(f"Animais que produziram: {len(animais)}")

    cur.close()
    conn.close()

except Exception as e:
    print(f"Erro: {e}")
