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
        base_soup = BeautifulSoup(requests.get(base_url).text, 'html.parser')

        digiocean_services = []
        for service_soup in base_soup.find('ul', {'class': 'UnifiedNav-list'}).find_all('li')[1].find_all('li'):
            service_name_soup = service_soup.find('p', {'class': 'UnifiedNavDropdown-link-contentTitle'})
            if not service_name_soup:
                continue
            service_name = service_name_soup.text.strip()
            print(service_name)
            service_desc = service_soup.find('p', {'class': 'UnifiedNavDropdown-link-contentDescription'}).text.strip()
            service_link = service_soup.find('a')['href']
            
            service_page_soup = BeautifulSoup(requests.get(service_link).text, 'html.parser')
            service_header_soup = service_page_soup.find('div', {'class': 'www-Container'})
            if len(service_header_soup.find_all('p')) == 1:
                service_long_desc = service_header_soup.find('p').text.strip()
            else:
                
                service_long_desc = service_header_soup.find('p', {'class': 'www-u-FontSize--large'}).text.strip()
            
            digiocean_services.append({
                'category_name': 'Compute',
                'name': service_name,
                'short_description': service_desc,
                'long_description': service_long_desc,
                'uri': service_link
            })

        return digiocean_services
