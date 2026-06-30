import pytest


@pytest.fixture
def user_id(client):
    return client.post("/users/", json={"name": "Arthur", "password": "123"}).json()["id"]


class TestExpensesEndpoints:
    def test_create_expense_returns_id(self, client, user_id):
        response = client.post(f"/users/{user_id}/expenses", json={
            "name": "Notebook", "expense_value": 3000, "installment": 10
        })
        assert response.status_code == 200
        assert response.json()["id"] is not None

    def test_create_expense_data_persisted(self, client, user_id):
        response = client.post(f"/users/{user_id}/expenses", json={
            "name": "Notebook", "expense_value": 3000, "installment": 10
        })
        data = response.json()
        assert data["name"] == "Notebook"
        assert data["expense_value"] == 3000
        assert data["installment"] == 10

    def test_list_expenses_empty(self, client, user_id):
        assert client.get(f"/users/{user_id}/expenses").json() == []

    def test_list_expenses_after_create(self, client, user_id):
        client.post(f"/users/{user_id}/expenses", json={
            "name": "TV", "expense_value": 1500, "installment": 6
        })
        assert len(client.get(f"/users/{user_id}/expenses").json()) == 1

    def test_list_expenses_multiple(self, client, user_id):
        client.post(f"/users/{user_id}/expenses", json={"name": "A", "expense_value": 100, "installment": 1})
        client.post(f"/users/{user_id}/expenses", json={"name": "B", "expense_value": 200, "installment": 2})
        assert len(client.get(f"/users/{user_id}/expenses").json()) == 2

    def test_create_expense_nonexistent_user_returns_404(self, client):
        response = client.post("/users/9999/expenses", json={
            "name": "X", "expense_value": 100, "installment": 1
        })
        assert response.status_code == 404

    def test_list_expenses_nonexistent_user_returns_404(self, client):
        assert client.get("/users/9999/expenses").status_code == 404


class TestBillsEndpoints:
    def test_create_bill_returns_id(self, client, user_id):
        response = client.post(f"/users/{user_id}/bills", json={
            "name": "Aluguel", "bill_value": 1200
        })
        assert response.status_code == 200
        assert response.json()["id"] is not None

    def test_create_bill_data_persisted(self, client, user_id):
        data = client.post(f"/users/{user_id}/bills", json={
            "name": "Aluguel", "bill_value": 1200
        }).json()
        assert data["name"] == "Aluguel"
        assert data["bill_value"] == 1200

    def test_list_bills_empty(self, client, user_id):
        assert client.get(f"/users/{user_id}/bills").json() == []

    def test_list_bills_after_create(self, client, user_id):
        client.post(f"/users/{user_id}/bills", json={"name": "Internet", "bill_value": 100})
        assert len(client.get(f"/users/{user_id}/bills").json()) == 1

    def test_create_bill_nonexistent_user_returns_404(self, client):
        assert client.post("/users/9999/bills", json={"name": "X", "bill_value": 100}).status_code == 404

    def test_list_bills_nonexistent_user_returns_404(self, client):
        assert client.get("/users/9999/bills").status_code == 404


class TestIncomesEndpoints:
    def test_create_income_returns_id(self, client, user_id):
        response = client.post(f"/users/{user_id}/incomes", json={
            "name": "Salário", "income_value": 5000
        })
        assert response.status_code == 200
        assert response.json()["id"] is not None

    def test_create_income_data_persisted(self, client, user_id):
        data = client.post(f"/users/{user_id}/incomes", json={
            "name": "Salário", "income_value": 5000
        }).json()
        assert data["name"] == "Salário"
        assert data["income_value"] == 5000

    def test_list_incomes_empty(self, client, user_id):
        assert client.get(f"/users/{user_id}/incomes").json() == []

    def test_list_incomes_after_create(self, client, user_id):
        client.post(f"/users/{user_id}/incomes", json={"name": "Freelance", "income_value": 1500})
        assert len(client.get(f"/users/{user_id}/incomes").json()) == 1

    def test_create_income_nonexistent_user_returns_404(self, client):
        assert client.post("/users/9999/incomes", json={"name": "X", "income_value": 100}).status_code == 404

    def test_list_incomes_nonexistent_user_returns_404(self, client):
        assert client.get("/users/9999/incomes").status_code == 404


class TestInvestmentsEndpoints:
    def test_create_investment_returns_id(self, client, user_id):
        response = client.post(f"/users/{user_id}/investments", json={
            "name": "Tesouro", "value_invested": 10000, "dividends": 500
        })
        assert response.status_code == 200
        assert response.json()["id"] is not None

    def test_create_investment_data_persisted(self, client, user_id):
        data = client.post(f"/users/{user_id}/investments", json={
            "name": "Tesouro", "value_invested": 10000, "dividends": 500
        }).json()
        assert data["name"] == "Tesouro"
        assert data["value_invested"] == 10000
        assert data["dividends"] == 500

    def test_list_investments_empty(self, client, user_id):
        assert client.get(f"/users/{user_id}/investments").json() == []

    def test_list_investments_after_create(self, client, user_id):
        client.post(f"/users/{user_id}/investments", json={
            "name": "CDB", "value_invested": 5000, "dividends": 0
        })
        assert len(client.get(f"/users/{user_id}/investments").json()) == 1

    def test_create_investment_nonexistent_user_returns_404(self, client):
        assert client.post("/users/9999/investments", json={
            "name": "X", "value_invested": 100, "dividends": 0
        }).status_code == 404

    def test_list_investments_nonexistent_user_returns_404(self, client):
        assert client.get("/users/9999/investments").status_code == 404


class TestDeleteEndpoints:
    def test_delete_expense_returns_204(self, client, user_id):
        expense_id = client.post(f"/users/{user_id}/expenses", json={
            "name": "TV", "expense_value": 1500, "installment": 1
        }).json()["id"]
        assert client.delete(f"/users/{user_id}/expenses/{expense_id}").status_code == 204

    def test_delete_expense_removes_from_list(self, client, user_id):
        expense_id = client.post(f"/users/{user_id}/expenses", json={
            "name": "TV", "expense_value": 1500, "installment": 1
        }).json()["id"]
        client.delete(f"/users/{user_id}/expenses/{expense_id}")
        assert client.get(f"/users/{user_id}/expenses").json() == []

    def test_delete_expense_nonexistent_returns_404(self, client, user_id):
        assert client.delete(f"/users/{user_id}/expenses/9999").status_code == 404

    def test_delete_bill_returns_204(self, client, user_id):
        bill_id = client.post(f"/users/{user_id}/bills", json={
            "name": "Internet", "bill_value": 100
        }).json()["id"]
        assert client.delete(f"/users/{user_id}/bills/{bill_id}").status_code == 204

    def test_delete_bill_removes_from_list(self, client, user_id):
        bill_id = client.post(f"/users/{user_id}/bills", json={
            "name": "Internet", "bill_value": 100
        }).json()["id"]
        client.delete(f"/users/{user_id}/bills/{bill_id}")
        assert client.get(f"/users/{user_id}/bills").json() == []

    def test_delete_income_returns_204(self, client, user_id):
        income_id = client.post(f"/users/{user_id}/incomes", json={
            "name": "Salário", "income_value": 5000
        }).json()["id"]
        assert client.delete(f"/users/{user_id}/incomes/{income_id}").status_code == 204

    def test_delete_income_removes_from_list(self, client, user_id):
        income_id = client.post(f"/users/{user_id}/incomes", json={
            "name": "Salário", "income_value": 5000
        }).json()["id"]
        client.delete(f"/users/{user_id}/incomes/{income_id}")
        assert client.get(f"/users/{user_id}/incomes").json() == []

    def test_delete_investment_returns_204(self, client, user_id):
        investment_id = client.post(f"/users/{user_id}/investments", json={
            "name": "CDB", "value_invested": 5000, "dividends": 0
        }).json()["id"]
        assert client.delete(f"/users/{user_id}/investments/{investment_id}").status_code == 204

    def test_delete_investment_removes_from_list(self, client, user_id):
        investment_id = client.post(f"/users/{user_id}/investments", json={
            "name": "CDB", "value_invested": 5000, "dividends": 0
        }).json()["id"]
        client.delete(f"/users/{user_id}/investments/{investment_id}")
        assert client.get(f"/users/{user_id}/investments").json() == []

    def test_delete_category_budget_returns_204(self, client, user_id):
        budget_id = client.post(f"/users/{user_id}/category-budgets", json={
            "category": "alimentação", "ceiling": 800
        }).json()["id"]
        assert client.delete(f"/users/{user_id}/category-budgets/{budget_id}").status_code == 204

    def test_delete_category_budget_removes_from_list(self, client, user_id):
        budget_id = client.post(f"/users/{user_id}/category-budgets", json={
            "category": "alimentação", "ceiling": 800
        }).json()["id"]
        client.delete(f"/users/{user_id}/category-budgets/{budget_id}")
        assert client.get(f"/users/{user_id}/category-budgets").json() == []

    def test_delete_category_budget_nonexistent_returns_404(self, client, user_id):
        assert client.delete(f"/users/{user_id}/category-budgets/9999").status_code == 404
