import click
from pathlib import Path
from src.data.cloud._constants import Cloud

from src.data.cloud.aws import AWSCloudProvider
from src.data.cloud.azure import AzureCloudProvider
from src.data.cloud.digitalocean import DigitalOceanCloudProvider
from src.data.cloud.google import GoogleCloudProvider
from src.data.cloud.ibm import IBMCloudProvider
# from src.data.cloud.oracle import OracleCloudProvider


def scrape_cloud_providers():
    for c in Cloud:
        print(f'Fetching services for {c.value}')
        print('=' * 50)
        scrape_cloud_provider(f'data/raw/{c.value.lower()}_services.csv', c.value)


def scrape_cloud_provider(output_filepath: Path, cloud: Cloud):

    cloud = Cloud(cloud)
    
    if cloud == Cloud.AWS:
        cloud_provider = AWSCloudProvider()
    elif cloud == Cloud.AZURE:
        cloud_provider = AzureCloudProvider()
    elif cloud == Cloud.DIGITALOCEAN:
        cloud_provider = DigitalOceanCloudProvider()
    elif cloud == Cloud.GCP:
        cloud_provider = GoogleCloudProvider()
    elif cloud == Cloud.IBM:
        cloud_provider = IBMCloudProvider()
    # elif cloud == Cloud.ORACLE:
    #     cloud_provider = OracleCloudProvider()

    services_df = cloud_provider.scrape_services()
    cloud_provider.save(services_df, output_filepath)


if __name__ == '__main__':
    scrape_cloud_providers()
