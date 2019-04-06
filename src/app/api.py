import json
import os
import multiprocessing as mp
import asyncio
from typing import List
import uuid

from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Body, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from redis import Redis

from src.app.exceptions import DocumentParseError
from src.app.cache import Cache
from src.app.cloud_service_ner import CloudServiceExtractor
from src.app.examples import load_examples
from src.app.models import (
    RuntimeEnvironment,
    DocumentRequest,
    DocumentsRequest,
    DocumentResponse,
    DocumentsResponse,
    AsyncStatusDocumentsResponse,
    AzureSearchDocumentsRequest,
    AzureSearchDocumentsResponse,
)
from src.data.search.azure_search import AzureSearchClient


load_dotenv(find_dotenv())

redis_host = os.getenv("AZURE_REDIS_HOST")
redis_key = os.getenv("AZURE_REDIS_KEY")
search_account_name = os.getenv("AZURE_SEARCH_ACCOUNT_NAME")
search_api_key = os.getenv("AZURE_SEARCH_KEY")
prefix = os.getenv("CLUSTER_ROUTE_PREFIX")
runtime_env = os.getenv("RUNTIME_ENVIRONMENT", RuntimeEnvironment.PRODUCTION)


if not prefix:
    prefix = ""
prefix = prefix.rstrip("/")

search_client = AzureSearchClient(search_account_name, search_api_key, "services")
cse = CloudServiceExtractor(search_client)
cache = Cache(redis_host, redis_key, testing=runtime_env == RuntimeEnvironment.TESTING)


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


batch_request, az_request = load_examples()


async def extract_from_text(text: str):
    """Extract Cloud Services from raw text"""
    request_id = hash(text)
    result = cache.get(request_id)

    if result:
        result = json.loads(result)
    else:
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

        result = list(cloud_services.values())
        cache.set(request_id, json.dumps(result))

    return result


async def extract_from_doc(doc):
    """Extract Cloud Services from a single Document"""
    cloud_services = await extract_from_text(doc.text)
    return {"id": doc.id, "cloudServices": cloud_services}


async def extract_from_docs_and_save(request_id, docs):
    """Extract Cloud Services from a batch of documents and cache the result"""

    results = []
    for doc in docs:
        result = extract_from_doc(doc)
        results.append(result)

    documents_res = await asyncio.gather(*results)
    cache.set(request_id, json.dumps(documents_res), expire_after=60 * 60 * 12)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url=f"{prefix}/docs")


@app.post("/extract", response_model=DocumentsResponse, tags=["NER"])
async def extract(body: DocumentsRequest = Body(..., example=batch_request)):
    """Extract Cloud Services for a batch document."""

    results = []
    for doc in body.documents:
        result = extract_from_doc(doc)
        results.append(result)

    documents_res = await asyncio.gather(*results)

    return {"documents": documents_res}


@app.post(
    "/extract_async", response_model=AsyncStatusDocumentsResponse, tags=["NER", "Async"]
)
async def extract_async(
    background_tasks: BackgroundTasks,
    body: DocumentsRequest = Body(..., example=batch_request),
):
    """Run extraction for batch of documents in the background"""

    request_id = str(uuid.uuid4())
    background_tasks.add_task(extract_from_docs_and_save, request_id, body.documents)

    return {"request_id": request_id, "status": "Running"}


@app.get("/status", response_model=AsyncStatusDocumentsResponse, tags=["NER", "Async"])
def request_status(request_id: str):
    """Get the status of an async extraction."""

    result = cache.get(request_id)
    if result:
        result = json.loads(result)
        return {
            "request_id": request_id,
            "status": "Completed",
            "result": {"documents": result},
        }
    else:
        return {"request_id": request_id, "status": "Running"}


@app.post(
    "/azure_cognitive_search",
    response_model=AzureSearchDocumentsResponse,
    tags=["NER", "Azure Search"],
)
async def extract_for_azure_search(
    body: AzureSearchDocumentsRequest = Body(..., example=az_request)
):
    """Extract Cloud Services for each document in an Azure Search Index.
    This route can be configured directly as a Cognitive Skill in Azure Search"""

    values_res = []
    for val in body.values:
        cloud_services = [
            c["serviceName"] for c in await extract_from_text(val.data.text)
        ]
        values_res.append(
            {"recordId": val.recordId, "data": {"cloudServices": cloud_services}}
        )
    return {"values": values_res}
