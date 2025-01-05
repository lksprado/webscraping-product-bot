import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bs4 import BeautifulSoup
import time
from abstract import Scraper
import pandas as pd
import re

pd.set_option('display.max_columns', None)

class DellScraper(Scraper):
    
    def parse_page(self, url):
        html = self.fetch_page(url)
        if not html:
            print ("Erro ao buscar a pagina")
            return {}
        
        soup = self.parse_html(html)
        
        try:
            product_name = soup.find('div', class_='sticky__page_title').get_text(strip=True)
            product_price = soup.find('div', class_='ps-dell-price ps-simplified').get_text(strip=True)
            product_price = int(re.search(r"R\$\s*([\d.]+),", product_price).group(1).replace('.', '')) if product_price else None

        except AttributeError:
            print("Erro ao encontrar os elementos na página.")
            return {}
        
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'created_at': timestamp,
            'product_name': product_name,
            'product_price': product_price,
            'url': url
        }
        
    def make_dataframe(self, _dict , df):
        new_row = pd.DataFrame([_dict])
        df = pd.concat([df, new_row], ignore_index=True)
        return df
    
    

if __name__ == "__main__":
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
    