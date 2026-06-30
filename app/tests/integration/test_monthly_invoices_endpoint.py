import pytest


@pytest.fixture
def user_id(client):
    return client.post("/users/", json={"name": "Arthur", "password": "123"}).json()["id"]


class TestMonthlyInvoicesEndpoint:
    def test_default_window_has_six_months(self, client, user_id):
        response = client.get(f"/users/{user_id}/monthly-invoices")
        assert response.status_code == 200
        body = response.json()
        assert body["months_ahead"] == 6
        assert len(body["invoices"]) == 6

    def test_custom_months_ahead(self, client, user_id):
        body = client.get(f"/users/{user_id}/monthly-invoices?months_ahead=3").json()
        assert body["months_ahead"] == 3
        assert len(body["invoices"]) == 3

    def test_no_expenses_returns_all_zero(self, client, user_id):
        invoices = client.get(f"/users/{user_id}/monthly-invoices").json()["invoices"]
        assert all(inv["total"] == 0.0 for inv in invoices)

    def test_installments_aggregated_within_window(self, client, user_id):
        # despesa sem data → começa no mês atual (default do schema/modelo).
        # 300 em 3x com janela de 6 meses: todas as 3 parcelas caem na janela.
        client.post(f"/users/{user_id}/expenses", json={
            "name": "Geladeira", "expense_value": 300, "installment": 3
        })
        invoices = client.get(f"/users/{user_id}/monthly-invoices?months_ahead=6").json()["invoices"]
        assert invoices[0]["total"] == 100.0          # mês atual = 1ª parcela
        assert round(sum(i["total"] for i in invoices), 2) == 300.0  # soma = valor total
        assert invoices[3]["total"] == 0.0            # além das 3 parcelas

    def test_months_ahead_zero_returns_422(self, client, user_id):
        assert client.get(f"/users/{user_id}/monthly-invoices?months_ahead=0").status_code == 422

    def test_nonexistent_user_returns_404(self, client):
        assert client.get("/users/9999/monthly-invoices").status_code == 404
