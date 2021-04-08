
import pandas as pd
import numpy as np
import requests
import time
import os

from config import *

api_keys = API_KEYS
symbols = STOCK_UNIVERSE


def make_dataframe(res):
    df = pd.DataFrame(res["values"])
    df.columns = ["date", "open", "high", "low", "close", "volume"]
    df["date"] = pd.to_datetime(df["date"])
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(int)
    df = df.sort_values("date", ascending=True).reset_index(drop=True)
    return df


def get_ohlc(symbol, i):
    api_key = api_keys[i%(len(api_keys))]
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&apikey={api_key}&outputsize={DAYS_BACK}"
    res = requests.get(url).json()
    df = make_dataframe(res)

    return df


def fetch_historical_data():
    for i, symbol in enumerate(symbols):
        try:
            data = get_ohlc(symbol, i)
        except Exception as e:
            print(f"{symbol} - {e}")
            continue

        print(data)
        if not os.path.exists(f"stocks/{symbol}/"):
            os.mkdir(f"stocks/{symbol}/")
        data.to_csv(f"stocks/{symbol}/raw.csv", index=False)


if __name__=="__main__":
    fetch_historical_data()