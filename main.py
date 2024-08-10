from EMA_Cross import EMA_Cross, loggs
import asyncio
import api_connect
from pydantic import BaseModel


class SignalPayload(BaseModel):
    symbol: str
    signal: str
    entry_price: float
    indicator: str


pause_event = asyncio.Event()


class IndicatorChecker:
    def __init__(self):
        self.symbols = ['MATIC/USDT', 'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT']
        self.api = api_connect.API()

    async def main(self):
        pause_event.set()

        while True:
            await pause_event.wait()
            try:
                tasks = [EMA_Cross.check_signal(symbol) for symbol in self.symbols]
                results = await asyncio.gather(*tasks)
                for result in results:
                    symbol = result[0]
                    signal = result[1]
                    entry_price = result[2]  # Assuming this is the third element in the result tuple
                    indicator = "EMA"  # This can be dynamic or static based on your requirement

                    if signal != 'Hold':
                        loggs.system_log.warning(f'Getting signal for {symbol} {signal}')
                        signal_payload = SignalPayload(
                            symbol=symbol.replace('/', ''),  # Adjust the symbol format if needed
                            signal=signal,
                            entry_price=entry_price,
                            indicator=indicator
                        )
                        self.api.send_signal(signal_payload)
                        pause_event.clear()
                        await asyncio.sleep(1800)

            except Exception as e:
                EMA_Cross.loggs.error_logs_logger.error(f'EMA Crossover script down!\nError message: {e}')

    async def monitor_signals(self):
        while True:
            await asyncio.sleep(1)  # Check every second
            is_finished = self.api.check_trade_status()
            if is_finished['Message']:
                self.api.clean_db(table_name='signals')
                self.api.clean_db(table_name='trades_alert')
                pause_event.set()  # Resume signal monitoring


if __name__ == '__main__':
    indicators = IndicatorChecker()
    asyncio.run(indicators.main())
