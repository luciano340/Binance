import websocket, json, talib, numpy, logging
import telepot
import os
import random
import time
from decimal import Decimal
from repository.trade_repository import RepositoryMongoTrade
from repository.dto import SellInfoDTO, TradeInputDTO, TradeOutputDTO
import datetime as dt

class bot_work:
    def __init__(self, coin, client):
        self.client = client
        self.coin = coin
        self.db = RepositoryMongoTrade()
        self.closed_values = list()
        self.high_values = list()
        self.low_values = list()
        self.volume_values = list()
        self.telebot = telepot.Bot(os.environ['telegram_bot_token'])
        self.price_onhold = None
        self.onhold = False
        self.LAST_STATUS = list()
        self.first_msg = None
        self.mfi_history = list()
        self.rsi_history = list()
        self.__check_first_onhold(coin)

    def __check_first_onhold(self, coin):
        symbol_info = self.db.find_position(coin)

        if symbol_info:
            self.price_onhold = symbol_info['purchase_price']
            self.onhold = True

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

        #Deafult Values
        RSI_PERIOD = 14
        RSI_OVERBOUGHT = 65
        RSI_OVERSOLD = 60
        MFI_OVERBOUGHT = 65
        MFI_OVERSOLD = 60
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
            if ctp <= self.price_onhold * self.STOP_LOSS:
                loss = ctp - ctp * self.STOP_LOSS
                sellDTO = SellInfoDTO(
                    sell_price = float(ctp),
                    sell_date = dt.datetime.today(),
                    balance = float(loss)
                )
                self.db.sell_position(self.coin, sellDTO)
                time.sleep(random.randrange(20, 40)/100)
                self.telebot.sendMessage(os.environ['telegram_chat_id'], f'Simulando stop loss {self.coin} vendido. Prejuizo {loss}')
                self.onhold = False
                self.price_onhold = None

        if last_rsi <= RSI_OVERSOLD and last_mfi <= MFI_OVERSOLD:
            self.LAST_STATUS.append(True)
            msg = f'{self.coin} Em tendencia de long {self.onhold}'
            logging.warn(msg)

            if not self.LAST_STATUS[-1] or not self.first_msg:
                time.sleep(random.randrange(20, 40)/100)
                self.telebot.sendMessage(os.environ['telegram_chat_id'], msg)
                self.first_msg = True

            if not self.onhold:
                logging.debug(f'Realizando compra {self.coin}')
                self.price_onhold = Decimal(self.client.get_symbol_ticker(symbol=self.coin)['price'])
                inputDTO = TradeInputDTO(
                    symbol = self.coin,
                    purchase_price = float(self.price_onhold),
                    mfi = last_mfi,
                    rsi = last_rsi,
                    date = dt.datetime.today(),
                    in_position = True
                )
                logging.debug(f'DTOINPUT {inputDTO}')
                self.db.insert_position(inputDTO)
                time.sleep(random.randrange(20, 40)/100)
                self.telebot.sendMessage(os.environ['telegram_chat_id'], f'Simulando compra de {self.coin} por ${self.price_onhold}')
                self.onhold = True
                logging.debug(f'compra realizada {self.coin} - {self.onhold}')

        elif last_rsi >= RSI_OVERBOUGHT and last_mfi >= MFI_OVERBOUGHT:
            self.LAST_STATUS.append(False)
            msg = f'{self.coin} Em tendencia de short - Temos em posição? {self.onhold}'
            logging.warn(msg)

            if self.LAST_STATUS[-1] or not self.first_msg:
                time.sleep(random.randrange(20, 40)/100)
                self.telebot.sendMessage(os.environ['telegram_chat_id'], msg)
                self.first_msg = True

            if self.onhold:
                ctp = Decimal(self.client.get_symbol_ticker(symbol=self.coin)['price'])

                if self.price_onhold >= ctp:
                    sell_ticket_price = ctp - self.price_onhold
                    sellDTO = SellInfoDTO(
                        sell_price = float(ctp),
                        sell_date = dt.datetime.today(),
                        balance = float(sell_ticket_price)
                    )
                    self.db.sell_position(self.coin, sellDTO)
                    time.sleep(random.randrange(20, 40)/100)
                    self.telebot.sendMessage(os.environ['telegram_chat_id'], f'Simulando venda de {self.coin} por ${ctp}. Lucro: {sell_ticket_price.normalize()}')
                    self.onhold = False
                    self.price_onhold = None
            
        self.reset_lists()

    def start_stream(self):
        SOCKET = f"wss://stream.binance.com:9443/ws/{self.coin.lower()}@kline_1m"
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(SOCKET, on_open=self.on_open, on_message=self.on_messege)
        ws.run_forever()