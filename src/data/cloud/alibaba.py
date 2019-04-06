import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from src.data.cloud._base import BaseCloudProvider


class AlibabaCloudProvider(BaseCloudProvider):
    def scrape_services(self):
        base_url = 'https://www.alibabacloud.com'
        soup = BeautifulSoup(requests.get(f"{base_url}/product").text, 'html.parser')
        cat_soups = soup.find_all('div', {'class': 'group-item'})

        alibaba_services = []
        for c_soup in cat_soups:
            cat = c_soup.find('div', {'class': 'group-head'})
            cat_name = cat.find('h2').text.strip()
            cat_desc = cat.find('p').text.strip()
            
            services = c_soup.find('div', {'class': 'group-body'})
            for service in services.find_all('li'):
                name = service.text.strip()
                if 'Alibaba' not in name:
                    name = f'Alibaba {name}'

                link = service.find('a')['href']
                if not link.startswith('https'):
                    link = f"{base_url}/{link}"
                    
                svc_soup = BeautifulSoup(requests.get(link).text, 'html.parser')
                try:
                    short_desc = svc_soup.find('p', {'class': 'text-thin'}).text.strip()
                    long_desc = ' '.join(svc_soup.find('div', {'class': 'description'}).text.strip().split())
                except:
                    pass
                alibaba_services.append({
                    'category_name': cat_name,
                    'category_description': cat_desc,
                    'name': name,
                    'link': link,
                    'short_description': short_desc,
                    'long_description': long_desc,
                    'icon': ''
                })
        return alibaba_services
