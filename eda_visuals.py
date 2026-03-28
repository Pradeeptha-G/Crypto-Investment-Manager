import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("crypto_data_200_days.csv")

# Convert Date column to datetime
df["Date"] = pd.to_datetime(df["Date"])

# Filter only Bitcoin
btc = df[df["Coin"] == "bitcoin"]

# 1️⃣ Price trend over time (Close price)
plt.figure()
plt.plot(btc["Date"], btc["Close"])
plt.title("Bitcoin Close Price Trend (200 Days)")
plt.xlabel("Date")
plt.ylabel("Close Price")
plt.show()

# 2️⃣ Distribution of Close price
plt.figure()
plt.hist(btc["Close"], bins=30)
plt.title("Distribution of Bitcoin Close Price")
plt.xlabel("Close Price")
plt.ylabel("Frequency")
plt.show()

# 3️⃣ High vs Low price comparison
plt.figure()
plt.plot(btc["Date"], btc["High"], label="High")
plt.plot(btc["Date"], btc["Low"], label="Low")
plt.title("Bitcoin High vs Low Price")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.show()
