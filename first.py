from binance.client import Client
from secrets import api_key, api_secret
import logging

logging.basicConfig(filename='general.log', encoding='utf-8', level=logging.DEBUG,
format='%(asctime)s - %(levelname)s - %(pathname)s on Line: %(lineno)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S')

try:
    client = Client(api_key, api_secret)
except Exception as err:
    loggin.error(f'Connection Error {err}')
    exit(1)

status = client.get_account_status()
logging.debug(f'Connection status {status["data"]}')

info = client.get_account()
logging.debug(f'Account information: \n{info}')

assets = client.futures_exchange_info()

asset_list = list()
for k in assets['symbols']:
    asset_list.append(k['symbol'])

logging.debug(f'Total assets to be used: {len(asset_list)}')
logging.info(f'Assents found {asset_list}')