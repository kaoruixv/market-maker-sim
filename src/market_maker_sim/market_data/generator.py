import random
from dataclasses import dataclass

from ..orderbook.book import OrderBook
from ..orderbook.models import Order, OrderType, Side


@dataclass
class GeneratorConfig:
    mu: float = 2.0
    lam: float = 5.0
    theta: float = 0.1
    tick_size: float = 0.1
    avg_qty: int = 10
    start_price: float = 100.0
    seed: int = 42


class OrderFlowGenerator:
    def __init__(self, config: GeneratorConfig, book: OrderBook):
        self.config = config
        self.book = book
        self.rng = random.Random(config.seed)
        self.current_time = 0.0
        self.order_id_counter = 1
        self._seed_initial_book()

    def next_event(self) -> tuple[float, Order | None, int | None]:
        active_orders = len(self.book.order_map)
        rate_cancel = self.config.theta * active_orders
        total_rate = self.config.mu + self.config.lam + rate_cancel

        if total_rate == 0:
            total_rate = self.config.lam

        dt = self.rng.expovariate(total_rate)
        self.current_time += dt
        rand_val = self.rng.random() * total_rate

        if rand_val < self.config.mu:
            return self.current_time, self._gen_order(OrderType.MARKET), None
        elif rand_val < self.config.mu + self.config.lam:
            return self.current_time, self._gen_order(OrderType.LIMIT), None
        else:
            cancel_id = (
                self.rng.choice(list(self.book.order_map.keys()))
                if self.book.order_map
                else -1
            )
            return self.current_time, None, cancel_id

    def _seed_initial_book(self) -> None:
        for _ in range(50):
            self.book.process_order(self._gen_order(OrderType.LIMIT, force_price=True))

    def _gen_order(self, order_type: OrderType, force_price: bool = False) -> Order:
        side = self.rng.choice([Side.BID, Side.ASK])
        qty = max(1, int(self.rng.expovariate(1.0 / self.config.avg_qty)))

        if order_type == OrderType.MARKET:
            order = Order(self.order_id_counter, side, qty, order_type=order_type)
        else:
            best_bid = self.book.best_bid()
            best_ask = self.book.best_ask()
            mid = (
                self.config.start_price
                if not best_bid or not best_ask or force_price
                else (best_bid + best_ask) / 2.0
            )
            tick_offset = self.rng.randint(1, 5) * self.config.tick_size
            price = round(
                mid - tick_offset if side == Side.BID else mid + tick_offset, 2
            )
            order = Order(self.order_id_counter, side, qty, price, order_type)

        self.order_id_counter += 1
        return order
