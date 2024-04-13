import websocket, json, talib, numpy, logging


class bot_work:
    def __init__(self, coin):
        self.coin = coin.lower()
        self.closed_values = list()
        self.high_values = list()
        self.low_values = list()
        self.volume_values = list()

    def reset_lists(self):
        logging.info(f'Reset informations lists for {self.coin}')
        self.closed_values = list()
        self.high_values = list()
        self.low_values = list()
        self.volume_values = list()

    def on_open(self, ws):
        logging.debug(f'Opened connection on stream for coin {self.coin}')
        print(f'Opened connection on stream for coin {self.coin}')

    def on_close(self, ws):
        logging.debug(f'Closed connection on stream for coin {self.coin}')
        print(f'Closed connection on stream for coin {self.coin}')

    def on_messege(self, ws, messege):
        RSI_PERIOD = 14
        RSI_OVERBOUGHT = 80
        RSI_OVERSOLD = 20
        MFI_OVERBOUGHT = 90
        MFI_OVERSOLD = 10

        logging.debug(f'Received messege from websocket {self.coin}')
        infos = json.loads(messege)
        candle = infos['k']
        is_candle_closed = candle['x']
        close = candle['c']
        high = candle['h']
        low =  candle['l']
        volume = candle['q']

        if not is_candle_closed:
            return None
        
        self.closed_values.append(float(close))
        self.high_values.append(float(high))
        self.low_values.append(float(low))
        self.volume_values.append(float(volume))

        if len(self.closed_values) <= RSI_PERIOD:
            return None

        np_closes = numpy.array(self.closed_values)
        np_high = numpy.array(self.high_values)
        np_low = numpy.array(self.low_values)
        np_volume = numpy.array(self.volume_values)

        rsi = talib.RSI(np_closes, RSI_PERIOD)
        last_rsi = rsi[-1]
        mfi = talib.MFI(np_high, np_low, np_closes, np_volume, RSI_PERIOD)
        last_mfi = mfi[-1]

        logging.info(f'Last for {self.coin}: {last_rsi} - Last MFI for {mfi} {self.coin}: {last_mfi}')
        
        if last_rsi <= RSI_OVERSOLD and last_mfi <= MFI_OVERSOLD:
            logging.warn(f'{self.coin} Em tentencia de long')
        elif last_rsi >= RSI_OVERBOUGHT and last_mfi >= MFI_OVERBOUGHT:
            logging.warn(f'{self.coin} Em tentencia de sort')
            
        self.reset_lists()

    def start_stream(self):
        SOCKET = f"wss://stream.binance.com:9443/ws/{self.coin}@kline_1m"
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(SOCKET, on_open=self.on_open, on_message=self.on_messege)
        ws.run_forever()