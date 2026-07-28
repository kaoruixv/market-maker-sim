from dataclasses import dataclass
from typing import List

@dataclass
class TradeSnapshot:
    timestamp: float
    mid_price: float
    bid_price: float
    ask_price: float
    inventory_position: int
    realized_pnl: float
    unrealized_pnl: float

class PerformanceLogger:
    def __init__(self):
        self.history: List[TradeSnapshot] = []

    def record_snapshot(self, snapshot: TradeSnapshot):
        self.history.append(snapshot)

    def get_total_pnl(self) -> float:
        if not self.history:
            return 0.0
        latest_snapshot = self.history[-1]
        return latest_snapshot.realized_pnl + latest_snapshot.unrealized_pnl
