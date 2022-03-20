import websocket
import logging

class bot_work:
    def __init__(self, coin):
        seelf.coin = coin

    def on_open(self, ws):
        logging.info(f'Opened connection on stream for coin {self.coin}')
        print(f'Opened connection on stream for coin {self.coin}')

    def on_close(self, ws):
        logging.info(f'Closed connection on stream for coin {self.coin}')
        print(f'Closed connection on stream for coin {self.coin}')

    def on_messege(self, ws, messege):
        logging.info(f'Received messege from websocket {self.coin}')
        print(f'Received messege from websocket {self.coin}')
        
    def start_stream(self):
        SOCKET = f"wss://stream.binance.com:9443/ws/{self.coin}@kline_1m"
        RSI_PERIOD = 15
        ws = websocket(SOCKET, on_open=self.on_open, on_close=, on_message=)
        ws.run_forever()