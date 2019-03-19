import functools
import multiprocessing as mp

import click
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from src.data.cloud._constants import Cloud
from src.data.cloud.alibaba import AlibabaCloudProvider
from src.data.cloud.aws import AWSCloudProvider
from src.data.cloud.azure import AzureCloudProvider
from src.data.cloud.digitalocean import DigitalOceanCloudProvider
from src.data.cloud.google import GoogleCloudProvider
from src.data.cloud.ibm import IBMCloudProvider
from src.data.cloud.oracle import OracleCloudProvider


@click.command()
@click.option(
    '-c',
    '--cloud',
    required=False,
    type=click.Choice([c.value for c in Cloud])
)
def scrape_cloud_providers(cloud=None):
    if cloud:
        _scrape_cloud_provider(Cloud(cloud))
    else:
        args = [c for c in Cloud]
        print(args)
        with mp.Pool(processes=len(args)) as pool:
            results = []
            for res in tqdm(pool.imap_unordered(_scrape_cloud_provider, Cloud), total=len(args)):
                results.append(res)




def _scrape_cloud_provider(cloud: Cloud):
    output_filepath = f'data/raw/{cloud.value.lower()}_services.csv'
    if cloud == Cloud.ALIBABA:
        cloud_provider = AlibabaCloudProvider(cloud)
    elif cloud == Cloud.AWS:
        cloud_provider = AWSCloudProvider(cloud)
    elif cloud == Cloud.AZURE:
        cloud_provider = AzureCloudProvider(cloud)
    elif cloud == Cloud.DIGITALOCEAN:
        cloud_provider = DigitalOceanCloudProvider(cloud)
    elif cloud == Cloud.GCP:
        cloud_provider = GoogleCloudProvider(cloud)
    elif cloud == Cloud.IBM:
        cloud_provider = IBMCloudProvider(cloud)
    elif cloud == Cloud.ORACLE:
        cloud_provider = OracleCloudProvider(cloud)

    services = cloud_provider.scrape_services()
    services_df = pd.DataFrame(services)
    cloud_provider.save(services_df, output_filepath)


if __name__ == '__main__':
    scrape_cloud_providers()
