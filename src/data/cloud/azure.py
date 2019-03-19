# -*- coding: utf-8 -*-
import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from src.data.cloud._base import BaseCloudProvider


class AzureCloudProvider(BaseCloudProvider):
    def scrape_services(self):
        base_url = 'https://azure.microsoft.com'

        soup = BeautifulSoup(requests.get(f'{base_url}/services').text, 'html.parser')
        products_soup = soup.find('div', {'id': 'products-list'})
        services = []

        for cat in products_soup.find_all('div', {'class': 'row-size3'}):
            nextNode = cat
            cat_id = cat.find('h2', {'class': 'product-category'})['id']
            cat_name = cat.find('h2', {'class': 'product-category'}).text.strip()
            try:
                cat_link = f"{base_url}{cat.find('a')['href']}"
            except:
                cat_link = ''
            while True:
                nextNode = nextNode.nextSibling.nextSibling

                try:
                    class_names = nextNode.get('class')
                except:
                    break
                
                if 'row-size2' in class_names:
                    names = [h2.text.strip() for h2 in nextNode.find_all('h2')]
                    links = [a['href'] for a in nextNode.find_all('a')]
                    descs = [p.text.strip() for p in nextNode.find_all('p')]
                    
                    for i in range(len(names)):
                        link = f"{base_url}{links[i]}"
                        svc_soup = BeautifulSoup(requests.get(link).text, 'html.parser')
                        long_desc = svc_soup.find('meta', {'name': 'description'})['content']
                        
                        try:
                            docs_btn = svc_soup.find('nav', {'class': 'sub-nav'}).find(text='Documentation').parent
                        except:
                            try:
                                docs_btn = svc_soup.find('nav', {'id': 'global-subnav'}).find_all('a', {'class', 'external-link'})[-1]
                            except:
                                try:
                                    docs_btn = svc_soup.find('nav', {'class': 'sub-nav'}).find(text='Developer Guide').parent
                                except:
                                    continue

                        if docs_btn and docs_btn.get('href'):
                            documentation_links = docs_btn['href']
                        else:
                            documentation_links = [a['href'] for a in docs_btn.nextSibling.nextSibling.find_all('a')]
                        
                        services.append({
                            'category_id': cat_id,
                            'category_name': cat_name,
                            'category_link': cat_link,
                            'name': names[i],
                            'link': link,
                            'short_description': descs[i],
                            'long_description': long_desc,
                            'icon': '',
                            'documentation_links': documentation_links
                        })
                else:
                    break
        return services
