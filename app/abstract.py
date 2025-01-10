# This is a scraper tooltkit to build html scrapers to 
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from abc import ABC, abstractmethod
from src.postgres_con import PostgresClient
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd


class Scraper(ABC):
    def __init__(self):
        self.pg = PostgresClient()
        
    @staticmethod
    def fetch_page(url, headers=None, method="GET", data=None):
        """Realiza a requisição HTTP e retorna o HTML."""
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, data=data)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")

            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Erro ao buscar a página: {e}")
            return None

    @abstractmethod
    def parse_page(self, url) -> dict:
        """Método abstrato que será implementado para coletar os dados específicos de uma página html."""
        pass
    
    @staticmethod
    def make_dataframe(_dict , df)->pd.DataFrame:
        """Gerar um dataframe."""
        new_row = pd.DataFrame([_dict])
        df = pd.concat([df, new_row], ignore_index=True)
        return df

    def save_to_db(self, data, table_name):
        """Salva o DataFrame no banco."""
        try:
            # Adiciona a coluna 'source_scraper' diretamente ao DataFrame
            data['source_scraper'] = self.__class__.__name__
            
            # Salva no banco de dados
            self.pg.save_dataframe(data, table_name)
        except Exception as e:
            print(f"Erro ao salvar os dados no banco: {e}")