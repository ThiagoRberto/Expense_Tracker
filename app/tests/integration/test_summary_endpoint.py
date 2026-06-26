class TestGetUserSummary:
    def test_summary_returns_correct_balance(self, client):
        payload = {
            "name": "Arthur",
            "password": "123",
            "incomes": [{"name": "Salário", "income_value": 5000}],
            "expenses": [{"name": "Notebook", "expense_value": 1200, "installment": 3}],
            "bills": [{"name": "Aluguel", "bill_value": 300}],
        }
        user_id = client.post("/users/", json=payload).json()["id"]
        summary = client.get(f"/users/{user_id}/summary").json()

        # 5000 - (1200/3) - 300 = 4300
        assert summary["balance"] == 4300.0

    def test_summary_returns_correct_net_worth(self, client):
        payload = {
            "name": "Arthur",
            "password": "123",
            "incomes": [{"name": "Salário", "income_value": 5000}],
            "bills": [{"name": "Aluguel", "bill_value": 300}],
            "investments": [{"name": "Tesouro", "value_invested": 10000, "dividends": 500}],
        }
        user_id = client.post("/users/", json=payload).json()["id"]
        summary = client.get(f"/users/{user_id}/summary").json()

        # balance = 5000 - 300 = 4700 | net_worth = 4700 + 10000 + 500 = 15200
        assert summary["net_worth"] == 15200.0

    def test_summary_without_budget_ceiling_omits_budget_status(self, client):
        payload = {"name": "Sem teto", "password": "123"}
        user_id = client.post("/users/", json=payload).json()["id"]
        summary = client.get(f"/users/{user_id}/summary").json()

        assert summary["budget_status"] is None

    def test_summary_budget_status_ok(self, client):
        payload = {
            "name": "Arthur",
            "password": "123",
            "budget_ceiling": 1000,
            "bills": [{"name": "Aluguel", "bill_value": 700}],
        }
        user_id = client.post("/users/", json=payload).json()["id"]
        summary = client.get(f"/users/{user_id}/summary").json()

        assert summary["budget_status"] == "OK"  # 700/1000 = 70%

    def test_summary_budget_status_warning(self, client):
        payload = {
            "name": "Arthur",
            "password": "123",
            "budget_ceiling": 1000,
            "bills": [{"name": "Aluguel", "bill_value": 900}],
        }
        user_id = client.post("/users/", json=payload).json()["id"]
        summary = client.get(f"/users/{user_id}/summary").json()

        assert summary["budget_status"] == "WARNING"  # 900/1000 = 90%

    def test_summary_budget_status_exceeded(self, client):
        payload = {
            "name": "Arthur",
            "password": "123",
            "budget_ceiling": 1000,
            "bills": [{"name": "Aluguel", "bill_value": 1200}],
        }
        user_id = client.post("/users/", json=payload).json()["id"]
        summary = client.get(f"/users/{user_id}/summary").json()

        assert summary["budget_status"] == "EXCEEDED"  # 1200/1000 = 120%

    def test_summary_user_with_no_entities_all_zeros(self, client):
        user_id = client.post("/users/", json={"name": "Vazio", "password": "123"}).json()["id"]
        summary = client.get(f"/users/{user_id}/summary").json()

        assert summary["balance"] == 0.0
        assert summary["net_worth"] == 0.0
        assert summary["total_income"] == 0.0
        assert summary["total_spending"] == 0.0

    def test_summary_nonexistent_user_returns_404(self, client):
        response = client.get("/users/9999/summary")
        assert response.status_code == 404
