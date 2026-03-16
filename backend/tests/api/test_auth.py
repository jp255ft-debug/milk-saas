from fastapi.testclient import TestClient

def test_register_and_login(client: TestClient):
    # Registrar nova fazenda
    register_data = {
        "owner_name": "João Silva",
        "farm_name": "Fazenda Teste",
        "email": "teste@example.com",
        "password": "senha123"
    }
    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "teste@example.com"
    assert "id" in data

    # Fazer login
    login_data = {
        "username": "teste@example.com",
        "password": "senha123"
    }
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token

    # Acessar rota protegida /auth/me
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "teste@example.com"