from fastapi.testclient import TestClient

def test_crud_animals(client: TestClient):
    # Primeiro criar um usuário e obter token
    register_data = {
        "owner_name": "Maria",
        "farm_name": "Fazenda Animais",
        "email": "maria@example.com",
        "password": "senha123"
    }
    client.post("/auth/register", json=register_data)
    login_data = {"username": "maria@example.com", "password": "senha123"}
    token = client.post("/auth/token", data=login_data).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Criar animal (sem farm_id)
    animal_data = {
        "tag_id": "123",
        "name": "Vaca Mocha",
        "breed": "Holandesa",
        "birth_date": "2020-01-01",
        "status": "lactation"
    }
    response = client.post("/animals/", json=animal_data, headers=headers)
    assert response.status_code == 200
    animal_id = response.json()["id"]

    # Listar animais
    response = client.get("/animals/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Buscar animal por ID
    response = client.get(f"/animals/{animal_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Vaca Mocha"

    # Atualizar animal
    update_data = {"name": "Vaca Mocha Atualizada"}
    response = client.put(f"/animals/{animal_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Vaca Mocha Atualizada"

    # Deletar animal
    response = client.delete(f"/animals/{animal_id}", headers=headers)
    assert response.status_code == 204
