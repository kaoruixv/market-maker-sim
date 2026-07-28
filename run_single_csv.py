import csv
import math
import random

from src.market_maker.strategy import AvellanedaStoikovAgent


def generate_csv_run():
    print("Running single AS simulation with CSV export...")
    agent = AvellanedaStoikovAgent(starting_cash=10000.0)
    mid_price = 100.0

    with open("simulation_ticks.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Step",
                "MidPrice",
                "Quote_Bid",
                "Quote_Ask",
                "Action",
                "Trade_Qty",
                "Inventory",
                "Cash",
                "Total_PnL",
            ]
        )

        for step in range(1, 101):
            mid_price += random.uniform(-0.5, 0.5)
            bid, ask = agent.get_quotes(mid_price)

            delta_bid = mid_price - bid
            delta_ask = ask - mid_price

            prob_bid_fill = min(1.0, math.exp(-agent.k * delta_bid))
            prob_ask_fill = min(1.0, math.exp(-agent.k * delta_ask))

            qty = random.randint(1, 10)
            action = "NONE"
            trade_qty = 0

            if random.random() < prob_bid_fill:
                agent.on_trade_fill(step, bid, qty, "BUY", mid_price)
                action = "BUY"
                trade_qty = qty

            if random.random() < prob_ask_fill:
                agent.on_trade_fill(step, ask, qty, "SELL", mid_price)
                action = "SELL" if action == "NONE" else "BOTH"
                trade_qty = qty if action == "SELL" else trade_qty + qty

            current_pnl = agent.logger.get_total_pnl()

            writer.writerow(
                [
                    step,
                    f"{mid_price:.3f}",
                    f"{bid:.3f}",
                    f"{ask:.3f}",
                    action,
                    trade_qty,
                    agent.inventory,
                    f"{agent.cash:.2f}",
                    f"{current_pnl:.2f}",
                ]
            )

    print("Export complete: simulation_ticks.csv")


if __name__ == "__main__":
    generate_csv_run()
