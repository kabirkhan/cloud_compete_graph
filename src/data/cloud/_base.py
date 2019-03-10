# -*- coding: utf-8 -*-
import abc
import json

import click
import logging
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pandas as pd


class BaseCloudProvider(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def scrape_services(self) -> pd.DataFrame:
        raise NotImplementedError

    def save(self, df: pd.DataFrame, output_filepath: Path):
        assert output_filepath.endswith('.csv')
        df.to_csv(output_filepath, index=False)
