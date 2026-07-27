import math
from dataclasses import dataclass
from typing import List
from ..orderbook.models import Order, Side
from ..orderbook.book import OrderBook

@dataclass
class StrategyConfig:
    gamma: float = 0.1      
    sigma: float = 1.0      
    k: float = 1.5          
    position_limit: int = 100
    order_qty: int = 10
    tick_size: float = 0.1
    fixed_spread: float = 1.0 

class BaseMarketMaker:
    def __init__(self, config: StrategyConfig):
        self.config = config
        self.inventory = 0
        self.cash = 0.0
        self.order_id_counter = 1000000

    def update_inventory(self, fill_qty: int, fill_price: float, side: Side):
        if side == Side.BID:
            self.inventory += fill_qty
            self.cash -= fill_qty * fill_price
        else:
            self.inventory -= fill_qty
            self.cash += fill_qty * fill_price
            
    def get_pnl(self, mid_price: float) -> float:
        return self.cash + (self.inventory * mid_price)

class NaiveMarketMaker(BaseMarketMaker):
    def generate_quotes(self, mid_price: float) -> List[Order]:
        orders = []
        half_spread = max(self.config.fixed_spread / 2.0, self.config.tick_size)
        
        if self.inventory + self.config.order_qty <= self.config.position_limit:
            orders.append(Order(self.order_id_counter, Side.BID, self.config.order_qty, round(mid_price - half_spread, 2)))
            self.order_id_counter += 1
            
        if self.inventory - self.config.order_qty >= -self.config.position_limit:
            orders.append(Order(self.order_id_counter, Side.ASK, self.config.order_qty, round(mid_price + half_spread, 2)))
            self.order_id_counter += 1
            
        return orders

class ASMarketMaker(BaseMarketMaker):
    def generate_quotes(self, mid_price: float) -> List[Order]:
        orders = []
        reservation_price = mid_price - (self.inventory * self.config.gamma * (self.config.sigma ** 2))
        spread = (self.config.gamma * (self.config.sigma ** 2)) + ((2.0 / self.config.gamma) * math.log(1.0 + (self.config.gamma / self.config.k)))
        half_spread = max(spread / 2.0, self.config.tick_size)
        
        if self.inventory + self.config.order_qty <= self.config.position_limit:
            orders.append(Order(self.order_id_counter, Side.BID, self.config.order_qty, round(reservation_price - half_spread, 2)))
            self.order_id_counter += 1
            
        if self.inventory - self.config.order_qty >= -self.config.position_limit:
            orders.append(Order(self.order_id_counter, Side.ASK, self.config.order_qty, round(reservation_price + half_spread, 2)))
            self.order_id_counter += 1
            
        return orders
