import json
import os
from dotenv import find_dotenv, load_dotenv
from src.data.cosmos import GremlinQueryManager
from src.data.graph.gremlin import GremlinQueryBuilder
from src.data.search.azure_search import AzureSearchClient


def make_services_search_index(index_name):

    # Varibales
    load_dotenv(find_dotenv())
    account_name = os.getenv('COSMOS_ACCOUNT_NAME')
    db_name = os.getenv('COSMOS_DB_NAME')
    graph_name = os.getenv('COSMOS_GRAPH_NAME')
    master_key = os.getenv('COSMOS_MASTER_KEY')
    search_account_name = os.getenv("AZURE_SEARCH_ACCOUNT_NAME")
    search_api_key = os.getenv("AZURE_SEARCH_KEY")

    # Clients
    gremlin_qm = GremlinQueryManager(account_name, master_key, db_name, graph_name)
    search_client = AzureSearchClient(search_account_name, search_api_key, index_name)

    # Search Synonyms
    azure_synonyms = """
    AD, Active Directory, AAD\n
    AKS, Azure Kubernetes Service\n,
    function, functions
    database, databases
    """
    search_client.upsert_synonym_map('azure-service-abbreviations', azure_synonyms).text
    print('Created Azure Synonym Map')

    # Services Search Index
    services_field_config = [
        {"name": "id", "type": "Edm.String", "key": True, "searchable": False, "sortable": False, "facetable": False},
        {"name": "name", "type": "Edm.String", "synonymMaps":["azure-service-abbreviations"]},
        {"name": "shortDescription", "type": "Edm.String", "filterable": False, "sortable": False, "facetable": False},
        {"name": "longDescription", "type": "Edm.String", "filterable": False, "sortable": False, "facetable": False},
        {"name": "uri", "type": "Edm.String", "facetable": False},
        {"name": "iconUri", "type": "Edm.String", "facetable": False},
        {
            "name": "categories", "type": "Collection(Edm.ComplexType)", "fields": [
                {"name": "id", "type": "Edm.String", "searchable": False, "filterable": False, "sortable": False, "facetable": False},
                {"name": "name", "type": "Edm.String", "searchable": True, "filterable": False, "sortable": False, "facetable": False}
            ]
        },
        {
            "name": "relatedServices", "type": "Collection(Edm.ComplexType)", "fields": [
                {"name": "id", "type": "Edm.String", "searchable": False, "filterable": False, "sortable": False, "facetable": False},
                {"name": "name", "type": "Edm.String", "searchable": True, "filterable": False, "sortable": False, "facetable": False}
            ]
        },
        {
            "name": "cloud", "type": "Edm.ComplexType", "fields": [
                {"name": "id", "type": "Edm.String", "searchable": False, "filterable": False, "sortable": False, "facetable": False},
                {"name": "name", "type": "Edm.String", "searchable": True, "filterable": False, "sortable": False, "facetable": False}
            ]
        }
    ]

    suggesters = [  
        {  
            "name": "suggest-name",  
            "searchMode": "analyzingInfixMatching",  
            "sourceFields": ["name"]
        }  
    ]

    scoring_profiles = [  
        {  
            "name": "boostName",  
            "text": {  
                "weights": {  
                "name": 3          
                }  
            }  
        }
    ]

    search_client.upsert_index(services_field_config, suggesters, scoring_profiles)
    print('Created Services Search Index')

    # Upload Services Data to Search Index
    services_data = []

    abbrs = gremlin_qm.query('g.V().has("label", "cloud").values("abbreviation")')
    for abbr in abbrs:
        q = f"""g.V().has("label", "{abbr}_service")
                .project("id", "name", "shortDescription", "longDescription", "uri", "iconUri", "categories", "relatedServices", "cloud")
                .by("id").by("name").by("short_description").by("long_description").by("uri").by("icon_uri")
                .by(out("belongs_to").project("id", "name").by(values("id")).by(values("name")).fold())
                .by(coalesce(out("related_service").project("id", "name").by(values("id")).by(values("name")).fold(), __.not(identity()).fold()))
                .by(out("belongs_to").out("source_cloud").project("id", "name").by(values("id")).by(values("name")))"""
        cloud_data = gremlin_qm.query(q)
        services_data += cloud_data
    
    for s in services_data:
        if s['name'] == 'Azure Functions':
            print(json.dumps(s, indent=4))
    search_client.upload_data(services_data)
    print('Uploaded Services Data from Graph To Azure Search')


if __name__ == '__main__':
    make_services_search_index('services')