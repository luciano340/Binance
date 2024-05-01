import telepot
import os
import random
import time
import logging
from queue import Queue
from prometheus_client import Counter, Gauge, Summary, Histogram
from timeit import default_timer as timer

class telegrambot:
    __msg_queue = Gauge('telegram_msg_queue', 'Total of messages on the python queue to telegram bot')
    __status_code = Counter('telegram_responses', 'Response quantity per status code', ['endpoint', 'status_code'])
    __response_time = Histogram('telegram_response_time', 'Check the response time of Telegram API requests', ['endpoint'])
    def __init__(self) -> None:
        self.telebot = telepot.Bot(os.environ['telegram_bot_token'])    

    def send_messages(self, queue: Queue) -> None:
        while True:
            total_msg = queue.qsize()
            telegrambot.__msg_queue.set(total_msg)
            logging.debug(f'Total of msg on the python telegram queue {total_msg}')
            print(f'Total of msg on the python telegram queue {total_msg}')
            if total_msg >= 1:
                msg = queue.get()
                try:
                    start = timer()
                    self.telebot.sendMessage(os.environ['telegram_chat_id'], msg)
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
            time.sleep(1.5)