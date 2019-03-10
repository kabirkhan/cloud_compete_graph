# -*- coding: utf-8 -*-
import json

import click
import logging
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pandas as pd
from src.data.cloud._base import BaseCloudProvider


class AzureCloudProvider(BaseCloudProvider):
    def scrape_services(self) -> pd.DataFrame:
        AZURE_DOCS_URL = 'https://docs.microsoft.com/en-us/azure/'
        
        soup = BeautifulSoup(requests.get(AZURE_DOCS_URL + '#pivot=products').text, 'html.parser')
        
        azure_services = []
        categories_soup = soup.find('ul', {'id': 'products'}).find_all(
            'a', {'data-linktype': 'self-bookmark'}
        )
        categories_soup = categories_soup[1:]

        for category in categories_soup:
            category_id = category['href'][1:]

            category_soup = soup.find('ul', {'id': category_id})
            
            for link_soup in category_soup.find_all('a'):
                card_soup = link_soup.find('div', {'class': 'card'})
                service_name = card_soup.find('h3').text
                if 'Azure' not in service_name:
                    service_name = f'Azure {service_name}'

                href = link_soup['href']
                # if not href.startswith('https'):
                link = f"https://docs.microsoft.com{href}"
                
                short_description = card_soup.find('p').text.strip()
                try:
                    service_page_soup = BeautifulSoup(requests.get(link).text, 'html.parser')
                except:
                    print("Could not access page: ", link)
                    print("Skipping")
                    continue
                    
                try:
                    abstract = service_page_soup.find('div', {'class': 'abstract'}).find('p').text
                except:
                    try:
                        # Redirected to an overview page which doesn't have an abstract.
                        # Grab the initial paragraph
                        abstract = service_page_soup.find('main').find('p').text
                    except:
                        print('Could not get abstract or initial paragraph describing ', service_name)
                        abstract = short_description
                    
                azure_services.append({
                    'category_id': category_id,
                    'category_name': category.text.strip(),
                    'icon': f"{AZURE_DOCS_URL}{card_soup.find('img')['src']}",
                    'name': service_name,
                    'short_description': short_description,
                    'long_description': abstract,
                    'link': link
                })

        azure_services_df = pd.DataFrame(azure_services)
        azure_services_df = azure_services_df[[
            'category_id', 'category_name', 'name', 'short_description', 'long_description', 'link', 'icon'
        ]]
        return azure_services_df