class TestGetUserSummary:
    def test_summary_returns_all_computed_fields(self, client):
        payload = {
            "name": "Arthur", "password": "123", "budget_ceiling": 1000,
            "incomes": [{"name": "Salário", "income_value": 5000}],
            "expenses": [{"name": "Notebook", "expense_value": 1200, "installment": 3}],
            "bills": [{"name": "Aluguel", "bill_value": 300}],
            "investments": [{"name": "Tesouro", "value_invested": 10000, "dividends": 500}],
        }
        user_id = client.post("/users/", json=payload).json()["id"]
        summary = client.get(f"/users/{user_id}/summary").json()

        # balance = 5000 - 1200/3 - 300 = 4300 | net_worth = 4300 + 10500 = 14800
        assert summary["balance"] == 4300.0
        assert summary["net_worth"] == 14800.0
        assert summary["total_income"] == 5000.0
        assert summary["budget_status"] == "OK"  # gasto 700 / 1000 = 70%

    def test_summary_without_ceiling_omits_budget_status(self, client):
        user_id = client.post("/users/", json={"name": "Sem teto", "password": "123"}).json()["id"]
        assert client.get(f"/users/{user_id}/summary").json()["budget_status"] is None

    def test_summary_nonexistent_user_returns_404(self, client):
        assert client.get("/users/9999/summary").status_code == 404
