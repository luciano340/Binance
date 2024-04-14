from binance.client import Client
from web_bot import bot_work
from threading import Thread
import logging
import re
import os
import random
import time

logging.basicConfig(filename='general.log', encoding='utf-8', level=logging.DEBUG,
format='%(asctime)s - %(levelname)s - %(pathname)s on Line: %(lineno)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S')

try:
    client = Client(os.environ['api_key_binance'], os.environ['api_secret_biance'])
except Exception as err:
    logging.error(f'Connection Error {err}')
    exit(1)

status = client.get_account_status()
logging.debug(f'Connection status {status["data"]}')

info = client.get_account()
logging.debug(f'Account information: \n{info}')

assets = client.get_exchange_info()

# asset_list = ['BTCUSDT', 'MATICUSDT', 'ETHUSDT', 'LINKUSDT', 'BNBUSDT', 'SOLUSDT']

asset_list = list()
for k in assets['symbols']:
    if re.search(r'[0-9]$', k['symbol']):
        continue

    if not re.search(r'USDT$', k['symbol']):
        continue
    
    try:
        ticker_info = client.get_ticker(symbol=k['symbol'])
    except Exception as err:
        print(f'{err} - {k['symbol']}')
        continue
    
    print(f'Price {k['symbol']} {ticker_info['lastPrice']}')
    if float(ticker_info['lastPrice']) < 0.50:
        continue
    
    print(f'Volume {k['symbol']} {ticker_info['quoteVolume']}')
    if float(ticker_info['quoteVolume']) < 24000:
        continue

    asset_list.append(k['symbol'])
    print(asset_list)
    time.sleep(random.randrange(50, 80)/100)

logging.debug(f'Total assets to be used: {len(asset_list)}')
logging.info(f'Assents found {asset_list}')

if __name__ == '__main__':
    for asset in asset_list:
        time.sleep(random.randrange(90, 150)/100)
        bot = bot_work(asset, client)
        Thread(target=bot.start_stream).start()