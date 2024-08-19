from coins_trade.miya import miya_trade
from colorama import init, Fore
from binance.client import Client
from coins_trade.miya import logging_settings
import api_connect
import time

client = Client()
api = api_connect.API()


def start_trade():
    signal_data = api.get_signal()
    print(signal_data)
    settings = api.get_settings()
    if signal_data[0] is not None:
        miya_trade.trade(
            symbol=signal_data[0][1],
            signal=signal_data[0][2],
            entry_price=signal_data[0][3],
            position_size=settings[0]['value'],
            indicator=settings[0]['indicator']
        )
        api.clean_db(table_name='signals')
        logging_settings.system_log.warning('Signals Table cleaned successfully')
        traded = True
        return traded
    else:
        print('No trading signal')


if __name__ == '__main__':
    print(Fore.YELLOW + 'Starting trade bot...')
    while True:
        is_traded = start_trade()
        time.sleep(5)
