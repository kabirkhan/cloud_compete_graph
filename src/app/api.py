import os
import sys

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from marshmallow import Schema, fields, ValidationError

from starlette.applications import Starlette
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.schemas import OpenAPIResponse
from starlette_apispec import APISpecSchemaGenerator
import uvicorn
import yaml
from dotenv import load_dotenv, find_dotenv
from azure.storage.blob import BlockBlobService

from src.app.exceptions import DocumentParseError
from src.app.schemas import DocumentSchema, DocumentsSchema, DocumentServicesSchema, ServicesResponseSchema, MatchSchema, ServiceSchema
from src.app.services.ner import CloudServiceExtractor
from src.data.search.azure_search import AzureSearchClient


load_dotenv(find_dotenv())
search_account_name = os.environ.get('AZURE_SEARCH_ACCOUNT_NAME')
search_api_key = os.environ.get('AZURE_SEARCH_KEY')

blob_service = BlockBlobService('ccgmlmodels', sas_token='?sv=2018-03-28&ss=b&srt=sco&sp=rl&se=2020-02-01T02:59:06Z&st=2019-01-31T18:59:06Z&spr=https&sig=xNlhxlgrHmoKZj2eeHl7VdXLeH0LNJGwqcaLzW61oe4%3D')
search_client = AzureSearchClient(search_account_name, search_api_key)

cse = CloudServiceExtractor(blob_service, search_client)


app = Starlette(debug=True)
app.schema_generator = APISpecSchemaGenerator(
    APISpec(
        title="Cloud Compete Graph NER",
        version="1.0",
        openapi_version="3.0.0",
        info={"description": "API for the Cloud Compete Graph Named Entity Recognition models"},
        plugins=[MarshmallowPlugin()]
    )
)
app.schema_generator.spec.components.schema('DocumentSchema', schema=DocumentSchema)
app.schema_generator.spec.components.schema('ServicesResponseSchema', schema=ServicesResponseSchema)


@app.route('/extract', methods=["POST"])
async def homepage(request: Request):
    """
    summary: Extract cloud services from document text as Named Entities
    requestBody:
        description: List of documents
        required: true
        content:
          application/json:
            schema: DocumentsSchema
    responses:
      200:
        description: Cloud services extracted from text
        content:
          application/json:
            schema: ServicesResponseSchema
    """
    response = None
    try:
        body = await request.json()
        docsSchema = DocumentsSchema()
        docs = docsSchema.load(body)

        documents_res = []
        for doc in docs['documents']:
            cloud_services = {}
            for ent, service in cse.extract(doc['text']):
                if service['id'] not in cloud_services:
                    cloud_services[service['id']] = {
                        'serviceId': service['id'],
                        'serviceName': service['name'],
                        'serviceShortDescription': service['shortDescription'],
                        'serviceUri': service['uri'],
                        'serviceCategories': service['categories'],
                        'relatedServices': service['relatedServices'],
                        'matches': []
                    }
                cloud_services[service['id']]['matches'].append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            
            documents_res.append({
                'id': doc['id'],
                'cloudServices': list(cloud_services.values())
            })
            
        response = JSONResponse({'documents': documents_res})
    except ValidationError as e:
        print(e)
        response = JSONResponse(e.messages, status_code=400)
    except DocumentParseError as e:
        print(e)
        response = JSONResponse(
            {'message': 'Error parsing your documents. Make sure you remove special characters from all documents.'},
            status_code=400
        )
    except Exception as e:
        print(e)
        response = JSONResponse(
            {'message': 'Request failed for an unknown reason. Please try again later.'},
            status_code=500
        )

    return response


@app.route("/schema", methods=["GET"], include_in_schema=False)
def schema(request):
    return OpenAPIResponse(app.schema)


if __name__ == '__main__':
    assert sys.argv[-1] in ("run", "schema"), "Usage: example.py [run|schema]"

    if sys.argv[-1] == "run":
        uvicorn.run(app, host='0.0.0.0', port=8000, debug=True)
    elif sys.argv[-1] == "schema":
        print(yaml.dump(app.schema, default_flow_style=False))
