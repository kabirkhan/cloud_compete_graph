from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Schema


class RuntimeEnvironment(str, Enum):
    PRODUCTION = "PRODUCTION"
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"


class DocumentRequest(BaseModel):
    id: str
    text: str
    language: str = "en"


class DocumentsRequest(BaseModel):
    documents: List[DocumentRequest]


class EntityMatch(BaseModel):
    label: str
    text: str
    start: int
    end: int
    relation: Optional[str] = None
    rootVerb: Optional[str] = None


class CloudServiceEntity(BaseModel):
    matches: List[EntityMatch]
    serviceId: str
    serviceName: str
    serviceShortDescription: str
    serviceLongDescription: str
    serviceUri: str
    serviceIconUri: str
    serviceCloud: str
    serviceCategories: List[str]
    relatedServices: List[str]


class DocumentResponse(BaseModel):
    id: str
    cloudServices: List[CloudServiceEntity]


class DocumentsResponse(BaseModel):
    documents: List[DocumentResponse]


class AsyncStatus(str, Enum):
    Completed = 'Completed'
    Running = 'Running'
    Failed = 'Failed'


class AsyncStatusDocumentsResponse(BaseModel):
    request_id: str
    status: AsyncStatus
    result: Optional[DocumentsResponse]


# Azure Search Cognitive Skills Models
class AzureSearchDocumentDataRequest(BaseModel):
    text: str
    language: str = "en"


class AzureSearchDocumentRequest(BaseModel):
    recordId: str
    data: AzureSearchDocumentDataRequest


class AzureSearchDocumentsRequest(BaseModel):
    values: List[AzureSearchDocumentRequest]


class AzureSearchDocumentDataResponse(BaseModel):
    cloudServices: List[str]


class AzureSearchDocumentResponse(BaseModel):
    recordId: str
    data: AzureSearchDocumentDataResponse
    errors: Optional[List[str]]
    warnings: Optional[List[str]]


class AzureSearchDocumentsResponse(BaseModel):
    values: List[AzureSearchDocumentResponse]
