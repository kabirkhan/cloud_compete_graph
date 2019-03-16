import json
from starlette.testclient import TestClient
from src.app.api import app


def test_api_validation_error():
    client = TestClient(app)
    response = client.post("extract")
    assert response.status_code == 422


def test_documents_api_success():
    client = TestClient(app)

    with open("src/app/tests/data/request_body.json") as request_body_file:
        request_body = json.load(request_body_file)

    response = client.post("extract", json=request_body)
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    for doc in data["documents"]:
        assert "id" in doc
        assert "cloudServices" in doc
        for s in doc["cloudServices"]:
            for k in ["serviceName", "serviceShortDescription", "serviceUri"]:
                assert isinstance(s[k], str)
            for k in ["serviceCategories", "relatedServices", "matches"]:
                assert isinstance(s[k], list)


def test_azure_cognitive_search_success():
    client = TestClient(app)

    request_body = {
        "values": [
            {
                "recordId": "a1",
                "data": {
                    "text": "Create serverless logic with Azure Functions",
                    "language": "en",
                },
            }
        ]
    }
    response = client.post("azure_cognitive_search", json=request_body)
    assert response.status_code == 200
    data = response.json()
    assert "values" in data
    for doc in data["values"]:
        assert "recordId" in doc
        assert "cloudServices" in doc["data"]
