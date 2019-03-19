import click
import pandas as pd
import requests
from tqdm import tqdm
from src.data.cloud._constants import Cloud


def get_normalized_cat_name(abbr, cat_name):
    query_url = 'https://cloudconceptgraph.azure-api.net/gremlin'
    q = {
        "query": f"g.V().has('abbreviation', '{abbr}').in('source_cloud').has('name', '{cat_name}').out('super_category').values('name')"
    }
    
    res = requests.post(query_url, json=q)
    data = res.json()
    if len(data) == 1:
        return data[0]
    else:
        return cat_name


def make_dedupe_data():
    """Extract normalized category_name, service_name, short_description and long_description
    from raw service data for use in linking services across cloud providers"""

    pbar = tqdm([c.value.lower() for c in Cloud])
    for c in pbar:
        pbar.set_description(c)
        df = pd.read_csv(f'data/raw/{c}_services.csv')
        df = df[['category_name', 'name', 'short_description', 'long_description']]

        norm_cats = {}
        for cat in df['category_name'].unique():
            norm_cats[cat] = get_normalized_cat_name(c, cat)

        df = df.groupby('name').aggregate({
            'category_name': list, 'short_description': 'first', 'long_description': 'first'
        }).reset_index()
        df.columns = ['name', 'categories', 'short_description', 'long_description']

        df['categories'] = df['categories'].apply(lambda cats: [norm_cats[cat_name] for cat_name in cats])
        df.to_csv(f'data/processed/{c}_dedupe_data.csv', index=False)


    pbar.set_description('Done')


if __name__ == '__main__':
    make_dedupe_data()