
from web_bot import bot_work
from multiprocessing import Pool, Manager
from utils.client import BinanceClient
from prometheus_client import start_http_server
from queue import Queue
from utils.telegram import telegrambot
import logging
import re
import os
import random
import time
import threading


def validate_ticker(symbol, array, client):
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
    
    if float(ticker_info['lastPrice']) < 15:
        return
    
    if float(ticker_info['quoteVolume']) < 120000:
        return

    array.append(symbol)

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
        manager = Manager()
        asset_list = manager.list()
    except Exception as err:
        logging.exception(f'Connection Error {err}')
        exit(1)

    status = client.get_account_status()
    logging.debug(f'Connection status {status["data"]}')

    info = client.get_account()
    logging.debug(f'Account information: \n{info}')

    assets_raw = client.get_exchange_info()
    assets =  [[i['symbol'], asset_list, client] for i in assets_raw['symbols'] ]

    p = Pool(processes=40)
    p.starmap(validate_ticker, assets)
    p.close()

    logging.debug(f'Total assets to be used: {len(asset_list)}')
    logging.info(f'Assents found {asset_list}')

    queue = Queue(maxsize=2000)
    for asset in asset_list:
        time.sleep(random.randrange(90, 150)/100)
        bot = bot_work(asset, client, queue)
        threading.Thread(target=bot.start_stream, name=f'scalp_bot_{asset}').start()

    tbot = telegrambot()
    threading.Thread(target=tbot.send_messages, args=(queue,), name="telegram_send_message").start()
    threading.Thread(target=tbot.start_bot, name="telegram_bot").start()