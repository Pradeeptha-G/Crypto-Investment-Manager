import requests
import pandas as pd
from datetime import datetime
import time


coins = [
    "bitcoin",
    "ethereum",
    "solana",
    "binancecoin"
]

DAYS = 200
all_data = []

for coin in coins:
    print(f"Collecting {coin} data...")

    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": DAYS
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "prices" not in data:
        print(f"Skipped {coin} due to API issue")
        continue

    df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    df["Date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date

    ohlc = df.groupby("Date")["price"].agg(
        Open="first",
        High="max",
        Low="min",
        Close="last"
    ).reset_index()

    for _, row in ohlc.iterrows():
        all_data.append([
            row["Date"],
            coin,
            row["Open"],
            row["High"],
            row["Low"],
            row["Close"]
        ])

    time.sleep(1)

final_df = pd.DataFrame(
    all_data,
    columns=["Date", "Coin", "Open", "High", "Low", "Close"]
)

final_df.to_csv("crypto_data_200_days.csv", index=False)

print("200 days OHLC data collected successfully")








