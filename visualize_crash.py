import math
import random

import matplotlib.pyplot as plt

from src.market_maker.strategy import AvellanedaStoikovAgent


def run_visual_crash():
    agent = AvellanedaStoikovAgent(starting_cash=10000.0)
    mid_price = 100.0

    # Tracking lists for plotting
    prices, bids, asks, inventories = [], [], [], []

    for step in range(1, 101):
        # Trigger the 20-tick crash
        if 40 <= step <= 60:
            mid_price += random.uniform(-1.5, 0.1)
        else:
            mid_price += random.uniform(-0.5, 0.5)

        bid, ask = agent.get_quotes(mid_price)

        # Clean up infinite values for plotting purposes
        plot_bid = bid if bid != -float("inf") else None
        plot_ask = ask if ask != float("inf") else None

        prices.append(mid_price)
        bids.append(plot_bid)
        asks.append(plot_ask)
        inventories.append(agent.inventory)

        delta_bid = mid_price - bid
        delta_ask = ask - mid_price

        prob_bid = (
            min(1.0, math.exp(-agent.k * delta_bid)) if bid != -float("inf") else 0.0
        )
        prob_ask = (
            min(1.0, math.exp(-agent.k * delta_ask)) if ask != float("inf") else 0.0
        )

        qty = random.randint(1, 10)

        if random.random() < prob_bid:
            agent.on_trade_fill(step, bid, qty, "BUY", mid_price)
        if random.random() < prob_ask:
            agent.on_trade_fill(step, ask, qty, "SELL", mid_price)

    # --- Plotting the Results ---
    _fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 8), gridspec_kw={"height_ratios": [3, 1]}
    )

    # Top Plot: Market Data & Quotes
    ax1.plot(prices, label="Mid Price", color="black", linewidth=2)
    ax1.plot(bids, label="Agent Bid", color="green", linestyle="--", marker=".")
    ax1.plot(asks, label="Agent Ask", color="red", linestyle="--", marker=".")
    ax1.axvspan(40, 60, color="grey", alpha=0.2, label="Toxic Flow (Crash)")
    ax1.set_title("Avellaneda-Stoikov Market Maker: Surviving a Flash Crash")
    ax1.set_ylabel("Price ($)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Bottom Plot: Inventory Management
    ax2.plot(inventories, label="Net Inventory", color="purple", drawstyle="steps-post")
    ax2.axhline(agent.max_inventory, color="red", linestyle=":", label="Max Long Limit")
    ax2.axhline(
        -agent.max_inventory, color="red", linestyle=":", label="Max Short Limit"
    )
    ax2.axhline(0, color="black", linewidth=0.5)
    ax2.set_xlabel("Simulation Tick")
    ax2.set_ylabel("Shares Held")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("crash_survival_plot.png", dpi=300)
    print("Visualization saved as 'crash_survival_plot.png'")


if __name__ == "__main__":
    run_visual_crash()
