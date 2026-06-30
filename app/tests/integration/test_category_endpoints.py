import pytest


@pytest.fixture
def user_id(client):
    return client.post("/users/", json={"name": "Arthur", "password": "123"}).json()["id"]


class TestCategoryBudgetsCrud:
    def test_create_persists(self, client, user_id):
        data = client.post(f"/users/{user_id}/category-budgets", json={
            "category": "alimentação", "ceiling": 800.0
        }).json()
        assert data["id"] is not None
        assert data["category"] == "alimentação"
        assert data["ceiling"] == 800.0

    def test_delete_removes_budget(self, client, user_id):
        budget_id = client.post(f"/users/{user_id}/category-budgets", json={
            "category": "alimentação", "ceiling": 800
        }).json()["id"]
        assert client.delete(f"/users/{user_id}/category-budgets/{budget_id}").status_code == 204
        assert client.get(f"/users/{user_id}/category-budgets").json() == []

    def test_nonexistent_user_returns_404(self, client):
        response = client.post("/users/9999/category-budgets", json={"category": "x", "ceiling": 100})
        assert response.status_code == 404


class TestCategoryAlerts:
    def test_no_budgets_returns_empty(self, client, user_id):
        assert client.get(f"/users/{user_id}/category-alerts").json()["alerts"] == []

    def test_alerts_reflect_status_per_category(self, client, user_id):
        client.post(f"/users/{user_id}/expenses", json={
            "name": "Mercado", "category": "alimentação", "expense_value": 300, "installment": 1
        })
        client.post(f"/users/{user_id}/expenses", json={
            "name": "Viagem", "category": "lazer", "expense_value": 1200, "installment": 1
        })
        client.post(f"/users/{user_id}/category-budgets", json={"category": "alimentação", "ceiling": 800})
        client.post(f"/users/{user_id}/category-budgets", json={"category": "lazer", "ceiling": 1000})

        alerts = {a["category"]: a["status"] for a in client.get(f"/users/{user_id}/category-alerts").json()["alerts"]}
        assert alerts == {"alimentação": "OK", "lazer": "EXCEEDED"}
