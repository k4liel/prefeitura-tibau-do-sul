from django.test import Client


def test_healthcheck_ok():
    client = Client()
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_schema_endpoint_ok():
    client = Client()
    response = client.get("/api/schema/")
    assert response.status_code == 200
