import os
import requests
import requests_cache
from datetime import timedelta
from dotenv import find_dotenv, load_dotenv


requests_cache.install_cache('cloud_service_ner_search', expire_after=timedelta(days=1))


class AzureSearchClient:
    def __init__(self, account_name, api_key, index_name):
        self.account_name = account_name
        self.api_key = api_key
        self.index_name = index_name
        self.default_headers = {
            'api-key': api_key
        }
                
    async def search(self, search_term, userSkills=None, k=10):
        search_url = f'https://{self.account_name}.search.windows.net/indexes/{self.index_name}/docs'

        params = {
            'api-version': '2017-11-11-preview',
            'search': search_term,
            '$top': k
        }
        
        if userSkills:
            params['scoringProfile'] = 'skills'
            params['scoringParameter'] = f'skills-{userSkills}'

        res = requests.get(search_url, headers=self.default_headers, params=params)
        return res

    async def suggest(self, search_term):
        search_url = f'https://{self.account_name}.search.windows.net/indexes/{self.index_name}/docs/suggest'
        params = {
            'api-version': '2017-11-11-preview',
            'search': search_term,
            '$top': 3,
            'scoringProfile': 'boostName',
            'autocompleteMode': 'twoTerms',
            'suggesterName': 'suggest-name',
            'fuzzy': True
        }
        res = requests.get(search_url, headers=self.default_headers, params=params)
        return res
        
    def upsert_index(self, fields_config, suggesters, scoring_profiles):
        kwargs = {
            'headers': self.default_headers,
            'json': {
                'name': self.index_name,
                'fields': fields_config,
                'suggesters': suggesters,
                'scoringProfiles': scoring_profiles
            }
        }
        delete_res = requests.delete(f"https://{self.account_name}.search.windows.net/indexes/{self.index_name}?api-version=2017-11-11", **kwargs)
        if delete_res.status_code > 299:
            print('Failed delete index')
        res = requests.post(
            f"https://{self.account_name}.search.windows.net/indexes/?api-version=2017-11-11",
            **kwargs
        )
        return res
    
    def upload_data(self, data):
        for i in range(len(data)):
            data[i]['@search.action'] = 'mergeOrUpload'
        res = requests.post(
            f"https://{self.account_name}.search.windows.net/indexes/{self.index_name}/docs/index?api-version=2017-11-11",
            headers=self.default_headers,
            json={
                'value': data
            }
        )
        return res
    
    def upsert_synonym_map(self, name, synonyms):
        kwargs = {
            'headers': self.default_headers,
            'json': {
                'name': name,
                'format': 'solr',
                'synonyms': synonyms
            }
        }

        res = requests.post(
            f"https://{self.account_name}.search.windows.net/synonymmaps?api-version=2017-11-11",
            **kwargs
        )
        if res.status_code > 299:
            res = requests.put(
                f"https://{self.account_name}.search.windows.net/synonymmaps/{name}?api-version=2017-11-11",
                **kwargs
            )
            
        return res
