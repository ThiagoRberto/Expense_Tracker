class TestCreateUser:
    def test_create_user_returns_id(self, client, user_payload):
        response = client.post("/users/", json=user_payload)
        assert response.status_code == 200
        assert response.json()["id"] is not None

    def test_create_user_name_persisted(self, client, user_payload):
        response = client.post("/users/", json=user_payload)
        assert response.json()["name"] == "Arthur"

    def test_create_user_budget_ceiling_persisted(self, client, user_payload):
        response = client.post("/users/", json=user_payload)
        assert response.json()["budget_ceiling"] == 2000

    def test_create_user_has_income(self, client, user_payload):
        response = client.post("/users/", json=user_payload)
        incomes = response.json()["incomes"]
        assert len(incomes) == 1
        assert incomes[0]["name"] == "Salário"
        assert incomes[0]["income_value"] == 5000

    def test_create_user_has_expense_with_installments(self, client, user_payload):
        response = client.post("/users/", json=user_payload)
        expenses = response.json()["expenses"]
        assert len(expenses) == 1
        assert expenses[0]["installment"] == 10

    def test_create_user_has_bill(self, client, user_payload):
        response = client.post("/users/", json=user_payload)
        bills = response.json()["bills"]
        assert len(bills) == 1
        assert bills[0]["bill_value"] == 1200

    def test_create_user_has_investment_with_dividends(self, client, user_payload):
        response = client.post("/users/", json=user_payload)
        investments = response.json()["investments"]
        assert len(investments) == 1
        assert investments[0]["dividends"] == 500

    def test_create_user_with_empty_lists(self, client):
        response = client.post("/users/", json={"name": "Vazio", "password": "123"})
        assert response.status_code == 200
        data = response.json()
        assert data["incomes"] == []
        assert data["expenses"] == []
        assert data["bills"] == []
        assert data["investments"] == []

    def test_create_user_without_budget_ceiling(self, client):
        response = client.post("/users/", json={"name": "Sem teto", "password": "123"})
        assert response.json()["budget_ceiling"] is None

    def test_create_user_with_multiple_incomes(self, client):
        payload = {
            "name": "Multi",
            "password": "123",
            "incomes": [
                {"name": "Salário", "income_value": 4000},
                {"name": "Freelance", "income_value": 1500},
            ],
        }
        response = client.post("/users/", json=payload)
        assert response.status_code == 200
        assert len(response.json()["incomes"]) == 2

    def test_create_user_with_multiple_expenses(self, client):
        payload = {
            "name": "Multi",
            "password": "123",
            "expenses": [
                {"name": "Celular", "expense_value": 1200, "installment": 12},
                {"name": "TV", "expense_value": 3000, "installment": 6},
            ],
        }
        response = client.post("/users/", json=payload)
        assert len(response.json()["expenses"]) == 2


class TestListUsers:
    def test_empty_database_returns_empty_list(self, client):
        response = client.get("/users/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_after_one_creation(self, client, user_payload):
        client.post("/users/", json=user_payload)
        response = client.get("/users/")
        assert len(response.json()) == 1

    def test_list_multiple_users(self, client, user_payload):
        client.post("/users/", json=user_payload)
        client.post("/users/", json={**user_payload, "name": "Outro"})
        response = client.get("/users/")
        assert len(response.json()) == 2

    def test_list_includes_related_entities(self, client, user_payload):
        client.post("/users/", json=user_payload)
        users = client.get("/users/").json()
        assert len(users[0]["incomes"]) == 1
        assert len(users[0]["bills"]) == 1


class TestGetUser:
    def test_get_existing_user(self, client, user_payload):
        created_id = client.post("/users/", json=user_payload).json()["id"]
        response = client.get(f"/users/{created_id}")
        assert response.status_code == 200
        assert response.json()["id"] == created_id

    def test_get_user_data_integrity(self, client, user_payload):
        created_id = client.post("/users/", json=user_payload).json()["id"]
        fetched = client.get(f"/users/{created_id}").json()
        assert fetched["bills"][0]["bill_value"] == 1200
        assert fetched["investments"][0]["dividends"] == 500
        assert fetched["expenses"][0]["installment"] == 10

    def test_get_nonexistent_user_returns_404(self, client):
        response = client.get("/users/9999")
        assert response.status_code == 404

    def test_get_user_id_zero_returns_404(self, client):
        response = client.get("/users/0")
        assert response.status_code == 404


class TestLoginUser:
    def test_login_returns_user_on_valid_credentials(self, client, user_payload):
        client.post("/users/", json=user_payload)
        response = client.post("/users/login", json={"name": "Arthur", "password": "secret"})
        assert response.status_code == 200
        assert response.json()["name"] == "Arthur"

    def test_login_includes_related_entities(self, client, user_payload):
        client.post("/users/", json=user_payload)
        data = client.post("/users/login", json={"name": "Arthur", "password": "secret"}).json()
        assert len(data["incomes"]) == 1
        assert len(data["bills"]) == 1

    def test_login_wrong_password_returns_401(self, client, user_payload):
        client.post("/users/", json=user_payload)
        response = client.post("/users/login", json={"name": "Arthur", "password": "errada"})
        assert response.status_code == 401

    def test_login_unknown_name_returns_401(self, client):
        response = client.post("/users/login", json={"name": "Ninguem", "password": "abc"})
        assert response.status_code == 401

    def test_login_does_not_expose_password(self, client, user_payload):
        client.post("/users/", json=user_payload)
        data = client.post("/users/login", json={"name": "Arthur", "password": "secret"}).json()
        assert "password" not in data


class TestUpdateUser:
    def test_patch_sets_budget_ceiling(self, client, user_payload):
        user_id = client.post("/users/", json=user_payload).json()["id"]
        response = client.patch(f"/users/{user_id}", json={"budget_ceiling": 3000})
        assert response.status_code == 200
        assert response.json()["budget_ceiling"] == 3000

    def test_patch_clears_budget_ceiling_when_null(self, client, user_payload):
        user_id = client.post("/users/", json=user_payload).json()["id"]
        response = client.patch(f"/users/{user_id}", json={"budget_ceiling": None})
        assert response.status_code == 200
        assert response.json()["budget_ceiling"] is None

    def test_patch_nonexistent_user_returns_404(self, client):
        response = client.patch("/users/9999", json={"budget_ceiling": 1000})
        assert response.status_code == 404
