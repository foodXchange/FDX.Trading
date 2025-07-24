import pandas as pd

# Load data
try:
    df = pd.read_csv('Suppliers 24_7_2025.csv', low_memory=False, dtype=str)
    print(df.head())  # Show first few rows as a check
except Exception as e:
    print(f"Failed to load data: {e}")

# TODO: Add further data processing or export logic here. 