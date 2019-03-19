# -*- coding: utf-8 -*-
import json

import click
import logging
from pathlib import Path
from urllib.parse import parse_qs

from bs4 import BeautifulSoup
import pandas as pd
import requests
from src.data.cloud._base import BaseCloudProvider
from tqdm import tqdm


class AWSCloudProvider(BaseCloudProvider):
    def scrape_services(self) -> pd.DataFrame:
        AWS_BASE_URL = 'https://aws.amazon.com'
        soup = BeautifulSoup(requests.get(f'{AWS_BASE_URL}/products').text, 'html.parser')

        category_soups = soup.find_all('a', {'class': 'lb-trigger'})
        aws_categories = []
        for i, cat in enumerate(category_soups):
            aws_categories.append({
                'category_id': i + 1,
                'category_name': cat.text.strip()
            })
        aws_categories_df = pd.DataFrame(aws_categories)
        
        service_soups = [s.find('a') for s in soup.find_all('div', {'class': 'lb-content-item'})]
        aws_services = []

        for s in service_soups:
            url = f"{AWS_BASE_URL}{s['href']}"
            text = s.text.strip()
            desc = s.find('span').text.strip()
            name = text[:text.index(desc)]
            
            service_detail_soup = BeautifulSoup(requests.get(url).text, 'html.parser')
            full_description = '\n'.join([p.text for p in service_detail_soup.find_all('p')[:3]])
            
            aws_services.append({
                'category_id': int(parse_qs(url.split('?')[1])['c'][0]),
                'name': name,
                'short_description': desc,
                'long_description': full_description,
                'link': url,
                'icon': ''
            })
        aws_services_df = pd.DataFrame(aws_services)
        aws_df = pd.merge(aws_categories_df, aws_services_df, on='category_id')
        aws_df = aws_df[['category_id', 'category_name', 'name', 'short_description', 'long_description', 'link', 'icon']]

        return aws_df.to_dict('records')
