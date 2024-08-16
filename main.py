from binance import Client
from EMA_Cross import EMA_Cross, loggs
import ta
import time
from pydantic import BaseModel
import api_connect


class SignalPayload(BaseModel):
    symbol: str
    signal: str
    entry_price: float
    indicator: str


def main():
    symbol = 'BNBUSDT'
    interval = Client.KLINE_INTERVAL_15MINUTE
    short_window = 9
    long_window = 21
    adx_period = 14
    miya_api = api_connect.API()
    while True:
        data = EMA_Cross.get_historical_klines(symbol, interval, "2 days ago UTC")
        short_ema = EMA_Cross.calculate_ema(data['close'], short_window)
        long_ema = EMA_Cross.calculate_ema(data['close'], long_window)
        adx = data['ADX'] = ta.trend.adx(data['high'], data['low'], data['close'], window=adx_period)
        print(adx.iloc[-1])
        crossover_buy, crossover_sell, last_close = EMA_Cross.check_ema_crossover(data, short_window, long_window)

        if crossover_buy and last_close > long_ema.iloc[-1] and adx.iloc[-1] > 22:
            loggs.system_log.warning(f'Getting signal for {symbol} Buy')
            signal_payload = SignalPayload(
                symbol=symbol[0],  # Adjust the symbol format if needed
                signal='Buy',
                entry_price=last_close,
                indicator='EMA'
            )
            response = miya_api.send_signal(signal_payload)

            loggs.system_log.warning("Bullish crossover detected. Placing a buy order.")
        elif crossover_sell and last_close < long_ema.iloc[-1] and adx.iloc[-1] > 22:
            signal_payload = SignalPayload(
                symbol=symbol[0],  # Adjust the symbol format if needed
                signal='Sell',
                entry_price=last_close,
                indicator='EMA'
            )
            response = miya_api.send_signal(signal_payload)

            loggs.system_log.warning("Bearish crossover detected. Placing a sell order.")

        else:
            loggs.system_log.warning("No crossover detected.")

        time.sleep(900)


if __name__ == '__main__':
    main()