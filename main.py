import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.amazon_scraper import AmazonScraper
from app.dell_scraper import DellScraper
from src.postgres_con import PostgresClient
from src.queries import sql_query
import pandas as pd 
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = Bot(token=TOKEN)

df = pd.DataFrame()

# Função para tratar o scraping
def process_scraper(scraper,urls, df):
    for url in urls:
        try:
            data = scraper.parse_page(url)
            df = scraper.make_dataframe(data, df)
        except Exception as e:
            print(f"Erro ao processar a URL {url}: {e}")
    return df

# Processar DELL ##############################################################
def process_dell_urls():
    urls_dell = [
        'https://www.dell.com/pt-br/shop/monitor-dell-de-27-4k-com-hub-usb-c-p2723qe/apd/210-beni/monitores-e-acess%C3%B3rios',
        'https://www.dell.com/pt-br/shop/monitor-dell-de-24-qhd-p2423d/apd/210-beos/monitores-e-acess%C3%B3rios'
    ]
    scraper_dell = DellScraper()
    return process_scraper(scraper_dell, urls_dell ,df)

## Processar Amazon ##############################################################
def process_amazon_urls():
    urls_amz = [
        'https://www.amazon.com.br/kindle-16gb-preto/dp/B0CP31L73X?th=1',
        'https://www.amazon.com.br/Apple-iPhone-15-128-GB/dp/B0CP6CVJSG?th=1'
    ]
    scraper_amazon = AmazonScraper()
    return process_scraper(scraper_amazon, urls_amz, df)

# Processar e salvar no banco de dados
def process_database(pg, df):
    try:
        pg.save_dataframe(df, 'wish_list')
    except Exception as e:
        print(f"Erro ao salvar os dados no banco: {e}")

    query = sql_query
    result_df = None
    try:
        result_df = pg.execute_query(query)
    except Exception as e:
        print(f"Erro ao executar a consulta SQL: {e}")
    return result_df


async def send_telegram_message(text):
    try:
        await bot.send_message(text=text, chat_id=CHAT_ID)
    except Exception as e:
        print(f"Erro ao enviar mensagem pelo Telegram: {e}")

async def main():
    df_dell = process_dell_urls()
    df_amazon = process_amazon_urls()
    df = pd.concat([df_dell, df_amazon], ignore_index=True)
    
    pg_client = PostgresClient()
    result_df = process_database(pg_client, df)
    if result_df is not None and not result_df.empty:
        message = "\n".join(
            f"{row['product_name']}, R${row['current_price']}, {row['preco']}"
            for _, row in result_df.iterrows()
        )
        await send_telegram_message(message)
    
    pg_client.close_connection()

if __name__ == "__main__":
    asyncio.run(main())
