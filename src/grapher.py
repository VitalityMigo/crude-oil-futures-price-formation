import os

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from config import ASSETS

# Path
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR  = os.path.join(_SRC_DIR, "..", "plot")


# Monte carlo
def plot_mc_paths(
    asset: str,
    paths: list,
    plot_dir: str = PLOT_DIR,
) -> str:
    """
    Graph MC Simulation
    """
    asset_label = ASSETS.get(asset.lower(), asset.upper())

    # Plot start
    fig, ax = plt.subplots(figsize=(14, 6))

    # Simulated paths
    for idx, path_df in enumerate(paths):
        ax.plot(
            path_df.index,
            path_df["simulated_price"],
            color="#9089f6",
            linewidth=0.7,
            alpha=0.1,
            label="Paths" if idx == 0 else "_nolegend_",
        )

    # Real price
    real = paths[0]["real_price"]
    ax.plot(real.index, real, color="#0d00c7", linewidth=1.5, label="Observed Price")

    ax.set_title(
        f"Observed Price vs Market Maker Quoted price ({asset_label})",
        fontsize=13,
    )
    ax.set_xlabel("Time")
    ax.set_ylabel("Price (USD / bbl)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()
    ax.legend(loc="upper left", framealpha=0.8)

    plt.tight_layout()
    filepath = os.path.join(plot_dir, f"price_{asset.lower()}.png")
    fig.savefig(filepath, dpi=150)
    plt.close(fig)
    return os.path.abspath(filepath)

# Single Path
def plot_quotes(asset, bbo_df, scatter_df, plot_dir=PLOT_DIR):
    """
    Generates two subplot on volatility vs. inventory
    """
    # Asset
    asset_label = ASSETS.get(asset.lower(), asset.upper())

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # BBO over time
    ax1.plot(bbo_df.index, bbo_df["best_bid"], color="#2ca02c", linewidth=1.0,
             linestyle="--", label="Best Bid")
    ax1.plot(bbo_df.index, bbo_df["best_ask"], color="#d62728", linewidth=1.0,
             linestyle="--", label="Best Ask")
    ax1.fill_between(bbo_df.index, bbo_df["best_bid"], bbo_df["best_ask"],
                     alpha=0.15, color="#1f77b4", label="BBO Spread")
    ax1.set_title(f"Top of Book ({asset_label})", fontsize=12)
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Price (USD / bbl)")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()
    ax1.legend(fontsize=9, framealpha=0.8)

    # Right: vol and inventory vs. spread
    sc = ax2.scatter(
        scatter_df["inventory"],
        scatter_df["vol"],
        c=scatter_df["spread_bps"],
        cmap="plasma",
        s=8,
        alpha=0.6,
    )
    cbar = fig.colorbar(sc, ax=ax2)
    cbar.set_label("Observed BBO Spread (bps)", fontsize=9)
    ax2.set_title("Volatility and Inventory vs. Spread", fontsize=12)
    ax2.set_xlabel("Inventory")
    ax2.set_ylabel("Annualized Volatility")

    plt.tight_layout()
    filepath = os.path.join(plot_dir, f"quote_{asset.lower()}.png")
    fig.savefig(filepath, dpi=150)
    plt.close(fig)
    return os.path.abspath(filepath)
