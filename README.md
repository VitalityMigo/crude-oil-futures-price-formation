# Crude Oil Price Formation under Multiple Market Makers

A simulation of how market-maker inventory dynamics have a permanent impact on the mid price of an asset, built around traditional systematic quoting model applied to Brent and WTI Crude Oil Futures.

---

## Overview

The core topic of this project is to understand how the aggregate inventory of competing market makers influence the observed price of an asset.

Each market maker holds a net position (inventory) and adjusts their bid/ask quotes accordingly — widening the spread when uncertain and skewing quotes to revert toward a flat book. When several independent market makers quote simultaneously, their collective behaviour determines the Best Bid and Offer (BBO), and by extension the effective mid price. 

This project simulates that process over real historical price data for Brent Crude and WTI Crude Oil.

<br>

<img width="2250" height="900" alt="image" src="https://github.com/user-attachments/assets/602936ad-73b8-4e9b-b101-b079936016f4" />

---

## Installation and Usage

To start using the project, clone the repository in your local environment. Then, install the dependecies using:

```bash
pip install -r requirements.txt
```

To interact with the notebook, open your terminal at the root and run the following commands:

```bash
cd src 
python core.py
```

The CLI will prompt you to select an asset (Brent or WTI) and a time horizon (6 months, 1 year, 3 years). It then runs the full pipeline automatically.

---

## What it does

1. **Downloads** daily OHLCV data from Yahoo Finance (`BZ=F` for Brent, `CL=F` for WTI) and computes a 30-day rolling historical volatility.

2. **Simulates Monte Carlo paths** — at each time step, a group of market-makers draws random inventories, computes quotes via the specified model, and the BBO mid drives the next simulated price. The real day-over-day return is used as a drift to keep paths anchored.

3. **Runs an explicit single path** for orderbook inspection, recording best bid, best ask, spread, and per-MM inventory at each step.

4. **Exports four files:**
   - `data/{asset}_daily.csv` — historical price and volatility
   - `data/quotes_{asset}.csv` — tick-level bid/ask log
   - `plot/price_{asset}.png` — Monte Carlo paths simulation
   - `plot/quote_{asset}.png` — bid/ask time series and inventory/vol scatter plot

An explanation of the quoting model used in the simulation is done in [notebook.ipynb](https://github.com/VitalityMigo/crude-oil-futures-price-formation/blob/main/notebook.ipynb).

---

## Project structure

```
src/
  config.py        # tickers, asset names, CLI menus
  data.py          # price and volatility series download
  quotes.py        # quoting model definition
  monte_carlo.py   # path simulation and BBO tracking
  grapher.py       # matplotlib chart generator
  core.py          # CLI entry point

data/              # downloaded and generated CSV files
plot/              # generated PNG charts
notebook.ipynb     # model specification
requirements.txt
```
