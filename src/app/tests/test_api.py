from starlette.testclient import TestClient
from src.app.api import app


def test_app():
    client = TestClient(app)
    response = client.post('extract')
    assert response.status_code == 422
