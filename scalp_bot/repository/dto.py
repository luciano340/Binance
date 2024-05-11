from pydantic import BaseModel
from typing import Optional
from typing_extensions import TypedDict
import datetime as dt

class SellInfoDTO(TypedDict):
    sell_price: float
    sell_date: dt.datetime
    balance: float

class TradeInputDTO(BaseModel):
    symbol: str
    purchase_price: float
    mfi: float
    rsi: float
    date: dt.datetime
    in_position: bool
    sell_info: Optional[SellInfoDTO] = {}
    class Config:
        frozen = True

class TradeOutputDTO(BaseModel):
    id: str
    symbol: str
    purchase_price: float
    date: dt.datetime