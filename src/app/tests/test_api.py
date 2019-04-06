import os
import json
import time
from starlette.testclient import TestClient
from src.app.api import app
from src.app.examples import load_examples
from src.app.models import AsyncStatus, RuntimeEnvironment


os.environ["RUNTIME_ENVIRONMENT"] = RuntimeEnvironment.TESTING


def validate_documents_response(data):
    assert "documents" in data
    for doc in data["documents"]:
        assert "id" in doc
        assert "cloudServices" in doc
        for s in doc["cloudServices"]:
            for k in ["serviceName", "serviceShortDescription", "serviceUri"]:
                assert isinstance(s[k], str)
            for k in ["serviceCategories", "relatedServices", "matches"]:
                assert isinstance(s[k], list)


def test_api_validation_error():
    client = TestClient(app)
    response = client.post("extract")
    assert response.status_code == 422


def test_documents_api_success():
    client = TestClient(app)

    batch_request, _ = load_examples()

    response = client.post("extract", json=batch_request)
    assert response.status_code == 200
    data = response.json()
    validate_documents_response(data)


def test_extract_async():
    client = TestClient(app)

    batch_request, _ = load_examples()

    response = client.post("extract_async", json=batch_request)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == AsyncStatus.Running
    request_id = data["request_id"]

    time.sleep(4)

    response = client.get("status", params={"request_id": request_id})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == AsyncStatus.Completed
    validate_documents_response(data["result"])


def test_azure_cognitive_search_success():
    client = TestClient(app)

    _, az_req_body = load_examples()
    response = client.post("azure_cognitive_search", json=az_req_body)
    assert response.status_code == 200
    data = response.json()
    assert "values" in data
    for doc in data["values"]:
        assert "recordId" in doc
        assert "cloudServices" in doc["data"]
        for c in doc["data"]["cloudServices"]:
            assert isinstance(c, str)
