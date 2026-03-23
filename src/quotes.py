import math
import numpy as np
from scipy.stats import truncnorm



def norm_draw_bounded(mean=0, std=50, low=-100, high=100):
    """
    Draw a value from a normal bounded in [low, high].
    """
    a = (low - mean) / std
    b = (high - mean) / std
    return truncnorm.rvs(a, b, loc=mean, scale=std)

def avellaneda_stoikov(mid_price: float, inventory: float, sigma: float, gamma: float = 50.0, T: float = 1.0,):
    """
    Compute bid/ask quotes using Avellaneda-Stoikov model (2008).

    The model adjusts a base half-spread depending on:
      1. Volatility risk: wider spread when vol is high.
      2. Inventory skew : asymmetric bid/ask to reach flat inventory.
      3. Risk aversion: discretionnary
    """

    # Convert annualised vol to daily vol (252 trading days)
    sigma_daily = sigma / np.sqrt(252)
    var_daily = sigma_daily ** 2

    # Base half-spread from volatility and time horizon
    half_spread = max((gamma * var_daily * T) / 2.0, 0)

    # Inventory skew factor
    k = max(2.0 + 8.0 * (1.0 - sigma), 0.1)

    if inventory == 0.0:  skew_factor = 0.0
    else:
        exp_factor = (np.exp(k * abs(inventory) / 100.0) - 1.0) / (np.exp(k) - 1.0)
        skew_factor = math.copysign(exp_factor, inventory)

    # Skewed half spread
    delta_skew = skew_factor * half_spread

    # Quotes
    bid = mid_price * (1.0 - (half_spread + delta_skew))
    ask = mid_price * (1.0 + (half_spread - delta_skew))

    # Measures
    spread_bps = 2.0 * half_spread * 10_000.0
    skew_pct   = skew_factor * 100.0

    return {
        "bid":        bid,
        "ask":        ask,
        "mid":        mid_price,
        "spread_bps": spread_bps,
        "skew_pct":   skew_pct,
    }
