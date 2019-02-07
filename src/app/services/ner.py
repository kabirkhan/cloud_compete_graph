import os
from collections import defaultdict
import spacy
from src.app import labels
from src.app.exceptions import DocumentParseError


class CloudServiceExtractor:
    def __init__(self, blob_service, search_client):

        self.search_client = search_client
        # print("Downloading NER model...", end='')
        # self.blob_service = blob_service

        # for blob in blob_service.list_blobs('ner'):
        #     path = f'src/app/services/models/{blob.name}'   
        #     os.makedirs(os.path.dirname(path), exist_ok=True)
        #     self.blob_service.get_blob_to_path('ner', blob.name, file_path=str(path))
        # print('Done')

        print("Loading NER model...", end='')
        self.nlp = spacy.load('en_core_web_lg')
        print("Done")

        self.service_cache = {}

    def resolve_service_name(self, name, threshold=0.8):
    
        if name in self.service_cache:
            return self.service_cache[name]
        
        res = self.search_client.suggest(name)
        
        if res.status_code == 200:
            suggestion = res.json()['value'][0] if res.json()['value'] else name
            search_res = self.search_client.search(suggestion['@search.text'])
            top_res = search_res.json()['value'][0]
            if top_res['@search.score'] > threshold:                
                self.service_cache[name] = top_res
                return self.service_cache[name]
        else:
            print(res.text)
            return None

    def extract(self, text):
        try:
            doc = self.nlp(text)
        except ValueError:
            raise DocumentParseError


        for ent in doc.ents:
            if ent.label_ in (labels.AZURE_SERVICE, labels.AWS_SERVICE, labels.GCP_SERVICE):
                service = self.resolve_service_name(ent.text)
                yield ent, service
