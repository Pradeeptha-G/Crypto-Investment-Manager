import pandas as pd

# Load the dataset
df = pd.read_csv("crypto_data_200_days.csv")

print("EDA STARTED")

# 1. Dataset size
print("\nDataset Shape (rows, columns):")
print(df.shape)

# 2. Column names
print("\nColumns in dataset:")
print(df.columns)

# 3. Check missing values
print("\nMissing values in each column:")
print(df.isnull().sum())

# 4. Basic statistics
print("\nStatistical Summary:")
print(df.describe())

# 5. Coins present
print("\nCryptocurrencies in dataset:")
print(df["Coin"].unique())

print("\nEDA COMPLETED")
