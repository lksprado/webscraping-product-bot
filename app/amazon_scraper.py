import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from playwright.sync_api import sync_playwright, Page
import logging
from app.abstract import Scraper
from tqdm import tqdm
from typing import List, Dict, Any
import time
import pandas as pd
import re


class AmazonScraper(Scraper):

    def setup_browser(self, pw) -> tuple:
        logging.info("Initiating Playwright browser")
        browser = pw.chromium.launch()
        context = browser.new_context(
            locale='en-US',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3 en-US,en;q=0.8',
            viewport={'width': 1920, 'height': 1080},
        )
        logging.info("Playwright browser setup completed")
        return browser, context.new_page()

    def parse_page(self, page: Page, timestamp: str, url: str, source_scraper: str) -> Dict:
        raw_data = page.evaluate('''
            (args) => {
                const { timestamp, url, source_scraper } = args;
                const title = document.querySelector('#productTitle')?.textContent.trim();
                const price = document.querySelector('.a-price-whole')?.textContent.trim();

                return {
                    created_at: timestamp,
                    product_name: title,
                    product_price: price,
                    url: url,
                    source_scraper: source_scraper
                };
            }
        ''', {'timestamp': timestamp, 'url': url, 'source_scraper': source_scraper})

        product_name = raw_data.get('product_name')
        product_price = raw_data.get('product_price')

        logging.info(f"Extracted product_name: {product_name}")
        logging.info(f"Extracted product_price: {product_price}")

        # Tratamento do campo 'price' para transformar no formato correto
        if product_price:
            try:
                raw_data['product_price'] = int(re.search(r"([\d.]+)", product_price).group(1).replace('.', ''))
            except (AttributeError, ValueError):
                logging.exception(f"Error while formatting product_price")
                raw_data['product_price'] = None  # Caso o formato não seja válido
        else:
            raw_data['product_price'] = None

        return raw_data

def run():
    df = pd.DataFrame()
    urls = [
        'https://www.amazon.com.br/kindle-16gb-preto/dp/B0CP31L73X?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=1HFWUNU2TWBY2&dib=eyJ2IjoiMSJ9.tPc6_ZjVnQ1jfDLVl67wncTB9j8KcpWsfZhOSUZR4sTmDaktoYP-gHBe1PZ7lcuMeELR61zM3MnLIxGLZprMv1UidewjUnSNaTyKgyNSEw0G6KsyaMvEOOOMnSSoaOMkwPmC8Op1Mcv5s-Ym8Rvx_OFoUpFJAAmt6e_tua83vzcxPe6QsTfq8Mp_Lf9PqwevTsN1NUcdfyI5myeGI711IElCieQdNDHSo-hNIijmrsgYSoSEncpaBSB2UZTORdxsvIAaRSBLLC7GetDc8Obvmw3CdK5q1dLnS_62w72j0Tpoq2_MA76Ep8ik2t3McDEnTxPpeJKHzCYsgZiunTrgxkAdiZDIrB0obQKJYyj8reZtfbfLUl44s2wL2btXOd6HFfZlvNukjaxoXjyUtRiFZw-574sTkWgdexKv-1e4PUVdDnLliYW4ccZ8-hgOmSjO.8U5pBFwgy-SZ09iFDs85owb7lz0zwUELS04ykNTl2jU&dib_tag=se&keywords=kindle&qid=1735602173&sprefix=kindl%2Caps%2C265&sr=8-1&ufe=app_do%3Aamzn1.fos.95de73c3-5dda-43a7-bd1f-63af03b14751&th=1',
        'https://www.amazon.com.br/Apple-iPhone-15-128-GB/dp/B0CP6CVJSG?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=2IKOYOL8LMQ2P&dib=eyJ2IjoiMSJ9.H9sLnVuXuYiD-cGJ27u1aSQEHJUb1-mkBQOUTGXBnHjJrE2SBYQsp3Jfl4A5-0Vh_mWKKjy300kIYcUHQZQ0cqqQpoS1YflOE5cgMQbuNKBnSeBFMIFz4maEPAhi1afhHYvODF_tH9xiLegsGp99cXd-MlX9Y1Luf4v1-3xf13dJ0x1znF4V7y-NXuyUOA1GVHXPyu30q_5XQinMi-SNvUJpFvGU_6IP-qpJtu53dRt8TQzOsKfuaApQy3ewK3T_nUOWJI0ycEd7YjDDQ0HjMMWRTj8_bA60h1yTGmsaukCTnOkkvZjlPo_gkS2PA9u0kEFgBQIjvZrbUgC5L8dnHX1ijSeULNAwmNcXGCwkqBu0JHmE6e4YzC4KHLJQlUlF0AHAavr8qutML6IMukkWd-lQJivzdB2sawIvnSRnCwpOtib8D464wafYKl3m1sD8.E8RJ9Edked4QBAmoHlwzZHAYUQZ3uyhMrg4pWm3LcxA&dib_tag=se&keywords=iphone%2B15&qid=1735604881&sprefix=iphone%2B1%2Caps%2C246&sr=8-4&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147&th=1'
    ]

    scraper = AmazonScraper()

    for url in urls:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        source_scraper = scraper.__class__.__name__ 
        # Setup browser context and page
        with sync_playwright() as pw:
            browser, page = scraper.setup_browser(pw)
            page.goto(url)

            # Coletar os dados da página
            data = scraper.parse_page(page, timestamp, url, source_scraper)

            # Adicionar os dados ao DataFrame
            df = scraper.make_dataframe(data, df)

            browser.close()

    if not df.empty:
        scraper.save_to_db(df, 'wish_list')