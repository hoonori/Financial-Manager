import requests
import pandas as pd
import os
import json
from datetime import datetime
import yfinance as yf

DEBUG = False

def log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def calculate_rsi(data, window=14):
    """Calculate the Relative Strength Index (RSI) for the given data."""
    delta = data.diff()
    gain = round((delta.where(delta > 0, 0)).rolling(window=window).mean(), 1)
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    # Replace zeros in 'loss' Series to avoid division by zero
    loss.replace(to_replace=0, value=0.001, inplace=True)

    rs = gain / loss
    rs = round(rs, 1)  # Round the rs values
    
    rsi = round(100 - (100 / (1 + rs)), 1)
    return rsi

def save_data(df, symbol):
    today = datetime.now().strftime("%Y-%m-%d")
    data_folder = f'raw_datas/{today}/{symbol}'
    os.makedirs(data_folder, exist_ok=True)
    json_filename = f'{data_folder}/data.json'
    # 날짜-시간에서 날짜 부분만 추출하여 문자열로 저장
    df['Date'] = pd.to_datetime(df['Date']).dt.date.astype(str)
    df.to_json(json_filename, orient='records', date_format='iso', indent=2)
    print(f'JSON Data saved for {symbol} to {json_filename}')

def process_stock_data(data, symbol):
    df = pd.DataFrame(data)
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    df = df.astype(float).round(1)  # Convert to float and round all data to one decimal
    # Assume calculate_rsi is a function defined elsewhere that computes the RSI
    log(data.columns)
    df['RSI'] = calculate_rsi(df['Close'])
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Date'}, inplace=True)
    save_data(df, symbol)

def fetch_and_save_stock_data_yfinance(symbol):
    stock = yf.Ticker(symbol)
    # '1y' for one year of data, you can customize the period as needed
    data = stock.history(period="1y")
    if data.empty:
        print("Error: No data found for", symbol)
    else:
        log(data)
        data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
        log(data)
        process_stock_data(data, symbol)


def fetch_and_save_stock_data(symbol):
    fetch_and_save_stock_data_yfinance(symbol)

def load_symbols():
    with open('symbols.txt', 'r') as file:
        symbols = [line.strip() for line in file if line.strip()]
    return symbols
