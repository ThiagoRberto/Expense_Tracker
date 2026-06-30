class TestCreateUser:
    def test_create_round_trips_fields_and_entities(self, client, user_payload):
        data = client.post("/users/", json=user_payload).json()
        assert data["id"] is not None
        assert data["name"] == "Arthur"
        assert data["budget_ceiling"] == 2000
        assert len(data["incomes"]) == 1
        assert len(data["expenses"]) == 1
        assert len(data["bills"]) == 1
        assert len(data["investments"]) == 1

    def test_create_minimal_user_uses_defaults(self, client):
        data = client.post("/users/", json={"name": "Vazio", "password": "123"}).json()
        assert data["budget_ceiling"] is None
        assert data["incomes"] == []

    def test_create_does_not_expose_password(self, client, user_payload):
        assert "password" not in client.post("/users/", json=user_payload).json()


class TestListAndGetUser:
    def test_list_includes_created_user_with_relations(self, client, user_payload):
        client.post("/users/", json=user_payload)
        users = client.get("/users/").json()
        assert len(users) == 1
        assert len(users[0]["incomes"]) == 1

    def test_get_existing_user(self, client, user_payload):
        created_id = client.post("/users/", json=user_payload).json()["id"]
        data = client.get(f"/users/{created_id}").json()
        assert data["id"] == created_id
        assert data["bills"][0]["bill_value"] == 1200

    def test_get_nonexistent_user_returns_404(self, client):
        assert client.get("/users/9999").status_code == 404


class TestLogin:
    def test_login_valid_credentials(self, client, user_payload):
        client.post("/users/", json=user_payload)
        response = client.post("/users/login", json={"name": "Arthur", "password": "secret"})
        assert response.status_code == 200
        assert response.json()["name"] == "Arthur"

    def test_login_wrong_password_returns_401(self, client, user_payload):
        client.post("/users/", json=user_payload)
        response = client.post("/users/login", json={"name": "Arthur", "password": "errada"})
        assert response.status_code == 401


class TestUpdateUser:
    def test_patch_updates_budget_ceiling(self, client, user_payload):
        user_id = client.post("/users/", json=user_payload).json()["id"]
        response = client.patch(f"/users/{user_id}", json={"budget_ceiling": 3000})
        assert response.status_code == 200
        assert response.json()["budget_ceiling"] == 3000
