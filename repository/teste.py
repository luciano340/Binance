import pymongo
import os
import logging
from gateway import RepositoryTradeInterface
from dto import TradeInputDTO, TradeOutputDTO, SellInfoDTO
from pydantic import validate_call
import datetime as dt
from decimal import Decimal

client = pymongo.MongoClient(os.environ['mongo_uri'])
db = client.BinanceTrade[os.environ['mongo_collection']]

class mongodb:
    def __init__(self):
        pass
    
    @validate_call
    def insert(self, input: TradeInputDTO):
        print(input)
        db.insert_one(input.dict())
    
ab = TradeInputDTO(
    symbol = 'BANDUSDT',
    purchase_price = 1.579,
    mfi = 41.62529449200918,
    rsi = 50.0,
    date = dt.datetime.today(),
    in_position = True
)

mongo = mongodb()
mongo.insert(ab)