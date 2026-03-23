import os
import sys
from datetime import date

# Path resolver
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ASSETS, ASSET_MENU, HORIZON_MENU
from data import fetch_prices, compute_historical_vol, save_to_csv
from monte_carlo import simulate_paths, simulate_explicit_path
from grapher import plot_mc_paths, plot_quotes


def _prompt(question, options):
    print(f"\n{question}")
    for key, label in options.items():
        print(f"  [{key}]  {label}")
    while True:
        choice = input("\n  Your choice: ").strip()
        if choice in options:
            return choice
        print(f"  ✗  Invalid input – select: {', '.join(options.keys())}.")


def _compute_start_date(horizon_key):
    today = date.today()
    _, years, months = HORIZON_MENU[horizon_key]
    year  = today.year  - years
    month = today.month - months
    if month <= 0:
        month += 12
        year  -= 1
    return today.replace(year=year, month=month)


def _banner():
    print()
    print("╔" + "═" * 61 + "╗")
    print("║   Crude Oil Price Formation with Multiple Market-Makers     ║")
    print("╚" + "═" * 61 + "╝")


def _step(msg):
    print(f"\n  ⟳  {msg}…")


def _ok(msg):
    print(f"  ✓  {msg}")


def run():
    _banner()

    # 1. Asset selection
    asset_key = _prompt("Select asset:", {k: ASSETS[v] for k, v in ASSET_MENU.items()})
    asset = ASSET_MENU[asset_key]

    # 2. Horizon selection
    horizon_key = _prompt("Select time horizon:", {k: v[0] for k, v in HORIZON_MENU.items()})
    end_date   = date.today()
    start_date = _compute_start_date(horizon_key)

    # 3. Data retrieval
    _step(f"Fetching data ({ASSETS[asset]})")
    df = fetch_prices(asset, start=str(start_date), end=str(end_date))
    df = compute_historical_vol(df, window=30)
    save_to_csv(df, asset)
    _ok(f"{len(df)} trading days  →  data/{asset}_daily.csv")

    # 4. Monte Carlo simulation
    _step("Monte Carlo simulation  (200 paths · 4 market-makers)")
    paths = simulate_paths(df, num_mm=4, n=200)
    _ok(f"{len(paths)} paths generated")

    # 4b. Quote analysis – BBO & scatter
    bbo_df, scatter_df = simulate_explicit_path(df, num_mm=4)
    save_to_csv(bbo_df, asset, filename=f"quotes_{asset}.csv")
    _ok(f"BBO log saved  →  data/quotes_{asset}.csv")

    # 5. Chart export
    _step("Generating output")
    plot_mc_paths(asset, paths)
    plot_quotes(asset, bbo_df, scatter_df)
    _ok(f"Charts saved  →  plot/price_{asset}.png  |  plot/quote_{asset}.png")

    print("\n  Done.\n")


if __name__ == "__main__":
    run()
