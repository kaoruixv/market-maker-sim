from dataclasses import dataclass
from enum import Enum


class Side(Enum):
    BID = 1
    ASK = 2


class OrderType(Enum):
    LIMIT = 1
    MARKET = 2


@dataclass
class Order:
    order_id: int
    side: Side
    qty: int
    price: float | None = None
    order_type: OrderType = OrderType.LIMIT
    timestamp: int = 0


@dataclass
class Trade:
    maker_order_id: int
    taker_order_id: int
    price: float
    qty: int
    taker_side: Side
    timestamp: int
