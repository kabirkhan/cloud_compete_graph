# -*- coding: utf-8 -*-
import json

import click
import logging
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pandas as pd


@click.command()
@click.argument('output_filepath', type=click.Path())
def scrape_azure_services(output_filepath):
    assert output_filepath.endswith('.csv')

    AZURE_DOCS_URL = 'https://docs.microsoft.com/en-us/azure/'
    
    soup = BeautifulSoup(requests.get(AZURE_DOCS_URL + '#pivot=products').text, 'html.parser')
    
    azure_services = []
    categories_soup = soup.find('ul', {'id': 'products'}).find_all(
        'a', {'data-linktype': 'self-bookmark'}
    )
    categories_soup = categories_soup[1:]

    for category in categories_soup:
        category_id = category['href'][1:]

        # services = []
        category_soup = soup.find('ul', {'id': category_id})
        
        for link_soup in category_soup.find_all('a'):
            card_soup = link_soup.find('div', {'class': 'card'})
            service_name = card_soup.find('h3').text
            if 'Azure' not in service_name:
                service_name = f'Azure {service_name}'

            azure_services.append({
                'category_id': category_id,
                'category_name': category.text.strip(),
                'icon': f"{AZURE_DOCS_URL}{card_soup.find('img')['src']}",
                'name': service_name,
                'short_description': card_soup.find('p').text.strip(),
                'long_description': card_soup.find('p').text.strip(),
                'link': f"https://docs.microsoft.com{link_soup['href']}"
            })

    azure_services_df = pd.DataFrame(azure_services)
    azure_services_df.to_csv(output_filepath, index=False)
    

if __name__ == '__main__':
    scrape_azure_services()