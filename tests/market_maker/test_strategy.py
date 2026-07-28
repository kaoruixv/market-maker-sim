from market_maker_sim.market_maker.strategy import (
    ASMarketMaker,
    NaiveMarketMaker,
    StrategyConfig,
)
from market_maker_sim.orderbook.models import Side


def test_naive_mm_quotes():
    config = StrategyConfig(fixed_spread=2.0, order_qty=10)
    mm = NaiveMarketMaker(config)
    quotes = mm.generate_quotes(100.0)
    assert len(quotes) == 2
    assert quotes[0].side == Side.BID and quotes[0].price == 99.0
    assert quotes[1].side == Side.ASK and quotes[1].price == 101.0

    mm.inventory = 100
    quotes = mm.generate_quotes(100.0)
    assert len(quotes) == 1
    assert quotes[0].side == Side.ASK


def test_as_mm_skew():
    config = StrategyConfig(gamma=0.1, sigma=1.0, k=1.5, order_qty=10)
    mm = ASMarketMaker(config)

    quotes_zero = mm.generate_quotes(100.0)
    bid_zero = next(q.price for q in quotes_zero if q.side == Side.BID)
    ask_zero = next(q.price for q in quotes_zero if q.side == Side.ASK)

    mm.inventory = 20
    quotes_long = mm.generate_quotes(100.0)
    bid_long = next(q.price for q in quotes_long if q.side == Side.BID)
    ask_long = next(q.price for q in quotes_long if q.side == Side.ASK)

    assert bid_long < bid_zero
    assert ask_long < ask_zero
