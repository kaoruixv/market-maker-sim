import math
import os
import random
import statistics

from src.market_maker.strategy import AvellanedaStoikovAgent


def run_single_simulation():
    agent = AvellanedaStoikovAgent(starting_cash=10000.0)
    mid_price = 100.0

    for step in range(1, 101):
        mid_price += random.uniform(-0.5, 0.5)

        bid, ask = agent.get_quotes(mid_price)

        delta_bid = mid_price - bid
        delta_ask = ask - mid_price

        # Guard against infinite distance calculations when inventory is maxed
        prob_bid_fill = (
            min(1.0, math.exp(-agent.k * delta_bid)) if bid != -float("inf") else 0.0
        )
        prob_ask_fill = (
            min(1.0, math.exp(-agent.k * delta_ask)) if ask != float("inf") else 0.0
        )

        quantity = random.randint(1, 10)

        if random.random() < prob_bid_fill:
            agent.on_trade_fill(step, bid, quantity, "BUY", mid_price)

        if random.random() < prob_ask_fill:
            agent.on_trade_fill(step, ask, quantity, "SELL", mid_price)

    # Mark the final inventory to market
    return agent.logger.get_total_pnl(agent.inventory, mid_price)


def run_monte_carlo(iterations=1000):
    print(f"Running Realistic AS Monte Carlo ({iterations} iterations)...")
    pnl_results = [run_single_simulation() for _ in range(iterations)]

    # Calculate stats
    mean_pnl = statistics.mean(pnl_results)
    stdev_pnl = statistics.stdev(pnl_results)
    variance_pnl = statistics.variance(pnl_results)
    min_pnl = min(pnl_results)
    max_pnl = max(pnl_results)

    # Format the output string
    output = (
        f"--- Realistic Statistical Risk Profile ---\n"
        f"Mean PnL:           ${mean_pnl:.2f}\n"
        f"Standard Deviation: ${stdev_pnl:.2f}\n"
        f"Variance:           ${variance_pnl:.2f}\n"
        f"Min PnL:            ${min_pnl:.2f}\n"
        f"Max PnL:            ${max_pnl:.2f}\n"
    )

    # Print to console (so you can still see it in the GitHub Actions UI)
    print(output)

    # THE FIX: Save the output to a file in the results folder
    os.makedirs("results", exist_ok=True)
    with open("results/monte_carlo_summary.txt", "w") as file:
        file.write(output)


if __name__ == "__main__":
    run_monte_carlo()
