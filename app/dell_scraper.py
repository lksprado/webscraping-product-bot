import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bs4 import BeautifulSoup
import time
from app.abstract import Scraper
import pandas as pd
import re

pd.set_option('display.max_columns', None)

class DellScraper(Scraper):
    
    def parse_page(self, url):
        html = self.fetch_page(url)
        if not html:
            print("Erro ao buscar a página")
            return {}

        soup = BeautifulSoup(html, 'html.parser')
        product_price = None
        try:
            product_name = soup.find('div', class_='sticky__page_title').get_text(strip=True)
            # Encontrar o div correto para o preço
            price_div = soup.find('div', class_='ps-dell-price ps-simplified')
            if price_div:
                # Buscar apenas o span correto dentro do div
                price_span = price_div.find('span', class_=None)
                if price_span:
                    product_price = price_span.get_text(strip=True)
                    product_price = int(re.search(r"R\$\s*([\d.]+),", product_price).group(1).replace('.', ''))
                else:
                    print("Elemento span do preço não encontrado.")
            else:
                print("Div do preço não encontrado.")

        except AttributeError:
            print("Erro ao encontrar os elementos na página.")
            return {}
        except ValueError:
            print("Erro ao converter o preço para inteiro.")
            return {}

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        return {
            'created_at': timestamp,
            'product_name': product_name,
            'product_price': product_price,
            'url': url,
            'source_scraper': self.__class__.__name__
        }

        
def run():
    df = pd.DataFrame()

    # URL do produto Dell
    urls = ['https://www.dell.com/pt-br/shop/monitor-dell-de-27-4k-com-hub-usb-c-p2723qe/apd/210-beni/monitores-e-acess%C3%B3rios',
            'https://www.dell.com/pt-br/shop/monitor-dell-de-24-qhd-p2423d/apd/210-beos/monitores-e-acess%C3%B3rios'
    ]

    # Criar instância do scrapper
    scraper = DellScraper()

    for url in urls:
        # Coletar os dados
        data = scraper.parse_page(url)
        df = scraper.make_dataframe(data ,df)
        time.sleep(1)

    if not df.empty:
        scraper.save_to_db(df, 'wish_list')
        
if __name__ == "__main__":
    run()
    