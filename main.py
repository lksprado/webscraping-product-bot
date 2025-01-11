import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.amazon_scraper import run as amz_run
from app.dell_scraper import run as dell_run
from src.postgres_con import PostgresClient
from src.queries import sql_query
import pandas as pd 
import asyncio
from telegram import Bot
import telegram
from dotenv import load_dotenv
from src.logger import logger
import time




load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = Bot(token=TOKEN)

amz_run()
dell_run()

async def send_telegram_message(text):
    try:
        await bot.send_message(text=text, chat_id=CHAT_ID, parse_mode='HTML')
    except Exception as e:
        logger.error(f"{e}")

def process_database(pg):
    try:
        query = sql_query
        result_df = None
        result_df = pg.execute_query(query)
    except Exception:
        logger.error(f"Error executing SQL")
    return result_df

async def main():
    timestamp = time.strftime('%d/%m/%Y')
    pg_client = PostgresClient()
    result_df = process_database(pg_client)
    if result_df is not None and not result_df.empty:
        for _, row in result_df.iterrows():
            message = f"{timestamp}\n{row['product_name']}\n<b>R${row['current_price']}</b>\n{row['preco']}"
            await send_telegram_message(message)
    
    pg_client.close_connection()
    
if __name__ == "__main__":
    asyncio.run(main())
    
