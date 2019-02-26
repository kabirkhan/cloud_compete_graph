import os

from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from src.app.exceptions import DocumentParseError
from src.app.cloud_service_ner import CloudServiceExtractor
from src.app.models import DocumentsRequest, DocumentsResponse
from src.data.search.azure_search import AzureSearchClient


load_dotenv(find_dotenv())

search_account_name = os.environ.get("AZURE_ACCOUNT_NAME")
search_api_key = os.environ.get("AZURE_SEARCH_KEY")
prefix = os.environ.get("CLUSTER_ROUTE_PREFIX")

if not prefix:
    prefix = ""
prefix = prefix.rstrip("/")

search_client = AzureSearchClient(search_account_name, search_api_key)
cse = CloudServiceExtractor(search_client)


app = FastAPI(
    title="Cloud Compete Graph NER",
    description="API for the Cloud Compete Graph Named Entity Recognition models",
    version="0.1.0",
    openapi_prefix=prefix,
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url=f"{prefix}/docs")


@app.post(
    "/extract", response_model=DocumentsResponse, tags=["Named Entity Recognition"]
)
def extract(body: DocumentsRequest):
    """
    {
        "documents": [
            {
                "id": "1",
                "text": "Create serverless logic with Azure Functions",
                "language": "en"
            }
        ]
    }
    """
    documents_res = []
    for doc in body.documents:
        cloud_services = {}
        for ent, service in cse.extract(doc.text):
            if service["id"] not in cloud_services:
                cloud_services[service["id"]] = {
                    "serviceId": service["id"],
                    "serviceName": service["name"],
                    "serviceShortDescription": service["shortDescription"],
                    "serviceUri": service["uri"],
                    "serviceCategories": service["categories"],
                    "relatedServices": service["relatedServices"],
                    "matches": [],
                }
            cloud_services[service["id"]]["matches"].append(
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                }
            )

        documents_res.append(
            {"id": doc.id, "cloudServices": list(cloud_services.values())}
        )
    return {"documents": documents_res}
