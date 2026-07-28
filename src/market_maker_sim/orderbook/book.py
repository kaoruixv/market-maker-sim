from sortedcontainers import SortedDict

from .models import Order, OrderType, Side, Trade


class PriceLevel:
    __slots__ = ["orders", "price", "volume"]

    def __init__(self, price: float):
        self.price = price
        self.orders: dict[int, Order] = {}
        self.volume: int = 0

    def add_order(self, order: Order) -> None:
        self.orders[order.order_id] = order
        self.volume += order.qty

    def remove_order(self, order_id: int) -> None:
        if order_id in self.orders:
            self.volume -= self.orders[order_id].qty
            del self.orders[order_id]


class OrderBook:
    def __init__(self):
        self.bids: SortedDict = SortedDict()
        self.asks: SortedDict = SortedDict()
        self.order_map: dict[int, Order] = {}

    def process_order(self, order: Order) -> list[Trade]:
        if order.order_id in self.order_map:
            raise ValueError(f"Duplicate order ID: {order.order_id}")

        trades = []
        if order.side == Side.BID:
            trades.extend(self._match(order, self.asks, is_bid=True))
            if order.qty > 0 and order.order_type == OrderType.LIMIT:
                self._add_to_book(order, self.bids)
        else:
            trades.extend(self._match(order, self.bids, is_bid=False))
            if order.qty > 0 and order.order_type == OrderType.LIMIT:
                self._add_to_book(order, self.asks)

        return trades

    def cancel_order(self, order_id: int) -> bool:
        if order_id not in self.order_map:
            return False

        order = self.order_map.pop(order_id)
        book = self.bids if order.side == Side.BID else self.asks

        level: PriceLevel = book[order.price]
        level.remove_order(order_id)

        if not level.orders:
            del book[order.price]

        return True

    def best_bid(self) -> float | None:
        return self.bids.peekitem(-1)[0] if self.bids else None

    def best_ask(self) -> float | None:
        return self.asks.peekitem(0)[0] if self.asks else None

    def _match(
        self, taker_order: Order, maker_book: SortedDict, is_bid: bool
    ) -> list[Trade]:
        trades = []

        while taker_order.qty > 0 and maker_book:
            best_price = (
                maker_book.peekitem(0)[0] if is_bid else maker_book.peekitem(-1)[0]
            )

            if taker_order.order_type == OrderType.LIMIT:
                if is_bid and taker_order.price < best_price:
                    break
                if not is_bid and taker_order.price > best_price:
                    break

            level: PriceLevel = maker_book[best_price]

            while taker_order.qty > 0 and level.orders:
                maker_order_id, maker_order = next(iter(level.orders.items()))

                trade_qty = min(taker_order.qty, maker_order.qty)
                taker_order.qty -= trade_qty
                maker_order.qty -= trade_qty
                level.volume -= trade_qty

                trades.append(
                    Trade(
                        maker_order_id=maker_order_id,
                        taker_order_id=taker_order.order_id,
                        price=best_price,
                        qty=trade_qty,
                        taker_side=taker_order.side,
                        timestamp=taker_order.timestamp,
                    )
                )

                if maker_order.qty == 0:
                    del level.orders[maker_order_id]
                    del self.order_map[maker_order_id]

            if not level.orders:
                del maker_book[best_price]

        return trades

    def _add_to_book(self, order: Order, book: SortedDict) -> None:
        if order.price not in book:
            book[order.price] = PriceLevel(order.price)
        book[order.price].add_order(order)
        self.order_map[order.order_id] = order
