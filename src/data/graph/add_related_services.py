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


def get_svc_id(gremlin_qm, svc_name):
        q = f'g.V().has("name", "{svc_name}").project("id", "relatedServices").by("id").by(out("related_service").fold())'
        res = gremlin_qm.query(q)
        return res[0]['id'], [s['id'] for s in res[0]['relatedServices']]


def build_related_query(from_id, to_id, score):
    return GremlinQueryBuilder.build_upsert_edge_query(from_id, to_id, {
        'label': 'related_service', 'related_service_score': score
    })


@click.command()
@click.argument('data_matching_output_filepath', type=click.Path())
def add_related_services(data_matching_output_filepath):
    """Uses the output of the prodigy dedupe annotation task to add related_service
        edges to the graph.
        In practice this yields low-level relationships in the graph like
        AWS Lambda -> Azure Functions -> Google Cloud Functions"""


    load_dotenv(find_dotenv())

    account_name = os.environ.get('COSMOS_ACCOUNT_NAME')
    db_name = os.environ.get('COSMOS_DB_NAME')
    graph_name = os.environ.get('COSMOS_GRAPH_NAME')
    master_key = os.environ.get('COSMOS_MASTER_KEY')

    gremlin_qm = GremlinQueryManager(account_name, master_key, db_name, graph_name)

    df = pd.read_csv(data_matching_output_filepath)
    related_df = df[df['Link Score'] > 0.6].sort_values(['Cluster ID', 'source file'])

    for i in range(list(related_df['Cluster ID'])[-1] + 1):
        related_services = related_df[related_df['Cluster ID'] == i].reset_index(drop=True)
        try:
            cloud_a_svc = related_services.iloc[0]
            cloud_b_svc = related_services.iloc[1]
        except:
            continue
        
        cloud_a_id, cloud_a_related = get_svc_id(gremlin_qm, cloud_a_svc['name'])
        cloud_b_id, cloud_b_related = get_svc_id(gremlin_qm, cloud_b_svc['name'])

        print(cloud_b_related, cloud_b_related)
        
        print(f'Adding related_service edges between {cloud_a_svc["name"]} and {cloud_b_svc["name"]}')
        gremlin_qm.query(build_related_query(cloud_a_id, cloud_b_id, cloud_a_svc['Link Score']))
        gremlin_qm.query(build_related_query(cloud_b_id, cloud_a_id, cloud_a_svc['Link Score']))

        for rs_id in cloud_a_related:
            if rs_id != cloud_b_id:
                print('adding to related', rs_id, cloud_b_id)
                gremlin_qm.query(build_related_query(rs_id, cloud_b_id, cloud_a_svc['Link Score']))
        
        for rs_id in cloud_b_related:
            if rs_id != cloud_a_id:
                print('adding to related', rs_id, cloud_a_id)
                gremlin_qm.query(build_related_query(rs_id, cloud_a_id, cloud_a_svc['Link Score']))


if __name__ == '__main__':
    add_related_services()