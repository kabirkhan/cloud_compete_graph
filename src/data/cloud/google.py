# -*- coding: utf-8 -*-
import json

import click
import logging
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse
from src.data.cloud._base import BaseCloudProvider


class GoogleCloudProvider(BaseCloudProvider):
    def scrape_services(self) -> pd.DataFrame:
        GOOGLE_BASE_URL = 'https://cloud.google.com/products'
        soup = BeautifulSoup(requests.get(GOOGLE_BASE_URL).text, 'html.parser')
        category_soups = soup.find_all('div', {'class': 'cloud-product-card'})

        services = []

        for cat_soup in category_soups:        
            cat_title = cat_soup.find('a').text.strip()
            if 'arrow_forward' in cat_title:
                cat_title = cat_title[:cat_title.index('arrow_forward') - 1]
            
            headlines = cat_soup.find_all('a', {'class': 'cloud-product-card__headline'})
            sub_headlines = cat_soup.find_all('div', {'class': 'cloud-product-card__sub-headline'})
            
            
            for i in range(len(headlines)):
                link = headlines[i]['href']
                service = {
                    'category_name': cat_title,
                    'name': headlines[i].text.strip(),
                    'short_description': sub_headlines[i].text.strip(),
                    'long_description': '',
                    'link': headlines[i]['href'],
                    'icon': ''
                }

                if urlparse(link).netloc == 'cloud.google.com':
                    
                    service_soup = BeautifulSoup(requests.get(link).text, 'html.parser')
                    
                    try:
                        service['long_description'] = service_soup.find('meta', {'property': 'og:description'})['content'].strip()

                        article_soup = service_soup.find('article', {'id': 'cloud-site'})
                        try_free_button_soup = article_soup.find('a')
                        icon_class = try_free_button_soup['class'][-1]
                        service['icon'] = f"{GOOGLE_BASE_URL}/_static/images/cloud/products/logos/svg/{icon_class}-icon.svg"
                    except:
                        print("No icon or long description")
                        pass
                
                services.append(service)
        gcp_services = pd.DataFrame(services)
        gcp_services = gcp_services[[
            'category_name', 'name', 'short_description', 'long_description', 'link', 'icon'
        ]]
        return gcp_services
