def test_health_db_not_configured(api_client: object) -> None:
    response = api_client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"status": "not_configured"}


def test_progress_requires_auth(api_client: object) -> None:
    response = api_client.get("/v1/progress/plan")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."


def test_documents_requires_auth(api_client: object) -> None:
    response = api_client.get("/v1/documents")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."


def test_auth_config_reports_neon_provider(api_client: object) -> None:
    response = api_client.get("/v1/auth/config")
    assert response.status_code == 200
    assert response.json()["provider"] == "neon-auth"
