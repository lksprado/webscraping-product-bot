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

    def fetch_page(self, url, headers=None, method="GET", data=None):
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

    def parse_html(self, html):
        """Transforma o HTML em um objeto BeautifulSoup."""
        return BeautifulSoup(html, 'html.parser')

    @abstractmethod
    def parse_page(self, url) -> dict:
        """Método abstrato que será implementado para coletar os dados específicos. Iniciar com o objeto soup criado a partir de parse_html"""
        pass
    
    @abstractmethod
    def make_dataframe(self, _dict):
        pass

    def save_to_db(self, data, table_name):
        """Salva o DataFrame no banco."""
        try:
            # Adiciona a coluna 'source_scraper' diretamente ao DataFrame
            data['source_scraper'] = self.__class__.__name__
            
            # Salva no banco de dados
            self.pg.save_dataframe(data, table_name)
        except Exception as e:
            print(f"Erro ao salvar os dados no banco: {e}")