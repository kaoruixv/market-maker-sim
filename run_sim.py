import random

from src.market_maker.strategy import AvellanedaStoikovAgent


def run_simulation():
    # Initialize our strategy with $10,000
    agent = AvellanedaStoikovAgent(starting_cash=10000.0)
    mid_price = 100.0

    print("Starting market simulation...")

    # Simulate 100 market events
    for step in range(1, 101):
        # 1. Simulate market volatility (Random Walk)
        mid_price += random.uniform(-0.5, 0.5)

        # 2. Simulate toxic vs non-toxic order flow hitting our quotes
        side = random.choice(["BUY", "SELL"])
        quantity = random.randint(1, 10)

        # 3. Assume we capture a $0.10 spread on execution
        execution_price = mid_price - 0.10 if side == "BUY" else mid_price + 0.10

        # 4. Feed it into our event-driven architecture
        agent.on_trade_fill(
            timestamp=float(step),
            execution_price=execution_price,
            quantity=quantity,
            side=side,
            mid_price=mid_price,
        )

    # Output the analytics
    print(f"Simulation complete. {len(agent.logger.history)} trades recorded.")
    print(f"Final Inventory Position: {agent.inventory} units")
    print(
        f"Final Total PnL (Realized + Unrealized): ${agent.logger.get_total_pnl():.2f}"
    )


if __name__ == "__main__":
    run_simulation()
