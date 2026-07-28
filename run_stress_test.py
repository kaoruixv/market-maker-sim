import math
import random
import statistics

from src.market_maker.strategy import AvellanedaStoikovAgent


def run_single_simulation(toxic_flow=True):
    agent = AvellanedaStoikovAgent(starting_cash=10000.0)
    mid_price = 100.0

    for step in range(1, 101):
        # STEP 3: Adverse Selection (Toxic Flow / Flash Crash)
        if toxic_flow and 40 <= step <= 60:
            # For 20 ticks, the market aggressively trends downward.
            # The downward pressure (-1.5) heavily outweighs upward ticks (+0.1).
            mid_price += random.uniform(-1.5, 0.1)
        else:
            # Normal balanced market
            mid_price += random.uniform(-0.5, 0.5)

        bid, ask = agent.get_quotes(mid_price)

        delta_bid = mid_price - bid
        delta_ask = ask - mid_price

        # Calculate Poisson fill probabilities
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

    return agent.logger.get_total_pnl(agent.inventory, mid_price)


def run_stress_test(iterations=1000):
    print(f"Running Toxic Flow Stress Test ({iterations} iterations)...")
    pnl_results = [run_single_simulation(toxic_flow=True) for _ in range(iterations)]

    print("\n--- Crash Survival Risk Profile ---")
    print(f"Mean PnL:           ${statistics.mean(pnl_results):.2f}")
    print(f"Standard Deviation: ${statistics.stdev(pnl_results):.2f}")
    print(f"Min PnL (Max Loss): ${min(pnl_results):.2f}")
    print(f"Max PnL:            ${max(pnl_results):.2f}")


if __name__ == "__main__":
    run_stress_test()
