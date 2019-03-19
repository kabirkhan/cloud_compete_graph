# -*- coding: utf-8 -*-
import json

from pathlib import Path
from urllib.parse import parse_qs

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from src.data.cloud._base import BaseCloudProvider


class IBMCloudProvider(BaseCloudProvider):
    def scrape_services(self):
        base_url = 'https://www.ibm.com'
        res = requests.get(f'{base_url}/cloud/products')
        base_soup = BeautifulSoup(res.text, 'html.parser')
        cat_services_mapping_soups = []
        band_soups = base_soup.find_all('div', {'class': 'ibm-band'}, id=True)
        i = 0
        while i < len(band_soups) - 1:
            cat_services_mapping_soups.append((band_soups[i], band_soups[i+1]))
            i += 2

        ibm_services = []

        for cat_soup, services_soup in cat_services_mapping_soups:
            cat_name = cat_soup.find('h2').text.strip()
            cat_desc_soup = cat_soup.find('p')
            cat_description = cat_desc_soup.text.strip()

            cat_link_soup = cat_desc_soup.find('a')
            
            if cat_link_soup:
                cat_link = f"{base_url}{cat_link_soup['href']}"
                learn_more_idx = cat_description.index(cat_link_soup.text.strip())
                cat_description = cat_description[:learn_more_idx]

            for card_soup in services_soup.find_all('div', {'class': 'ibm-card'}):
                service_link_soup = card_soup.find('a')
                service_name = service_link_soup.text.strip()

                href = service_link_soup['href']
                if href.startswith('http'):
                    service_link = href
                else:   
                    service_link = f"{base_url}{href}"
                
                
                service_page_soup = BeautifulSoup(requests.get(service_link).text, 'html.parser')
                try:
                    service_short_desc = service_page_soup.find('meta', {'name': 'description'})['content'].strip()
                except:
                    continue
                try:
                    
                    service_long_desc = service_page_soup.find(
                        'section', {'class': 'product-overview-summary-section'}
                    ).text.strip().split('\n\n')[-1]
                except:
                    service_long_desc = service_short_desc

                ibm_services.append({        
                    'category_name': cat_name,
                    'category_description': cat_description,
                    'category_link': cat_link,
                    'name': service_name,
                    'short_description': service_short_desc,
                    'long_description': service_long_desc,
                    'link': service_link,
                    'icon': ''
                })

        return ibm_services
