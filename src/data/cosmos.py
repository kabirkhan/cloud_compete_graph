import concurrent.futures
from azure.cosmos.cosmos_client import CosmosClient
from gremlin_python.driver import client, serializer


class DocumentQueryManager:
    """Utitlity class for managing cosmos db client connection
    and collections for easy querying."""
    def __init__(self, account_name, master_key, db_name):
        self.client = CosmosClient('https://{}.documents.azure.com:443/'.format(account_name), {
            'masterKey': master_key
        })
        dbs = list(self.client.ReadDatabases())
        self.db = dbs[0]['_self']
        for d in dbs:
            if d['id'] == db_name:
                self.db = d['_self']

        self.collections = {}
        for c in list(self.client.ReadContainers(self.db)):
            self.collections[c['id']] = c['_self']


class GremlinQueryManager:
    def __init__(self, account_name, master_key, database_name, graph_name):
        
        self.client = client.Client(
            f'wss://{account_name}.gremlin.cosmosdb.azure.com:443/',
            'g',
            username=f'/dbs/{database_name}/colls/{graph_name}',
            password=master_key,
            message_serializer=serializer.GraphSONMessageSerializer()
        )

    def query(self, query):
        callback = self.client.submitAsync(query)
        if callback.result():
            res = []
            for r in callback.result():
                res += r
        return res
