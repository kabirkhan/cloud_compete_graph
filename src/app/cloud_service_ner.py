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

    async def resolve_service_name(self, name, threshold=0.8):
        """
        Resolve the name of the service from the 
        NER model to the search index
        """
        res = await self.search_client.suggest(name)

        try:
            res.raise_for_status()
            suggestion = res.json()["value"][0] if res.json()["value"] else name
            if isinstance(suggestion, str):
                search_res = await self.search_client.search(name)
            else:
                search_res = await self.search_client.search(suggestion["@search.text"])
            search_res.raise_for_status()
            top_res = search_res.json()["value"][0]
            return top_res
        except:
            print(f'Could not resolve: {name}')
            return None

    async def extract(self, text, ent_labels=[AWS_SERVICE, AZURE_SERVICE, GCP_SERVICE]):
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

        res = []

        for ent in filter(lambda w: w.ent_type_ in ent_labels, doc):
            service = await self.resolve_service_name(ent.text)
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
                        if cur.head == cur:
                            break
                        cur = cur.head

                ent_span = Span(
                    doc, ent.i, ent.i + 1, label=ent.ent_type
                )
                res.append((ent_span, service, relation, root_verb))

        return res
