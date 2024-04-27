import requests.adapters
from binance.client import Client
from web_bot import bot_work
from threading import Thread
from multiprocessing import Pool, Manager
import requests
import logging
import re
import os
import random
import time


def validate_ticker(symbol, array, client):
    if re.search(r'[0-9]$', symbol):
        return

    if not re.search(r'USDT$', symbol):
        return
    
    try:
        time.sleep(random.randrange(60, 90)/100)
        ticker_info = client.get_ticker(symbol=symbol)
    except Exception as err:
        logging.error(f'{err} - {symbol}')
        return
    
    if float(ticker_info['lastPrice']) < 1.50:
        return
    
    if float(ticker_info['quoteVolume']) < 48000:
        return

    array.append(symbol)

if __name__ == '__main__':
    logging.basicConfig(filename='general.log', encoding='utf-8', level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(pathname)s on Line: %(lineno)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S')

    try:
        client = Client(os.environ['api_key_binance'], os.environ['api_secret_biance'])
        request_config = requests.adapters.HTTPAdapter(
            pool_connections=250,
            pool_maxsize=250,
            max_retries=5)
        client.session.mount('https://', request_config)
        manager = Manager()
        asset_list = manager.list()
    except Exception as err:
        logging.error(f'Connection Error {err}')
        exit(1)

    status = client.get_account_status()
    logging.debug(f'Connection status {status["data"]}')

    info = client.get_account()
    logging.debug(f'Account information: \n{info}')

    assets_raw = client.get_exchange_info()
    assets =  [[i['symbol'], asset_list, client] for i in assets_raw['symbols'] ]

    p = Pool(processes=12)
    p.starmap(validate_ticker, assets)
    p.close()

    logging.debug(f'Total assets to be used: {len(asset_list)}')
    logging.info(f'Assents found {asset_list}')

    for asset in asset_list:
        time.sleep(random.randrange(90, 150)/100)
        bot = bot_work(asset, client)
        Thread(target=bot.start_stream).start()