from binance.client import Client
from web_bot import bot_work
from threading import Thread
import logging
import re
import os

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

assets = client.futures_exchange_info()

asset_list = list()
for k in assets['symbols']:
    if re.search(r'[0-9]$', k['symbol']):
        continue

    asset_list.append(k['symbol'])

logging.debug(f'Total assets to be used: {len(asset_list)}')
logging.info(f'Assents found {asset_list}')

if __name__ == '__main__':
    for asset in asset_list:
        bot = bot_work(asset)
        Thread(target=bot_work.start_stream())