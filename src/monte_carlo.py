import pandas as pd
from quotes import avellaneda_stoikov, norm_draw_bounded


def _sample_market_makers(n: int = 4) -> list[str]:
    """
    Generate MM names
    """
    return [f"MM{i}" for i in range(min(n, 10))]


def draw_quotes(
    mid_price: float, volatility: float, market_makers: list[str], std_dev: float=50
):
    """
    Generate one bid/ask quote per market maker at a given price step.
    """
    quotes = []
    for mm in market_makers:
        inventory = norm_draw_bounded(mean=0.0, std=75)
        quote = avellaneda_stoikov(mid_price, inventory, volatility)
        quotes.append({"market_maker": mm, "inventory": inventory, **quote})
    return quotes


def BBO_MID(quotes: list) -> float:
    """
    Compute the effective mid price from BBO.
    """
    best_bid = max(q["bid"] for q in quotes)
    best_ask = min(q["ask"] for q in quotes)
    return (best_bid + best_ask) / 2.0


def simulate_paths( df: pd.DataFrame, num_mm: int = 4, n: int = 200,) :
    """
    Run n Monte Carlo simulations of path-dependent prices driven by MM quoting.

    At each time step the simulated price is computed by:
      1. Calculating the real DoD return
      2. Plungging the return in the simulated price and draw quotes.
      3. Updating the simulated price to the effective mid of the quotes.
    """
    prices = df["close"].tolist()
    vols = df["vol"].tolist()
    dates = df.index

    paths = []

    for _ in range(n):
        market_makers = _sample_market_makers(num_mm)
        path_price = prices[0]
        records: list[dict] = []

        for i in range(len(prices)):
            real_price = prices[i]
            vol = vols[i]

            # Adjust price to real DoD
            prev_real = prices[i - 1] if i > 0 else real_price
            adjusted_price = path_price * (real_price / prev_real)

            # Generate quotes
            quotes = draw_quotes(adjusted_price, vol, market_makers)
            effective_mid = BBO_MID(quotes)

            records.append(
                {
                    "date": dates[i],
                    "real_price": real_price,
                    "simulated_price": effective_mid,
                }
            )

            path_price = effective_mid

        paths.append(pd.DataFrame(records).set_index("date"))

    return paths


def simulate_explicit_path(df, num_mm=4):
    """
    Single path simulation that captures both BBO-level and per-MM detail.
    """
    prices = df["close"].tolist()
    vols   = df["vol"].tolist()
    dates  = df.index

    market_makers = _sample_market_makers(num_mm)
    path_price    = prices[0]
    bbo_records     = []
    scatter_records = []

    for i in range(len(prices)):
        real_price = prices[i]
        vol        = vols[i]
        prev_real  = prices[i - 1] if i > 0 else real_price
        adjusted   = path_price * (real_price / prev_real)

        quotes     = draw_quotes(adjusted, vol, market_makers)
        best_bid   = max(q["bid"] for q in quotes)
        best_ask   = min(q["ask"] for q in quotes)
        eff_mid    = (best_bid + best_ask) / 2.0
        spread_bps = (best_ask - best_bid) / eff_mid * 10_000

        bbo_records.append({
            "date":       dates[i],
            "price": round(real_price, 2),
            "sim_mid":    round(eff_mid, 2),
            "best_bid":   round(best_bid, 2),
            "best_ask":   round(best_ask, 2),
            "spread_bps": round(spread_bps, 2),
        })

        # Scatter
        for q in quotes:
            scatter_records.append({
                "inventory":  q["inventory"],
                "vol":        vol,
                "spread_bps": spread_bps,
            })

        path_price = eff_mid

    bbo_df     = pd.DataFrame(bbo_records).set_index("date")
    scatter_df = pd.DataFrame(scatter_records)
    return bbo_df, scatter_df
