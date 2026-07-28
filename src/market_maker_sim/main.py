import matplotlib.pyplot as plt
import pandas as pd

from market_maker_sim.market_data.generator import GeneratorConfig, OrderFlowGenerator
from market_maker_sim.market_maker.strategy import (
    ASMarketMaker,
    NaiveMarketMaker,
    StrategyConfig,
)
from market_maker_sim.orderbook.book import OrderBook
from market_maker_sim.risk_and_pnl.metrics import MetricsTracker


def run_sim(mm_class, steps=10000):
    book = OrderBook()
    # High lambda vs mu creates a thick book. Theta keeps it from infinite growth.
    gen_config = GeneratorConfig(mu=5.0, lam=15.0, theta=0.5, seed=42)
    generator = OrderFlowGenerator(gen_config, book)

    mm_config = StrategyConfig(
        gamma=0.1, sigma=0.5, k=1.5, order_qty=5, fixed_spread=0.2
    )
    mm = mm_class(mm_config)
    metrics = MetricsTracker()

    mm_active_orders = {}

    for step in range(steps):
        best_bid = book.best_bid()
        best_ask = book.best_ask()
        mid_price = (
            (best_bid + best_ask) / 2.0
            if best_bid and best_ask
            else gen_config.start_price
        )

        # 1. MM cancels old quotes
        for oid in list(mm_active_orders.keys()):
            book.cancel_order(oid)
            del mm_active_orders[oid]

        # 2. MM places new quotes based on current state
        quotes = mm.generate_quotes(mid_price)
        for q in quotes:
            book.process_order(q)
            mm_active_orders[q.order_id] = q

        # 3. Market event occurs
        t, order, cancel_id = generator.next_event()
        if order:
            trades = book.process_order(order)
            for trade in trades:
                if trade.maker_order_id in mm_active_orders:
                    # MM order was filled
                    mm_order = mm_active_orders[trade.maker_order_id]
                    mm.update_inventory(trade.qty, trade.price, mm_order.side)
                    # Treat as fill/kill for simplicity in this loop
                    del mm_active_orders[trade.maker_order_id]
        elif cancel_id and cancel_id != -1 and cancel_id not in mm_active_orders:
            book.cancel_order(cancel_id)

        # 4. Record state
        if step % 50 == 0:
            metrics.record(t, mid_price, mm.inventory, mm.get_pnl(mid_price))

    return metrics


if __name__ == "__main__":
    print("Running Baseline (Naive) MM...")
    naive_metrics = run_sim(NaiveMarketMaker)

    print("Running Avellaneda-Stoikov (Inventory-Aware) MM...")
    as_metrics = run_sim(ASMarketMaker)

    print("\n--- RESULTS OVER 10,000 EVENTS ---")
    print(f"Naive Strategy: {naive_metrics.summary()}")
    print(f"A-S Strategy:   {as_metrics.summary()}")

    df_naive = pd.DataFrame(naive_metrics.history)
    df_as = pd.DataFrame(as_metrics.history)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # PnL Plot
    ax1.plot(df_naive["time"], df_naive["pnl"], label="Naive PnL", color="red")
    ax1.plot(df_as["time"], df_as["pnl"], label="Avellaneda-Stoikov PnL", color="blue")
    ax1.set_title("Cumulative P&L Comparison")
    ax1.set_ylabel("P&L ($)")
    ax1.legend()
    ax1.grid(True)

    # Inventory Plot
    ax2.plot(
        df_naive["time"],
        df_naive["inventory"],
        label="Naive Inventory",
        color="red",
        alpha=0.6,
    )
    ax2.plot(
        df_as["time"],
        df_as["inventory"],
        label="A-S Inventory",
        color="blue",
        alpha=0.6,
    )
    ax2.set_title("Inventory Drift")
    ax2.set_xlabel("Simulation Time (seconds)")
    ax2.set_ylabel("Position (Lots)")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig("results/backtest_results.png")
    print("\nPlot saved to results/backtest_results.png")
