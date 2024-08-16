from binance.client import Client
import pandas as pd
import numpy as np
import time
import warnings
from . import loggs
import ta

warnings.filterwarnings(action='ignore')
api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)


def get_historical_klines(symbol, interval, lookback):
    klines = client.get_historical_klines(symbol, interval, lookback)
    data = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
        'taker_buy_quote_asset_volume', 'ignore'
    ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    data = data[['open', 'high', 'low', 'close', 'volume']]
    data = data.astype(float)
    return data


def calculate_ema(data, window):
    """Calculate Exponential Moving Average (EMA)."""
    return data.ewm(span=window, adjust=False).mean()


def check_ema_crossover(data, short_ema, long_ema):
    """Check for EMA crossover signals."""
    short_ema = calculate_ema(data['close'], short_ema)
    long_ema = calculate_ema(data['close'], long_ema)
    last_close_price = data['close'].iloc[-2]

    crossover_buy = (short_ema.iloc[-2] < long_ema.iloc[-2]) and (short_ema.iloc[-1] > long_ema.iloc[-1])
    crossover_sell = (short_ema.iloc[-2] > long_ema.iloc[-2]) and (short_ema.iloc[-1] < long_ema.iloc[-1])

    print(crossover_sell, crossover_buy, data['close'].iloc[-2])
    return crossover_buy, crossover_sell, last_close_price


def main():
    symbol = 'BNBUSDT'
    interval = Client.KLINE_INTERVAL_15MINUTE
    short_window = 9
    long_window = 21
    adx_period = 14

    while True:
        data = get_historical_klines(symbol, interval, "2 days ago UTC")
        short_ema = calculate_ema(data['close'], short_window)
        long_ema = calculate_ema(data['close'], long_window)
        adx = data['ADX'] = ta.trend.adx(data['high'], data['low'], data['close'], window=adx_period)
        print(adx.iloc[-1])
        crossover_buy, crossover_sell, last_close = check_ema_crossover(data, short_window, long_window)

        if crossover_buy and last_close > long_ema.iloc[-1] and adx.iloc[-1] > 22:
            loggs.system_log.warning("Bullish crossover detected. Placing a buy order.")
        elif crossover_sell and last_close < long_ema.iloc[-1] and adx.iloc[-1] > 22:
            loggs.system_log.warning("Bearish crossover detected. Placing a sell order.")
        else:
            loggs.system_log.warning("No crossover detected.")

        time.sleep(900)


if __name__ == "__main__":
    main()
