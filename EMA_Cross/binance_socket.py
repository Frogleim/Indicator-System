import asyncio
import aiohttp
import logging
import pandas as pd
import ssl

symbols = ['BNBUSDT', 'BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'ADAUSDT']
interval = '15m'


async def fetch_klines(session, symbol, interval):
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}'
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        logging.error(f'Error fetching klines for {symbol}: {e}')
        return []


async def fetch_all_klines(symbols, interval):
    # Create an SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_klines(session, symbol, interval) for symbol in symbols]
        results = await asyncio.gather(*tasks)

        # Process and store data for each symbol
        dataframes = {}
        for symbol, df in zip(symbols, results):
            df = pd.DataFrame(df, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            dataframes[symbol] = df

        return dataframes


if __name__ == '__main__':
    result = asyncio.run(fetch_all_klines(symbols, interval))
    for symbol, df in result.items():
        print(f"Data for {symbol}:")
        print(df.head())
