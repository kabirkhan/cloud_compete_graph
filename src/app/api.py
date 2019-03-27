import os
import multiprocessing as mp
import asyncio
from typing import List

from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from src.app.exceptions import DocumentParseError
from src.app.cloud_service_ner import CloudServiceExtractor
from src.app.models import (
    DocumentRequest,
    DocumentsRequest,
    DocumentResponse,
    DocumentsResponse,
    AzureSearchDocumentsRequest,
    AzureSearchDocumentsResponse,
)
from src.data.search.azure_search import AzureSearchClient


load_dotenv(find_dotenv())

search_account_name = os.environ.get("AZURE_SEARCH_ACCOUNT_NAME")
search_api_key = os.environ.get("AZURE_SEARCH_KEY")
prefix = os.environ.get("CLUSTER_ROUTE_PREFIX")

if not prefix:
    prefix = ""
prefix = prefix.rstrip("/")

search_client = AzureSearchClient(search_account_name, search_api_key, 'services')
cse = CloudServiceExtractor(search_client)


app = FastAPI(
    title="Cloud Compete Graph NER",
    description="API for the Cloud Compete Graph Named Entity Recognition models",
    version="1.0.0",
    openapi_prefix=prefix,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def extract_from_text(text: str):
    """Extract Cloud Services from raw text"""
    cloud_services = {}
    for ent, service, relation, root_verb in await cse.extract(text):
        if service["id"] not in cloud_services:
            cloud_services[service["id"]] = {
                "serviceId": service["id"],
                "serviceName": service["name"],
                "serviceShortDescription": service["shortDescription"],
                "serviceLongDescription": service["longDescription"],
                "serviceUri": service["uri"],
                "serviceIconUri": service["iconUri"],
                "serviceCloud": service["cloud"],
                "serviceCategories": service["categories"],
                "relatedServices": service["relatedServices"],
                "matches": [],
            }
        match = {
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
        }
        if relation:
            match["relation"] = relation.text
        if root_verb:
            match["rootVerb"] = root_verb.lemma_
        cloud_services[service["id"]]["matches"].append(match)
    return list(cloud_services.values())


async def extract_from_doc(doc):
    cloud_services = await extract_from_text(doc.text)
    return {
        'id': doc.id,
        'cloudServices': cloud_services
    }


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url=f"{prefix}/docs")


@app.post("/extract", response_model=DocumentsResponse, tags=["NER"])
async def extract(body: DocumentsRequest):
    """
    Example:
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
    results = []
    for doc in body.documents:
        result = extract_from_doc(doc)
        results.append(result)
    
    documents_res = await asyncio.gather(*results)
    
    return {"documents": documents_res}


@app.post(
    "/azure_cognitive_search",
    response_model=AzureSearchDocumentsResponse,
    tags=["NER", "Azure Search"],
)
def extract_for_azure_search(body: AzureSearchDocumentsRequest):
    """Extract Cloud Services for each document in an Azure Search Index.
    This route can be configured directly as a Cognitive Skill in Azure Search"""

    values_res = []
    for val in body.values:
        cloud_services = [c["serviceName"] for c in extract_from_text(val.data.text)]
        values_res.append(
            {"recordId": val.recordId, "data": {"cloudServices": cloud_services}}
        )
    return {"values": values_res}
