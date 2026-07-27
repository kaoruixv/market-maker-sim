# market-maker-sim

A limit order book engine and market-making strategy simulator designed to evaluate the Avellaneda-Stoikov (inventory-aware) strategy against a naive symmetric baseline under stochastic order flow.

**Key Finding:** Under continuous mean-reverting stochastic flow, the Avellaneda-Stoikov strategy significantly outperforms the naive strategy by skewing quotes to control inventory drift, heavily minimizing adverse selection costs and completely avoiding maximum position limit breaches.

## Architecture
- **`orderbook/`**: O(1) matching engine utilizing price-level hash maps and Red-Black trees (`sortedcontainers`) for O(log N) best-bid/offer lookup. Enforces strict price-time priority.
- **`market_data/`**: Calibrated synthetic order flow generator utilizing the Gillespie algorithm to simulate competing Poisson processes for limit orders, market orders, and cancellations.
- **`market_maker/`**: Direct implementation of the Avellaneda-Stoikov optimal spread and reservation price equations, benchmarked against a baseline fixed-spread quoter.
- **`risk_and_pnl/`**: Marks inventory to mid-price continuously to track PnL, Maximum Drawdown, and Sharpe ratios.

## Quickstart

```bash
git clone [https://github.com/kaoruixv/market-maker-sim.git](https://github.com/kaoruixv/market-maker-sim.git)
cd market-maker-sim
uv sync
uv run pytest tests/
uv run python src/market_maker_sim/main.py
