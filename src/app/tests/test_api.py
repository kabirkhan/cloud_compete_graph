import json
from starlette.testclient import TestClient
from src.app.api import app


def test_api_validation_error():
    client = TestClient(app)
    response = client.post('extract')
    assert response.status_code == 422


def test_api_success():
    client = TestClient(app)
    
    with open('src/app/tests/data/request_body.json') as request_body_file:
        request_body = json.load(request_body_file)
    with open('src/app/tests/data/response_body.json') as response_body_file:
        response_body = json.load(response_body_file)

    response = client.post('extract', json=request_body)
    assert response.status_code == 200
    assert 'documents' in response.json()

    assert response.json() == response_body
