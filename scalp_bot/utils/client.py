import requests.adapters
from binance.client import Client
from time import sleep
from prometheus_metrics import function_counter, broker_timer, function_error_counter
import requests, os, logging, random

class BinanceClient:
    def __init__(self) -> None:
        self.client = self.__create_client()

    def __create_client(self) -> Client:
        client = Client(os.environ['api_key_binance'], os.environ['api_secret_biance'])
        request_config = requests.adapters.HTTPAdapter(
            pool_connections=999,
            pool_maxsize=999,
            max_retries=15)
        client.session.mount('https://', request_config)
        client.session.mount('wss://', request_config)
        
        return client

    @function_error_counter.count_exceptions()
    def _run_function(self, function: str, **kwargs) -> dict:
        sleep(random.randrange(60, 120)/100)
        try:
            if kwargs:
                info = eval(f'self.client.{function}')(**kwargs)
            else:
                info = eval(f'self.client.{function}')()
        except Exception as err:
            logging.exception(f'Function {function} - {err}')
            sleep(random.randrange(60, 120)/100)
            self._run_function(function, **kwargs)

        function_counter.labels(function_name=function).inc()
        return info

    get_account_status_metric = broker_timer.labels(endpoint='/sapi/v1/account/status')
    @get_account_status_metric.time()
    def get_account_status(self) -> dict:
        return self._run_function('get_account_status')
    
    get_account_metric = broker_timer.labels(endpoint='/api/v3/account')
    @get_account_metric.time()
    def get_account(self) -> dict:
        return self._run_function('get_account')

    get_exchange_info_metric = broker_timer.labels(endpoint='/api/v3/exchangeInfo')
    @get_exchange_info_metric.time()
    def get_exchange_info(self) -> dict:
        return self._run_function('get_exchange_info')
    
    get_symbol_ticker_metrric = broker_timer.labels(endpoint='/api/v3/ticker/price')
    @get_symbol_ticker_metrric.time()
    def get_symbol_ticker(self, **kwargs) -> dict:
        return self._run_function('get_symbol_ticker', **kwargs)

    get_ticker_metric = broker_timer.labels(endpoint='/api/v3/ticker/24hr')
    @get_ticker_metric.time()
    def get_ticker(self, **kwargs) -> dict:
        return self._run_function('get_ticker', **kwargs)

