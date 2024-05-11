import pymongo
import os
import logging
from gateway import RepositoryTradeInterface
from dto import TradeInputDTO, TradeOutputDTO, SellInfoDTO
from pydantic import validate_call

class RepositoryMongoTrade(RepositoryTradeInterface):
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(os.environ['mongo_uri'])
        except Exception as err:
            logging.error(f'Error to connect with mongo {err}')
            raise Exception(err)
        self.db = self.client.BinanceTrade[os.environ['mongo_collection']]

    def insert_position(self, input: TradeInputDTO) -> None:
        logging.debug(f'Inserindo informações no mongodb {input}')

        try:
            self.db.insert_one(input.dict())
        except Exception as err:
            logging.error(f'Error to insert mongodb {err}')
            return None

    def find_position(self, valor: str) -> TradeOutputDTO:
        filter = {
            "symbol": valor,
            "in_position": {"$eq": True}
        }
        try:
            r = self.db.find_one(filter)
        except Exception as err:
            logging.error(f'Error to find position mongodb {err}')
            return None
        
        if not r:
            return None
        
        return TradeOutputDTO(
            id = str(r['_id']),
            symbol = r['symbol'],
            purchase_price = r['purchase_price'],
            date    =   r['date']
        ).dict()

    def find_all_positions(self) -> list[TradeOutputDTO]:
        logging.debug('Starting find_all_position mongodb')
        filter = {
            "in_position": {"$eq": True}
        }

        r = self.db.find(filter)
        
        return_list = list()
        for doc in r:
            return_list.append(
                TradeOutputDTO(
                    id = str(doc['_id']),
                    symbol = doc['symbol'],
                    purchase_price = doc['purchase_price'],
                    date = doc['date']
                ).dict()
            )
        
        return return_list

    def sell_position(self, valor: str, info: SellInfoDTO) -> None:
        logging.debug(f'sell_position informações no mongodb {valor}')
        filter = {
            "symbol": valor,
            "in_position": {"$eq": True}
        }

        novos_valores = {
                "$set": {
                    "in_position": False,
                    "sell_info": info
                }
            }
        
        try:
            self.db.update_one(filter, novos_valores)
        except Exception as err:
            logging.error(f'Error to update mongodb {err}')
            return None