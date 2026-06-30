import pytest


@pytest.fixture
def user_id(client):
    return client.post("/users/", json={"name": "Arthur", "password": "123"}).json()["id"]


class TestInstallmentsEndpoint:
    def test_no_expenses_returns_empty_projections(self, client, user_id):
        response = client.get(f"/users/{user_id}/installments")
        assert response.status_code == 200
        assert response.json()["projections"] == []

    def test_single_installment_expense_has_one_entry(self, client, user_id):
        client.post(f"/users/{user_id}/expenses", json={
            "name": "Mercado", "category": "alimentação",
            "expense_value": 300, "installment": 1,
            "start_month": 6, "start_year": 2026,
        })
        projections = client.get(f"/users/{user_id}/installments").json()["projections"]
        assert len(projections) == 1
        assert len(projections[0]["entries"]) == 1
        assert projections[0]["entries"][0]["installment_number"] == 1
        assert projections[0]["entries"][0]["amount"] == 300.0

    def test_multi_installment_expense_has_correct_entries(self, client, user_id):
        client.post(f"/users/{user_id}/expenses", json={
            "name": "Notebook", "category": "tecnologia",
            "expense_value": 3000, "installment": 10,
            "start_month": 1, "start_year": 2026,
        })
        projections = client.get(f"/users/{user_id}/installments").json()["projections"]
        assert len(projections[0]["entries"]) == 10
        assert projections[0]["total_value"] == 3000.0
        assert projections[0]["installments"] == 10

    def test_projection_includes_expense_metadata(self, client, user_id):
        client.post(f"/users/{user_id}/expenses", json={
            "name": "Geladeira", "category": "casa",
            "expense_value": 2400, "installment": 12,
            "start_month": 6, "start_year": 2026,
        })
        proj = client.get(f"/users/{user_id}/installments").json()["projections"][0]
        assert proj["expense_name"] == "Geladeira"
        assert proj["category"] == "casa"
        assert proj["total_value"] == 2400.0
        assert proj["installments"] == 12

    def test_multiple_expenses_return_multiple_projections(self, client, user_id):
        client.post(f"/users/{user_id}/expenses", json={
            "name": "A", "expense_value": 100, "installment": 2,
            "start_month": 1, "start_year": 2026,
        })
        client.post(f"/users/{user_id}/expenses", json={
            "name": "B", "expense_value": 200, "installment": 3,
            "start_month": 3, "start_year": 2026,
        })
        projections = client.get(f"/users/{user_id}/installments").json()["projections"]
        assert len(projections) == 2
        names = {p["expense_name"] for p in projections}
        assert names == {"A", "B"}

    def test_nonexistent_user_returns_404(self, client):
        assert client.get("/users/9999/installments").status_code == 404
