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
                        svc_name = names[i]
                        ids = ['Azure', 'Bing', 'Microsoft', 'Xamarin', 'Visual Studio']
                        no_id = all([i not in svc_name for i in ids])
                        if no_id:
                            svc_name = f'Azure {svc_name}' 
                        
                        link = f"{base_url}{links[i]}"
                        svc_soup = BeautifulSoup(requests.get(link).text, 'html.parser')
                        long_desc = svc_soup.find('meta', {'name': 'description'})['content']
                        
                        services.append({
                            'category_id': cat_id,
                            'category_name': cat_name,
                            'category_link': cat_link,
                            'name': svc_name,
                            'link': link,
                            'short_description': descs[i],
                            'long_description': long_desc,
                            'icon': ''
                        })
                else:
                    break
        return services
