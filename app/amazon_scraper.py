import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bs4 import BeautifulSoup
import time
from abstract import Scraper
import pandas as pd
import re
import undetected_chromedriver as uc
import random

pd.set_option('display.max_columns', None)

class AmazonScraper(Scraper):
    
    def fetch_page_with_uc(self, driver, url):
        driver.get(url)
        time.sleep(random.uniform(1, 2))  # Aguardar um tempo aleatório para evitar bloqueios
        html = driver.page_source
        return html


    def parse_page(self, driver, url):
        html = self.fetch_page_with_uc(driver, url)
        soup = BeautifulSoup(html, 'lxml')
        product_name = soup.find('span', id='productTitle').get_text(strip=True)
        product_price = soup.find('span', attrs={'class': 'a-price aok-align-center'}).find(
            'span', attrs={'class': 'a-offscreen'}).text.strip()
        product_price = int(re.search(r"R\$\s*([\d.]+),", product_price).group(1).replace('.', '')) if product_price else None
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

    # URL do produto Amazon
    urls = ['https://www.amazon.com.br/kindle-16gb-preto/dp/B0CP31L73X?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=1HFWUNU2TWBY2&dib=eyJ2IjoiMSJ9.tPc6_ZjVnQ1jfDLVl67wncTB9j8KcpWsfZhOSUZR4sTmDaktoYP-gHBe1PZ7lcuMeELR61zM3MnLIxGLZprMv1UidewjUnSNaTyKgyNSEw0G6KsyaMvEOOOMnSSoaOMkwPmC8Op1Mcv5s-Ym8Rvx_OFoUpFJAAmt6e_tua83vzcxPe6QsTfq8Mp_Lf9PqwevTsN1NUcdfyI5myeGI711IElCieQdNDHSo-hNIijmrsgYSoSEncpaBSB2UZTORdxsvIAaRSBLLC7GetDc8Obvmw3CdK5q1dLnS_62w72j0Tpoq2_MA76Ep8ik2t3McDEnTxPpeJKHzCYsgZiunTrgxkAdiZDIrB0obQKJYyj8reZtfbfLUl44s2wL2btXOd6HFfZlvNukjaxoXjyUtRiFZw-574sTkWgdexKv-1e4PUVdDnLliYW4ccZ8-hgOmSjO.8U5pBFwgy-SZ09iFDs85owb7lz0zwUELS04ykNTl2jU&dib_tag=se&keywords=kindle&qid=1735602173&sprefix=kindl%2Caps%2C265&sr=8-1&ufe=app_do%3Aamzn1.fos.95de73c3-5dda-43a7-bd1f-63af03b14751&th=1',
            'https://www.amazon.com.br/Apple-iPhone-15-128-GB/dp/B0CP6CVJSG?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=2IKOYOL8LMQ2P&dib=eyJ2IjoiMSJ9.H9sLnVuXuYiD-cGJ27u1aSQEHJUb1-mkBQOUTGXBnHjJrE2SBYQsp3Jfl4A5-0Vh_mWKKjy300kIYcUHQZQ0cqqQpoS1YflOE5cgMQbuNKBnSeBFMIFz4maEPAhi1afhHYvODF_tH9xiLegsGp99cXd-MlX9Y1Luf4v1-3xf13dJ0x1znF4V7y-NXuyUOA1GVHXPyu30q_5XQinMi-SNvUJpFvGU_6IP-qpJtu53dRt8TQzOsKfuaApQy3ewK3T_nUOWJI0ycEd7YjDDQ0HjMMWRTj8_bA60h1yTGmsaukCTnOkkvZjlPo_gkS2PA9u0kEFgBQIjvZrbUgC5L8dnHX1ijSeULNAwmNcXGCwkqBu0JHmE6e4YzC4KHLJQlUlF0AHAavr8qutML6IMukkWd-lQJivzdB2sawIvnSRnCwpOtib8D464wafYKl3m1sD8.E8RJ9Edked4QBAmoHlwzZHAYUQZ3uyhMrg4pWm3LcxA&dib_tag=se&keywords=iphone%2B15&qid=1735604881&sprefix=iphone%2B1%2Caps%2C246&sr=8-4&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147&th=1'
    ]
            
    # Configurar navegador
    options = uc.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    
    driver = uc.Chrome(options=options)

    try:
        # Criar instância do scraper
        scraper = AmazonScraper()

        for url in urls:
            # Coletar os dados
            data = scraper.parse_page(driver, url)
            df = scraper.make_dataframe(data, df)
            time.sleep(1)

        #print(df)
        if not df.empty:
            scraper.save_to_db(df, 'wish_list')
    finally:
        # Fechar navegador
        driver.quit()
    