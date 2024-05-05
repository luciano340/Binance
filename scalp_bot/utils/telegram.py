import telebot
import os
import random
import time
import logging
import threading
from queue import Queue
from prometheus_client import Counter, Gauge, Summary, Histogram
from timeit import default_timer as timer
from repository.trade_repository import RepositoryMongoTrade

class telegrambot:
    __msg_queue = Gauge('telegram_msg_queue', 'Total of messages on the python queue to telegram bot')
    __status_code = Counter('telegram_responses', 'Response quantity per status code', ['endpoint', 'status_code'])
    __response_time = Histogram('telegram_response_time', 'Check the response time of Telegram API requests', ['endpoint'])
    def __init__(self) -> None:
        self.telebot = telebot.TeleBot(os.environ['telegram_bot_token'])    
        self.__init_commands()

    def send_messages(self, queue: Queue) -> None:
        while True:
            total_msg = queue.qsize()
            telegrambot.__msg_queue.set(total_msg)
            logging.debug(f'Total of msg on the python telegram queue {total_msg}')
            if total_msg >= 1:
                msg = queue.get()
                try:
                    start = timer()
                    self.telebot.send_message(os.environ['telegram_chat_id'], msg)
                    end = timer()
                    total_time = start - end
                    metrics_time = telegrambot.__response_time.labels(endpoint='/sendMessage')
                    metrics_time.observe(total_time)
                    metrics_statuscode = telegrambot.__status_code.labels(endpoint='/sendMessage', status_code=200)
                    metrics_statuscode.inc(1)
                    logging.debug(f'Response time for msg {msg} {total_time}')
                except Exception as err:
                    logging.error(f'Error to send msg on telegram {type(err)} - {err}')
                    metrics_statuscode = telegrambot.__status_code.labels(endpoint='/sendMessage', status_code=429)
                    metrics_statuscode.inc(1)
                    queue.put(msg)
                    time.sleep(30)
            time.sleep(3.5)

    def __init_commands(self):
        self.telebot.message_handler(commands=["check_positions"])(self.__check_coins_inposition)
        self.telebot.message_handler(commands=["check_running_coins"])(self.__check_proccess)

    def __check_coins_inposition(self, message):
        text = message.text.split()
    
        if len(text) == 1:
            self.telebot.send_message(os.environ['telegram_chat_id'], "Vai retornar todas as posições!")
            return

        mongo = RepositoryMongoTrade()
        coin = text[1]
        r = mongo.find_position(coin)

        if not r:
            self.telebot.send_message(os.environ['telegram_chat_id'], f"Não temos a {coin} em posição")
            return 

        self.telebot.send_message(os.environ['telegram_chat_id'], f"{r}")
        mongo.client.close()

    def __check_proccess(self, message):
        coins_list = ''
        for i in threading.enumerate():
            name = i.name
            if 'scalp' in name:
                coin = name.split('_')[2]
                coins_list = f'{coins_list}\n{coin}'

        self.telebot.send_message(os.environ['telegram_chat_id'], f"Atualmente o bot está trabalho com as seguintes moedas:\n{coins_list}")
        
    def start_bot(self):
        self.telebot.polling()