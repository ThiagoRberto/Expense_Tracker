import pytest


@pytest.fixture
def user_id(client):
    return client.post("/users/", json={"name": "Arthur", "password": "123"}).json()["id"]


# Os 4 routers de entidade (expenses, bills, incomes, investments) são o MESMO
# CRUD copiado. `expenses` é o representante (lifecycle completo); os outros
# recebem só um smoke de criação, para provar que a rota existe e persiste.
class TestExpensesCrud:
    def test_create_persists(self, client, user_id):
        data = client.post(f"/users/{user_id}/expenses", json={
            "name": "Notebook", "expense_value": 3000, "installment": 10
        }).json()
        assert data["id"] is not None
        assert data["name"] == "Notebook"
        assert data["installment"] == 10

    def test_delete_removes_expense(self, client, user_id):
        expense_id = client.post(f"/users/{user_id}/expenses", json={
            "name": "TV", "expense_value": 1500, "installment": 1
        }).json()["id"]
        assert client.delete(f"/users/{user_id}/expenses/{expense_id}").status_code == 204
        assert client.get(f"/users/{user_id}/expenses").json() == []

    def test_delete_nonexistent_returns_404(self, client, user_id):
        assert client.delete(f"/users/{user_id}/expenses/9999").status_code == 404

    def test_nonexistent_user_returns_404(self, client):
        assert client.get("/users/9999/expenses").status_code == 404


class TestOtherEntitiesSmoke:
    def test_create_bill(self, client, user_id):
        data = client.post(f"/users/{user_id}/bills", json={"name": "Aluguel", "bill_value": 1200}).json()
        assert data["id"] is not None and data["bill_value"] == 1200

    def test_create_income(self, client, user_id):
        data = client.post(f"/users/{user_id}/incomes", json={"name": "Salário", "income_value": 5000}).json()
        assert data["id"] is not None and data["income_value"] == 5000

    def test_create_investment(self, client, user_id):
        data = client.post(f"/users/{user_id}/investments", json={
            "name": "Tesouro", "value_invested": 10000, "dividends": 500
        }).json()
        assert data["id"] is not None and data["dividends"] == 500
