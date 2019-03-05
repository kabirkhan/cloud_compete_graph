import os
from typing import List
from collections import defaultdict
import spacy
from spacy.tokens import Span

from src.app.exceptions import DocumentParseError
from src.app.labels import AWS_SERVICE, AZURE_SERVICE, GCP_SERVICE


class CloudServiceExtractor:
    def __init__(self, search_client):

        self.search_client = search_client

        print("Loading NER model...", end="")
        self.nlp = spacy.load("en_ner_azure_lg")
        print("Done")

    def resolve_service_name(self, name, threshold=0.8):
        """
        Resolve the name of the service from the 
        NER model to the search index
        """
        res = self.search_client.suggest(name)

        if res.status_code == 200:
            suggestion = res.json()["value"][0] if res.json()["value"] else name
            if isinstance(suggestion, str):
                search_res = self.search_client.search(name)
            else:
                search_res = self.search_client.search(suggestion["@search.text"])
            top_res = search_res.json()["value"][0]
            return top_res
        else:
            print(res.text)
            return None

    def extract(self, text, ent_labels=[AWS_SERVICE, AZURE_SERVICE, GCP_SERVICE]):
        """
        Extract Named Entity Cloud services and relationships in text
        """
        try:
            doc = self.nlp(text)
        except ValueError:
            raise DocumentParseError

        spans = list(doc.ents) + list(doc.noun_chunks)
        for span in spans:
            span.merge()

        for ent in filter(lambda w: w.ent_type_ in ent_labels, doc):
            service = self.resolve_service_name(ent.text)
            if service:
                relation = None
                root_verb = None

                if ent.dep_ in ("attr", "dobj"):
                    subject = [w for w in ent.head.lefts if w.dep_ == "nsubj"]
                    if subject:
                        subject = subject[0]
                        relation = subject

                elif ent.dep_ == "pobj" and ent.head.dep_ == "prep":
                    relation = ent.head.head
                    cur = relation
                    while cur.head:
                        if cur.pos_ == "VERB":
                            root_verb = cur
                            break
                        else:
                            cur = cur.head
                
                yield Span(doc, ent.i, ent.i + 1, label=ent.ent_type), service, relation, root_verb
