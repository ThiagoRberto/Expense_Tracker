import pytest


@pytest.fixture
def user_id(client):
    return client.post("/users/", json={"name": "Arthur", "password": "123"}).json()["id"]


class TestInstallmentsEndpoint:
    def test_projection_has_entries_and_metadata(self, client, user_id):
        client.post(f"/users/{user_id}/expenses", json={
            "name": "Notebook", "category": "tecnologia",
            "expense_value": 3000, "installment": 10,
            "start_month": 1, "start_year": 2026,
        })
        proj = client.get(f"/users/{user_id}/installments").json()["projections"][0]
        assert proj["expense_name"] == "Notebook"
        assert proj["total_value"] == 3000.0
        assert proj["installments"] == 10
        assert len(proj["entries"]) == 10

    def test_multiple_expenses_return_multiple_projections(self, client, user_id):
        client.post(f"/users/{user_id}/expenses", json={
            "name": "A", "expense_value": 100, "installment": 2, "start_month": 1, "start_year": 2026,
        })
        client.post(f"/users/{user_id}/expenses", json={
            "name": "B", "expense_value": 200, "installment": 3, "start_month": 3, "start_year": 2026,
        })
        projections = client.get(f"/users/{user_id}/installments").json()["projections"]
        assert {p["expense_name"] for p in projections} == {"A", "B"}
