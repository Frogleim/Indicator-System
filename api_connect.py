import requests
from pydantic import BaseModel


class SignalPayload(BaseModel):
    symbol: str
    signal: str
    entry_price: float
    indicator: str


class API:
    def __init__(self):
        self.url = 'http://77.37.51.134:8080/'
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

    def send_signal(self, signal_data: SignalPayload):

        data = {
            "symbol": signal_data.symbol,
            "signal": signal_data.signal,
            "entry_price": signal_data.entry_price,
            "indicator": signal_data.indicator
        }

        response = requests.post(self.url + 'insert-signal', headers=self.headers, json=data, verify=False)
        print(response.json())
        if response.status_code == 200:
            return {'Message': 'Signal added successfully', 'Action': True}
        else:
            return {'Error': 'Failed to add signal', 'Action': False}

    def check_trade_status(self):
        url = self.url + 'is_finished'
        print(url)
        r = requests.get(self.url + 'is_finished', verify=False)
        return r.json()

    def clean_db(self, table_name):
        data = {
            "table_name": table_name
        }
        r = requests.get(self.url, self.headers, json=data, verify=False)
        if r.status_code == 200:
            return True
        else:
            return False


if __name__ == '__main__':
    api = API()
    status = api.check_trade_status()
    print(status)
