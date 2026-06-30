import pytest


@pytest.fixture
def user_id(client):
    return client.post("/users/", json={"name": "Arthur", "password": "123"}).json()["id"]


class TestMonthlyInvoicesEndpoint:
    def test_returns_window_of_requested_size(self, client, user_id):
        invoices = client.get(f"/users/{user_id}/monthly-invoices?months_ahead=4").json()["invoices"]
        assert len(invoices) == 4

    def test_installments_aggregated_in_window(self, client, user_id):
        # despesa começa no mês atual (default) → 300 em 3x cai dentro da janela
        client.post(f"/users/{user_id}/expenses", json={
            "name": "Geladeira", "expense_value": 300, "installment": 3
        })
        invoices = client.get(f"/users/{user_id}/monthly-invoices?months_ahead=6").json()["invoices"]
        assert invoices[0]["total"] == 100.0
        assert round(sum(i["total"] for i in invoices), 2) == 300.0

    def test_invalid_months_ahead_returns_422(self, client, user_id):
        assert client.get(f"/users/{user_id}/monthly-invoices?months_ahead=0").status_code == 422
