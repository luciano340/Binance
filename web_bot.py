import websocket, json, talib, numpy, logging
import telepot
import os
import random
import time
from decimal import Decimal
from repository.trade_repository import RepositoryMongoTrade
from repository.dto import SellInfoDTO, TradeInputDTO, TradeOutputDTO
import datetime as dt
from collections import deque

class bot_work:
    def __init__(self, coin, client):
        self.client = client
        self.coin = coin
        self.db = RepositoryMongoTrade()
        self.closed_values = deque()
        self.high_values = deque()
        self.low_values = deque()
        self.volume_values = deque()
        self.telebot = telepot.Bot(os.environ['telegram_bot_token'])
        self.price_onhold = None
        self.onhold = False
        self.LAST_STATUS = deque()
        self.first_msg = None
        self.mfi_history = deque()
        self.rsi_history = deque()
        self.__check_first_onhold(coin)

    def __check_first_onhold(self, coin):
        symbol_info = self.db.find_position(coin)

        if symbol_info:
            logging.debug(f'{coin} já em posição ao iniciar process {os.getpid()} {symbol_info}')
            self.price_onhold = symbol_info['purchase_price']
            self.onhold = True
        
    def __send_telegram_msg(self, msg):
        self.telebot.sendMessage(os.environ['telegram_chat_id'], msg)

    def reset_lists(self):
        logging.info(f'Reset informations lists for {self.coin}')
        self.closed_values.clear()
        self.high_values.clear()
        self.low_values.clear()
        self.volume_values.clear()

    def on_open(self, ws):
        logging.info(f'Opened connection on stream for coin {self.coin}')

    def on_close(self, ws):
        logging.debug(f'Closed connection on stream for coin {self.coin}')

    def on_messege(self, ws, messege):
        time.sleep(random.randrange(40, 80)/100)
        logging.debug(f'Debugando msg recebido. {self.coin} - {self.onhold} - PID {os.getpid()}')
        logging.debug(f'Quantidade itens no historico de MFI e RSI {len(self.mfi_history)}')
        #Deafult Values
        RSI_PERIOD = 14
        RSI_OVERBOUGHT = 80
        RSI_OVERSOLD = 15
        MFI_OVERBOUGHT = 85
        MFI_OVERSOLD = 20
        STOP_LOSS = Decimal(0.98)
        #Fazer STOPWIN

        if len(self.LAST_STATUS) >= 4:
            del self.LAST_STATUS[:2]
        
        if len(self.mfi_history) >= 60:
            RSI = (sum(self.rsi_history) / len(self.rsi_history))
            RSI_OVERBOUGHT = RSI + 10
            RSI_OVERSOLD = RSI - 10

            MFI = (sum(self.mfi_history) / len(self.mfi_history))
            MFI_OVERBOUGHT = MFI + 5
            MFI_OVERSOLD = MFI - 5

            logging.debug(f'Mudando valores \nRSI_OVERBOUGHT: {RSI_OVERBOUGHT}\nRSI_OVERSOLD: {RSI_OVERSOLD}\nMSI_OVERBOUGHT: {MFI_OVERBOUGHT}\nMSI_OVERSOLD: {MFI_OVERSOLD}')
            self.rsi_history.pop(0)
            self.mfi_history.pop(0)

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
        last_rsi = float(rsi[-1])
        mfi = talib.MFI(np_high, np_low, np_closes, np_volume, RSI_PERIOD)
        last_mfi = float(mfi[-1])
        self.mfi_history.append(last_mfi)
        self.rsi_history.append(last_rsi)

        logging.info(f'Last for RSI {self.coin}:{last_rsi} - Last MFI for {self.coin}: {last_mfi}')
        logging.debug(f'{self.coin} Oversold {last_rsi <= RSI_OVERSOLD and last_mfi <= MFI_OVERSOLD}')
        logging.debug(f'{self.coin} OVERBOUGHT {last_rsi >= RSI_OVERBOUGHT and last_mfi >= MFI_OVERBOUGHT}')

        #STOP LOSS
        if self.onhold:
            ctp = Decimal(self.client.get_symbol_ticker(symbol=self.coin)['price'])
            if ctp <= self.price_onhold * STOP_LOSS:
                loss = ctp - ctp * STOP_LOSS
                self.onhold = False
                self.price_onhold = None

                sellDTO = SellInfoDTO(
                    sell_price = float(ctp),
                    sell_date = dt.datetime.today(),
                    balance = float(loss)
                )
                self.db.sell_position(self.coin, sellDTO)
                time.sleep(random.randrange(20, 40)/100)
                self.__send_telegram_msg(f'Simulando stop loss {self.coin} vendido. Prejuizo {loss}')


        if last_rsi <= RSI_OVERSOLD and last_mfi <= MFI_OVERSOLD:
            self.LAST_STATUS.append(True)
            msg = f'{self.coin} Em tendencia de long {self.onhold}'
            logging.warn(msg)

            if not self.LAST_STATUS[-1] or not self.first_msg:
                time.sleep(random.randrange(20, 40)/100)
                self.__send_telegram_msg(msg)
                self.first_msg = True

            if not self.onhold:
                logging.debug(f'Realizando compra {self.coin} - {self.onhold} - PID {os.getpid()}')
                self.price_onhold = Decimal(self.client.get_symbol_ticker(symbol=self.coin)['price'])
                self.onhold = True
                inputDTO = TradeInputDTO(
                    symbol = self.coin,
                    purchase_price = float(self.price_onhold),
                    mfi = last_mfi,
                    rsi = last_rsi,
                    date = dt.datetime.today(),
                    in_position = True
                )
                logging.debug(f'DTOINPUT {inputDTO} - {os.getpid()}')
                self.db.insert_position(inputDTO)
                time.sleep(random.randrange(20, 40)/100)
                self.__send_telegram_msg(f'Simulando compra de {self.coin} por ${self.price_onhold}')
                logging.debug(f'compra realizada {self.coin} - {self.onhold} - {os.getpid()}')

        elif last_rsi >= RSI_OVERBOUGHT and last_mfi >= MFI_OVERBOUGHT:
            self.LAST_STATUS.append(False)
            msg = f'{self.coin} Em tendencia de short - Temos em posição? {self.onhold}'
            logging.warn(msg)

            if self.LAST_STATUS[-1] or not self.first_msg:
                time.sleep(random.randrange(20, 40)/100)
                self.__send_telegram_msg(msg)
                self.first_msg = True

            if self.onhold:
                ctp = Decimal(self.client.get_symbol_ticker(symbol=self.coin)['price'])

                if self.price_onhold >= ctp:
                    sell_ticket_price = ctp - self.price_onhold
                    self.onhold = False
                    self.price_onhold = None
                    sellDTO = SellInfoDTO(
                        sell_price = float(ctp),
                        sell_date = dt.datetime.today(),
                        balance = float(sell_ticket_price)
                    )
                    self.db.sell_position(self.coin, sellDTO)
                    time.sleep(random.randrange(20, 40)/100)
                    self.__send_telegram_msg(f'Simulando venda de {self.coin} por ${ctp}. Lucro: {sell_ticket_price.normalize()}')

            
        self.reset_lists()

    def start_stream(self):
        SOCKET = f"wss://stream.binance.com:9443/ws/{self.coin.lower()}@kline_1m"
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(SOCKET, on_open=self.on_open, on_message=self.on_messege)
        ws.run_forever()