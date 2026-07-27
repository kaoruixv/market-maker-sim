import pandas as pd
import numpy as np

class MetricsTracker:
    def __init__(self):
        self.history = []

    def record(self, time_sec: float, mid_price: float, inventory: int, pnl: float):
        self.history.append({
            'time': time_sec,
            'mid_price': mid_price,
            'inventory': inventory,
            'pnl': pnl
        })

    def summary(self) -> dict:
        if not self.history:
            return {}
        df = pd.DataFrame(self.history)
        
        total_pnl = df['pnl'].iloc[-1]
        
        df['peak'] = df['pnl'].cummax()
        df['drawdown'] = df['pnl'] - df['peak']
        mdd = df['drawdown'].min()

        returns = df['pnl'].diff().fillna(0)
        std_dev = returns.std()
        sharpe = (returns.mean() / std_dev) * np.sqrt(len(df)) if std_dev > 0 else 0

        return {
            'Total PnL': round(total_pnl, 2),
            'Max Drawdown': round(mdd, 2),
            'Approx Sharpe': round(sharpe, 2)
        }
