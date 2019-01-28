import os
import re
import json

from dotenv import find_dotenv, load_dotenv
import click
import pandas as pd
from fuzzywuzzy import fuzz
import configparser
import requests
import pandas as pd

from src.data.cosmos import GremlinQueryManager, DocumentQueryManager
from src.data.graph.gremlin import GremlinQueryBuilder


def add_cloud(gremlin_qm, data_directory, cloud_abbr, cloud_name):
    """Add all categories and services for a cloud.
        1. Add cloud vertex
        2. Add cloud specific categories and link them up to the cloud vertex
        3. Add cloud specific services and link them to the appropriate category
    """
    print(f'Adding {cloud_name}')
    # 1
    q = GremlinQueryBuilder.build_upsert_vertex_query('cloud', {
        'name': cloud_name, 'abbreviation': cloud_abbr
    })
    res = gremlin_qm.query(q)
    cloud_id = res[0]['id']

    # 2
    services_df = pd.read_csv(f'{data_directory}/{cloud_abbr}_services.csv')
    services_df.fillna('', inplace=True)
    categories = list(services_df['category_name'].unique())
    
    for cat in categories:
        vq = GremlinQueryBuilder.build_upsert_vertex_query(
            f'{cloud_abbr}_category', {'name': cat}
        )
        v_id = gremlin_qm.query(vq)[0]['id']
        eq = GremlinQueryBuilder.build_upsert_edge_query(
            v_id, cloud_id, {'label': 'source_cloud'}
        )
        gremlin_qm.query(eq)

    # 3
    def add_service_and_edge(row):
        label = f'{cloud_abbr}_service'
        props = {
            'name': row['name'],
            'short_description': row['short_description'],
            'long_description': row['long_description'],
            'uri': row['link'],
            'icon_uri': row['icon']
        }
        for k, v in props.items():
            props[k] = GremlinQueryBuilder.gremlin_escape(v)
        vq = GremlinQueryBuilder.build_upsert_vertex_query(label, props)
        
        v_res = gremlin_qm.query(vq)    

        cat_name = row['category_name']
        q_res = gremlin_qm.query(
            f"g.V().has('name', '{cat_name}').has('label', '{cloud_abbr}_category')"
        )
        cat_id = q_res[0]['id']

        cat_eq = GremlinQueryBuilder.build_upsert_edge_query(
            v_res[0]['id'], cat_id, {'label': 'belongs_to'}
        )
        gremlin_qm.query(cat_eq)

    services_df.apply(add_service_and_edge, axis=1)

    return cloud_id, categories, services_df


def normalize_category_lists(a_cats: list, b_cats: list, ratio=75, normalized_cats={}):
    _normalized_cats = normalized_cats.copy()
    for a_cat in a_cats:
        for b_cat in b_cats:
            if fuzz.ratio(a_cat, b_cat) > ratio or a_cat in b_cat or b_cat in a_cat:
                if normalized_cats:
                    _normalized_cats[a_cat] = b_cat
                else:
                    if len(a_cat) < len(b_cat):
                        norm = b_cat
                    else:
                        norm = a_cat

                    _normalized_cats[b_cat] = norm
                    _normalized_cats[a_cat] = norm

    return _normalized_cats


def add_normalized_categories(gremlin_qm: GremlinQueryManager, normalized_cats: dict):
    """Add normalized super categories and create connections 
        from cloud specific categories. This will allow initial travsersals
        across the different cloud providers"""
    for text, norm in normalized_cats.items():
        category_res = gremlin_qm.query(
            f"g.V().has('name', '{norm}').has('label', 'category')"
        )
        if category_res:
            norm_category_id = category_res[0]['id']
        else:
            vq = GremlinQueryBuilder.build_upsert_vertex_query(
                'category', {'name': norm}
            )
            norm_category_id = gremlin_qm.query(vq)[0]['id']

        nodes = gremlin_qm.query(f"g.V().has('name', '{text}')")
        for node in nodes:        
            eq = GremlinQueryBuilder.build_upsert_edge_query(
                node['id'], norm_category_id, {'label': 'super_category'}
            )
            gremlin_qm.query(eq)


@click.command()
@click.argument('data_directory', type=click.Path())
def construct_base_graph(data_directory):
    """Constructs the base graph in a Cosmos DB Graph"""
    load_dotenv(find_dotenv())

    account_name = os.environ.get('COSMOS_ACCOUNT_NAME')
    db_name = os.environ.get('COSMOS_DB_NAME')
    graph_name = os.environ.get('COSMOS_GRAPH_NAME')
    master_key = os.environ.get('COSMOS_MASTER_KEY')

    gremlin_qm = GremlinQueryManager(account_name, master_key, db_name, graph_name)

    # 1. Add cloud nodes to graph
    clouds = {
        'aws': 'Amazon Web Services', 
        'azure': 'Microsoft Azure', 
        'gcp': 'Google Cloud'
    }

    cloud_categories = {}
    for cloud_abbr, cloud_name in clouds.items():
        _, cats, _ = add_cloud(gremlin_qm, data_directory, cloud_abbr, cloud_name)
        cloud_categories[cloud_abbr] = cats

    normalized_cats = normalize_category_lists(
        cloud_categories['aws'], cloud_categories['azure']
    )

    normalized_cats = normalize_category_lists(
        cloud_categories['gcp'], normalized_cats.values(),
        ratio=60, normalized_cats=normalized_cats
    )

    print('Normalized Categories: ')
    print(json.dumps(normalized_cats, indent=4))

    # Adding a couple obvious edge cases from Google Cloud
    normalized_cats['Cloud IAM'] = normalized_cats['Identity']
    normalized_cats['Cloud IOT Core'] = normalized_cats['Internet of Things']

    add_normalized_categories(gremlin_qm, normalized_cats)

if __name__ == '__main__':
    construct_base_graph()