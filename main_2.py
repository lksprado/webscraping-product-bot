import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from playwright.sync_api import sync_playwright, Page
from app.amazon_scraper import run as amz_run
from app.dell_scraper import run as dell_run
from src.postgres_con import PostgresClient
from src.queries import sql_query
import pandas as pd 
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import re

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = Bot(token=TOKEN)

amz_run()
dell_run()

async def send_telegram_message(text):
    try:
        await bot.send_message(text=text, chat_id=CHAT_ID)
    except Exception as e:
        print(f"Erro ao enviar mensagem pelo Telegram: {e}")

def process_database(pg):
    try:
        query = sql_query
        result_df = None
        result_df = pg.execute_query(query)
    except Exception as e:
        print(f"Erro ao executar a consulta SQL: {e}")
    return result_df

async def main():
    pg_client = PostgresClient()
    result_df = process_database(pg_client)
    if result_df is not None and not result_df.empty:
        for _, row in result_df.iterrows():
            message = f"{row['product_name']}\nR${row['current_price']}\n{row['preco']}"
            await send_telegram_message(message)
    
    pg_client.close_connection()
    
if __name__ == "__main__":
    asyncio.run(main())
    
