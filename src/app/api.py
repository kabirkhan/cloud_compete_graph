import os

import hug
import falcon
from dotenv import load_dotenv, find_dotenv
from src.data.cosmos import DocumentQueryManager, GremlinQueryManager
from src.data.graph.gremlin import GremlinQueryBuilder


load_dotenv(find_dotenv())

account_name = os.environ.get('COSMOS_ACCOUNT_NAME')
db_name = os.environ.get('COSMOS_DB_NAME')
graph_name = os.environ.get('COSMOS_GRAPH_NAME')
master_key = os.environ.get('COSMOS_MASTER_KEY')

gremlin_qm = GremlinQueryManager(account_name, master_key, db_name, graph_name)


def get_value(res, k):
    if k in res['properties']:
        if len(res['properties'][k]) == 1:
            return res['properties'][k]['value']


@hug.get('/clouds')
def get_clouds(cloud_id=None):
    project_str = '.project("id", "name", "abbreviation").by("id").by("name").by("abbreviation")'
    if cloud_id:
        q = f'g.V("{cloud_id}"){project_str}'
    
        res = gremlin_qm.query(q)[0]
    else:
        q = f'g.V().has("label", "cloud"){project_str}'
        res = gremlin_qm.query(q)

    return res
    # return {
    #     'id': res['id'],
    #     'name': get_value(res, 'name'),
    #     'abbreviation': get_value(res, 'abbreviation')
    # }


@hug.get('/categories')
def get_categories(cloud_id=None):

    if cloud_id:
        project_str = GremlinQueryBuilder.build_project_clause(['id', 'label', 'name'])
        q = f'g.V("{cloud_id}").in("source_cloud"){project_str}'
    else:
        q = 'g.V().has("label", "category")'

    print(q)

    res = gremlin_qm.query(q)
    return res


@hug.get('/categories/{category_id}/services')
def get_services(category_id):
    project_str = GremlinQueryBuilder.build_project_clause([
        'id', 'label', 'name', 'short_description', 'long_description', 'uri', 'icon_uri'
    ])
    q = f"g.V('{category_id}').in('belongs_to'){project_str}"
    res = gremlin_qm.query(q)
    return res


@hug.get('/services/{service_id}')
def get_related_services(service_id):
    q = f"""g.V("{service_id}")
            .project(
                "id", "label", "name", "short_description",
                "long_description", "uri", "icon_uri", "related_services"
            ).by("id").by("label").by("name").by("short_description")
             .by("long_description").by("uri").by("icon_uri")
             .by(out("related_service"))"""
    
    res = gremlin_qm.query(q)
    print(res)
    res[0]['related_services'] = [{'id': res[0]['related_services']['id']}]
    
    return res[0]


@hug.post('/gremlin')
def run_gremlin_query(query, response):
    q = GremlinQueryBuilder.gremlin_escape(query)
    if 'drop' in q or 'add' in q:
        response.status = falcon.HTTP_400
        return "No `drop` or `add` queries are allowed, only traversals."
    else:
        res = gremlin_qm.query(q)
        print(res, q)
        return res
