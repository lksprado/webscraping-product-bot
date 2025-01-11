import logging 
from logging.handlers import RotatingFileHandler
import os

logging.basicConfig(
    filename='scrapers_logs.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
)
logger = logging.getLogger(__name__)