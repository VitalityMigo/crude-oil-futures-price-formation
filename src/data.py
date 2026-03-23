import os
import numpy as np
import pandas as pd
import yfinance as yf

from config import TICKERS

# Path resolver
_SRC_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(_SRC_DIR, "..", "data")


def fetch_prices(asset: str, start: str, end: str):
    """
    Retreive oil daily close price.
    """
    ticker = TICKERS[asset.lower()]
    raw = yf.download(ticker, start=start, end=end, auto_adjust=False, progress=False)

    if raw.empty:
        raise ValueError(
            f"No data available for {ticker} between {start} and {end}. "
        )

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.droplevel(1)

    df = raw[["Close"]].copy()
    df.columns = ["close"]
    df.index.name = "date"
    df.index = pd.to_datetime(df.index)
    return df.dropna()


def compute_historical_vol(df: pd.DataFrame, window: int = 30):
    """
    Rolling annualized volatility .
    """
    df = df.copy()
    log_ret = np.log(df["close"] / df["close"].shift(1)).dropna()
    df["vol"] = log_ret.rolling(window=window).std() * np.sqrt(252)
    return df.dropna()


def save_to_csv(df: pd.DataFrame, asset: str, data_dir: str = DATA_DIR, filename: str = None):
    """
    Save DataFrame to CSV.
    """
    os.makedirs(data_dir, exist_ok=True)
    name = filename if filename else f"{asset.lower()}_daily.csv"
    filepath = os.path.join(data_dir, name)
    df.to_csv(filepath)
    return os.path.abspath(filepath)


def load_from_csv(asset: str, data_dir: str = DATA_DIR):
    """
    Load DataFrame from CSV.
    """
    filepath = os.path.join(data_dir, f"{asset.lower()}_daily.csv")
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"No CSV found at '{filepath}'."
        )
    return pd.read_csv(filepath, index_col="date", parse_dates=True)
