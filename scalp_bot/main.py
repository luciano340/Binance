
from csv import Error
from math import log
from repository.trade_repository import RepositoryMongoTrade
from web_bot import bot_work
from multiprocessing import Pool, Manager
from utils.client import BinanceClient
from prometheus_client import start_http_server
from queue import Queue
from utils.telegram import telegrambot
from concurrent.futures import ProcessPoolExecutor
import re
import logging
import random
import time
import threading


def validate_ticker(symbol, client):
    print(f'Starting validation of {symbol}')
    if re.search(r'[0-9]$', symbol):
        return

    if not re.search(r'USDT$', symbol):
        return
    
    try:
        time.sleep(random.randrange(60, 90)/100)
        ticker_info = client.get_ticker(symbol=symbol)
    except Exception as err:
        logging.exception(f'{err} - {symbol}')
        return
    
    if float(ticker_info['lastPrice']) < 1:
        return
    
    if float(ticker_info['quoteVolume']) < 120000:
        return

    return symbol

def process_symbol(symbol):
    return validate_ticker(symbol, client)
                           
if __name__ == '__main__':
    logging.basicConfig(filename='general.log', encoding='utf-8', level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(pathname)s on Line: %(lineno)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S')

    try:
        logging.info('Starting prometheus server on port 8000')
        start_http_server(8000)
    except Exception as err:
        logging.exception(f'Error to start prometheus server {err}')
        exit(1)
        
    try:
        client = BinanceClient()
    except Exception as err:
        logging.exception(f'Connection Error {err}')
        exit(1)

    status = client.get_account_status()
    logging.debug(f'Connection status {status["data"]}')

    info = client.get_account()
    logging.debug(f'Account information: \n{info}')

    assets_raw = client.get_exchange_info()
    symbols = [asset['symbol'] for asset in assets_raw['symbols']]
    with ProcessPoolExecutor(max_workers=40) as executor:
        results = list(executor.map(process_symbol, symbols))

    asset_list = [asset for asset in results if asset is not None]

    logging.debug(f'Total assets to be used: {len(asset_list)}')
    logging.info(f'Assents found {asset_list}')

    queue = Queue(maxsize=2000)
    USDT = client.client.get_asset_balance(asset="USDT")['free']
    queue.put(f'USDT em conta inicial: {USDT}')
    
    try:
        mongo_repository = RepositoryMongoTrade()
    except Exception as err:
        logging.error(f"Error to create pool connection with repository: {err}")
        raise Error(err)
    
    tbot = telegrambot(repository=mongo_repository)
    threading.Thread(target=tbot.send_messages, args=(queue,), name="telegram_send_message").start()
    threading.Thread(target=tbot.start_bot, name="telegram_bot").start()
    for asset in asset_list:
        time.sleep(random.randrange(90, 150)/100)
        bot = bot_work(coin=asset, client=client, queue=queue, repository=mongo_repository)
        threading.Thread(target=bot.start_stream, name=f'scalp_bot_{asset}').start()
        queue.put(f'Iniciando {asset}')