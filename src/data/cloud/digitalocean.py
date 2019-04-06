# -*- coding: utf-8 -*-
import json
from pathlib import Path
from urllib.parse import parse_qs

from bs4 import BeautifulSoup
import requests
from src.data.cloud._base import BaseCloudProvider


class DigitalOceanCloudProvider(BaseCloudProvider):
    def scrape_services(self):
        base_url = 'https://www.digitalocean.com/'
        base_soup = BeautifulSoup(requests.get(f'{base_url}/products').text, 'html.parser')

        digiocean_services = []
        for cat_soup in base_soup.find_all('section', {'class': 'InPageNav-anchor'}):
            cat_id = cat_soup['id']
            cat_name = cat_soup.find('h3').text.strip()
            cat_desc = cat_soup.find('p').text.strip()
            for svc_soup in cat_soup.find_all('a', {'class': 'www-Card'}):
                name = svc_soup.find('h4').text.strip()
                if 'Digital' not in name:
                    name = f'DigitalOcean {name}'
                link = svc_soup['href'].strip()
                url = f'{base_url}{link}'
                
                short_desc = svc_soup.find('p').text.strip()
                icon_src = svc_soup.find('img')['src']
                icon_url = f'{base_url}{icon_src}'
                digiocean_services.append({
                    'category_id': cat_id,
                    'category_name': cat_name,
                    'category_description': cat_desc,
                    'name': name,
                    'link': url,
                    'short_description': short_desc,
                    'long_description': '',
                    'icon': icon_url
                })
        return digiocean_services
