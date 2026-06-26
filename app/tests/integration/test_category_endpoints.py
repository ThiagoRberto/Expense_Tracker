import pytest


@pytest.fixture
def user_id(client):
    return client.post("/users/", json={"name": "Arthur", "password": "123"}).json()["id"]


class TestCategoryBudgetsEndpoints:
    def test_create_category_budget_returns_id(self, client, user_id):
        response = client.post(f"/users/{user_id}/category-budgets", json={
            "category": "alimentação", "ceiling": 800.0
        })
        assert response.status_code == 200
        assert response.json()["id"] is not None

    def test_create_category_budget_data_persisted(self, client, user_id):
        data = client.post(f"/users/{user_id}/category-budgets", json={
            "category": "transporte", "ceiling": 300.0
        }).json()
        assert data["category"] == "transporte"
        assert data["ceiling"] == 300.0

    def test_list_category_budgets_empty(self, client, user_id):
        assert client.get(f"/users/{user_id}/category-budgets").json() == []

    def test_list_category_budgets_after_create(self, client, user_id):
        client.post(f"/users/{user_id}/category-budgets", json={"category": "lazer", "ceiling": 500})
        assert len(client.get(f"/users/{user_id}/category-budgets").json()) == 1

    def test_create_category_budget_nonexistent_user_returns_404(self, client):
        response = client.post("/users/9999/category-budgets", json={"category": "x", "ceiling": 100})
        assert response.status_code == 404

    def test_list_category_budgets_nonexistent_user_returns_404(self, client):
        assert client.get("/users/9999/category-budgets").status_code == 404


class TestCategoryAlertsEndpoint:
    def test_no_budgets_returns_empty_alerts(self, client, user_id):
        response = client.get(f"/users/{user_id}/category-alerts")
        assert response.status_code == 200
        assert response.json()["alerts"] == []

    def test_alert_ok(self, client, user_id):
        client.post(f"/users/{user_id}/expenses", json={
            "name": "Mercado", "category": "alimentação", "expense_value": 300, "installment": 1
        })
        client.post(f"/users/{user_id}/category-budgets", json={"category": "alimentação", "ceiling": 800})

        alerts = client.get(f"/users/{user_id}/category-alerts").json()["alerts"]
        assert len(alerts) == 1
        assert alerts[0]["status"] == "OK"
        assert alerts[0]["total"] == 300.0
        assert alerts[0]["ceiling"] == 800.0

    def test_alert_warning(self, client, user_id):
        client.post(f"/users/{user_id}/expenses", json={
            "name": "Restaurantes", "category": "alimentação", "expense_value": 700, "installment": 1
        })
        client.post(f"/users/{user_id}/category-budgets", json={"category": "alimentação", "ceiling": 800})

        alert = client.get(f"/users/{user_id}/category-alerts").json()["alerts"][0]
        assert alert["status"] == "WARNING"  # 700/800 = 87.5%

    def test_alert_exceeded(self, client, user_id):
        client.post(f"/users/{user_id}/expenses", json={
            "name": "Viagem", "category": "lazer", "expense_value": 1200, "installment": 1
        })
        client.post(f"/users/{user_id}/category-budgets", json={"category": "lazer", "ceiling": 1000})

        alert = client.get(f"/users/{user_id}/category-alerts").json()["alerts"][0]
        assert alert["status"] == "EXCEEDED"

    def test_category_with_no_expenses_is_ok(self, client, user_id):
        client.post(f"/users/{user_id}/category-budgets", json={"category": "transporte", "ceiling": 500})

        alert = client.get(f"/users/{user_id}/category-alerts").json()["alerts"][0]
        assert alert["status"] == "OK"
        assert alert["total"] == 0.0

    def test_installment_expense_contributes_monthly_fraction(self, client, user_id):
        client.post(f"/users/{user_id}/expenses", json={
            "name": "Notebook", "category": "tecnologia", "expense_value": 3000, "installment": 10
        })
        client.post(f"/users/{user_id}/category-budgets", json={"category": "tecnologia", "ceiling": 500})

        alert = client.get(f"/users/{user_id}/category-alerts").json()["alerts"][0]
        assert alert["total"] == 300.0  # 3000/10
        assert alert["status"] == "OK"  # 300/500 = 60%

    def test_multiple_categories_independent_alerts(self, client, user_id):
        client.post(f"/users/{user_id}/expenses", json={
            "name": "Mercado", "category": "alimentação", "expense_value": 300, "installment": 1
        })
        client.post(f"/users/{user_id}/expenses", json={
            "name": "Viagem", "category": "lazer", "expense_value": 1200, "installment": 1
        })
        client.post(f"/users/{user_id}/category-budgets", json={"category": "alimentação", "ceiling": 800})
        client.post(f"/users/{user_id}/category-budgets", json={"category": "lazer", "ceiling": 1000})

        alerts = {a["category"]: a["status"] for a in client.get(f"/users/{user_id}/category-alerts").json()["alerts"]}
        assert alerts["alimentação"] == "OK"
        assert alerts["lazer"] == "EXCEEDED"

    def test_category_alerts_nonexistent_user_returns_404(self, client):
        assert client.get("/users/9999/category-alerts").status_code == 404
