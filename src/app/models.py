from typing import List, Optional
from pydantic import BaseModel, Schema


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


class EntityRequest(BaseModel):
    text: str