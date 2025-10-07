from rest_framework.test import APIClient


def test_healthz_ok(db: None) -> None:
    client = APIClient()
    res = client.get("/healthz/")
    assert res.status_code == 200
    data = res.json()
    assert data.get("ok") is True
