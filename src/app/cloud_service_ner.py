import os
from collections import defaultdict
import spacy

from src.app.exceptions import DocumentParseError
from src.app.labels import AWS_SERVICE, AZURE_SERVICE, GCP_SERVICE


class CloudServiceExtractor:
    def __init__(self, search_client):

        self.search_client = search_client

        print("Loading NER model...", end='')
        self.nlp = spacy.load('en_ner_azure')
        print("Done")

        self.service_cache = {}

    def resolve_service_name(self, name, threshold=0.8):
        """
        Resolve the name of the service from the 
        NER model to the search index
        """
        if name in self.service_cache:
            return self.service_cache[name]
        
        res = self.search_client.suggest(name)
        
        if res.status_code == 200:
            suggestion = res.json()['value'][0] if res.json()['value'] else name
            if isinstance(suggestion, str):
                search_res = self.search_client.search(name)
            else:
                search_res = self.search_client.search(suggestion['@search.text'])
            top_res = search_res.json()['value'][0]
            if top_res['@search.score'] > threshold:                
                self.service_cache[name] = top_res
                return self.service_cache[name]
        else:
            print(res.text)
            return None

    def extract(self, text):
        """
        Extract Named entities
        """
        try:
            doc = self.nlp(text)
        except ValueError:
            raise DocumentParseError

        for ent in doc.ents:
            if ent.label_ in [AWS_SERVICE, AZURE_SERVICE, GCP_SERVICE]:
                service = self.resolve_service_name(ent.text)
                yield ent, service
