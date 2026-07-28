from market_maker_sim.orderbook.book import OrderBook
from market_maker_sim.orderbook.models import Order, OrderType, Side


def test_price_time_priority():
    ob = OrderBook()
    ob.process_order(Order(1, Side.BID, 10, 100.0))
    ob.process_order(Order(2, Side.BID, 10, 100.0))
    trades = ob.process_order(Order(3, Side.ASK, 15, order_type=OrderType.MARKET))
    assert len(trades) == 2
    assert trades[0].maker_order_id == 1 and trades[0].qty == 10
    assert trades[1].maker_order_id == 2 and trades[1].qty == 5


def test_no_crossed_book_invariant():
    ob = OrderBook()
    ob.process_order(Order(1, Side.ASK, 10, 101.0))
    ob.process_order(Order(2, Side.BID, 10, 99.0))
    ob.process_order(Order(3, Side.BID, 15, 102.0))
    assert ob.best_bid() == 102.0
    assert ob.best_ask() is None
