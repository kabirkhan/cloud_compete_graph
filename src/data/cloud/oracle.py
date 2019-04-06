import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from src.data.cloud._base import BaseCloudProvider


class OracleCloudProvider(BaseCloudProvider):
    def scrape_services(self):
        paas_url = 'https://www.oracle.com/cloud/platform.html'
        iaas_url = 'https://www.oracle.com/cloud/infrastructure.html'
        services = self.get_services(iaas_url) + self.get_services(paas_url)
        return services

    def get_services(self, base_url):
        soup = BeautifulSoup(requests.get(base_url).text, 'html.parser')
        cat_soups = soup.find('section', {'class': 'cw60'}).find_all('div', {'class': 'cw60w2'})

        services = []
        for c_soup in cat_soups:
            cat_id = c_soup.find('a')['href'][1:]
            h6 = c_soup.find('h6', {'class': 'beforeblue'})
            cat_name = h6.text

            for s_soup in c_soup.find_all('div', {'class': 'cw60w4'}):
                name = s_soup.find('a').text
                if 'Oracle' not in name:
                    name = f'Oracle {name}'
                link = s_soup.find('a')['href']
                short_desc = s_soup.find('p').text
                if link.startswith('/'):
                    continue
                page_soup = BeautifulSoup(requests.get(link).text, 'html.parser')
                try:
                    long_desc = page_soup.find('h5', {'black-center'}).text
                except:
                    try:
                        long_desc = page_soup.find('h6', {'class': 'grey2'}).text
                    except:
                        long_desc = ''
                icon = page_soup.find('div', {'class': 'service-banner-icon'})
                try:
                    icon_url =  f"https://cloud.oracle.com{icon.find('img')['src']}" if icon else ''
                except:
                    icon_url = ''

                services.append({
                    'category_id': cat_id,
                    'category_name': cat_name,
                    'name': name,
                    'short_description': short_desc,
                    'long_description': long_desc,
                    'link': link,
                    'icon': icon_url
                })
        return services