import math
import statistics
from collections import deque


class PerformanceLogger:
    def __init__(self):
        self.realized_pnl = 0.0

    def log_trade(self, pnl_impact):
        self.realized_pnl += pnl_impact

    def get_total_pnl(self, current_inventory=0, mid_price=0.0):
        return self.realized_pnl + (current_inventory * mid_price)


class AvellanedaStoikovAgent:
    def __init__(self, starting_cash=10000.0, max_inventory=20, vol_window=10):
        self.cash = starting_cash
        self.inventory = 0
        self.gamma = 0.1
        self.k = 1.5
        self.max_inventory = max_inventory

        # New Dynamic Volatility Engine
        self.vol_window = vol_window
        self.price_history = deque(maxlen=vol_window)

        self.logger = PerformanceLogger()

    def get_quotes(self, mid_price):
        # 1. Update market memory
        self.price_history.append(mid_price)

        # 2. Calculate dynamic sigma (volatility)
        if len(self.price_history) < 2:
            current_sigma = 1.0  # Fallback until we have enough data
        else:
            current_sigma = statistics.stdev(self.price_history)
            # Floor the volatility so the spread doesn't collapse to 0 in perfectly flat markets
            current_sigma = max(current_sigma, 0.1)

        # 3. Calculate reservation price and optimal spread using dynamic sigma
        reservation_price = mid_price - (
            self.inventory * self.gamma * (current_sigma**2)
        )
        spread = (self.gamma * (current_sigma**2)) + (2 / self.gamma) * math.log(
            1 + (self.gamma / self.k)
        )

        # 4. Apply hard inventory constraints via infinite pricing
        if self.inventory >= self.max_inventory:
            bid = -float("inf")
        else:
            bid = reservation_price - (spread / 2)

        if self.inventory <= -self.max_inventory:
            ask = float("inf")
        else:
            ask = reservation_price + (spread / 2)

        return bid, ask

    def on_trade_fill(self, timestamp, execution_price, quantity, side, mid_price):
        if side == "BUY":
            self.inventory += quantity
            cash_impact = -(execution_price * quantity)
        elif side == "SELL":
            self.inventory -= quantity
            cash_impact = execution_price * quantity

        self.cash += cash_impact
        self.logger.log_trade(cash_impact)
