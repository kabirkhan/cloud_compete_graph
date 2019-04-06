import os
from typing import List
from collections import defaultdict
import spacy
from spacy.tokens import Span

from src.app.exceptions import DocumentParseError
from src.app.labels import LABELS


class CloudServiceExtractor:
    def __init__(self, search_client, model="en_ner_cloud_lg"):

        self.search_client = search_client

        print("Loading NER model...", end="")
        self.nlp = spacy.load(model)
        self.nlp.add_pipe(self.nlp.create_pipe("merge_entities"))
        print("Done")

    async def resolve_service_name(self, name, ent_label, threshold=0.8):
        """
        Resolve the name of the service from the 
        NER model to the search index
        """
        cloud_filter = f"cloud eq '{LABELS[ent_label]}'"

        search_params = {
            "queryType": "full",
            "searchFields": "name",
            "filter": cloud_filter,
        }
        try:
            search_res = await self.search_client.search(
                name, search_params=search_params
            )
            search_res.raise_for_status()
            top_res = search_res.json()["value"][0]
            return top_res
        except:
            print(f"Could not resolve: {name}")
            return None

    async def extract(self, text, ent_labels=list(LABELS.keys())):
        """
        Extract Named Entity Cloud services and relationships in text
        """
        try:
            doc = self.nlp(text)
        except ValueError:
            raise DocumentParseError

        res = []
        for ent in filter(lambda w: w.ent_type_ in ent_labels, doc):
            service = await self.resolve_service_name(ent.text, ent.ent_type_)
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

                ent_span = Span(doc, ent.i, ent.i + 1, label=ent.ent_type)
                res.append((ent_span, service, relation, root_verb))

        return res
