import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bs4 import BeautifulSoup
import time
from app.abstract import Scraper
import pandas as pd
import re
import logging

pd.set_option('display.max_columns', None)

class DellScraper(Scraper):

    def parse_page(self, url):
        html = self.fetch_page(url)
        if not html:
            logging.error(f"Error fetching page: {url}")
            print(f"Error fetching page: {url}")
            return {}

        soup = BeautifulSoup(html, 'html.parser')
        product_price = None
        try:
            product_name = soup.find('div', class_='sticky__page_title').get_text(strip=True)
            if product_name:
                logging.info(f"Extracted product_name: {product_name}")
            # Encontrar o div correto para o preço
            price_div = soup.find('div', class_='ps-dell-price ps-simplified')
            
            if price_div:
                # Buscar o texto bruto do preço no span correto
                price_span = price_div.find('span', class_=None)
                if price_span:
                    raw_price_text = price_span.get_text(strip=True)
                    logging.info(f"Extracted product_price: {raw_price_text}")
                    match = re.search(r"R\$\s*([\d.]+),", raw_price_text)
                    if match:
                        product_price = int(match.group(1).replace('.', ''))
                    else:
                        logging.error(f"Regex did not match price text: {raw_price_text}")
                else:
                    logging.warning("Price span not found in price_div")
            else:
                logging.error("Price div not found in HTML")

        except AttributeError as e:
            logging.exception(f"{e}")
            print(f"{e}")
            return {}
        except ValueError as e:
            logging.exception(f"{e}")
            print(f"{e}")
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
    