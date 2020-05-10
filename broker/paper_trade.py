from .api_base import ApiBase
import datetime
import json


class Paper(ApiBase):
    def __init__(self, client=None, cash=0.0, portfolio=None):
        """
        client: either Robinhood or TD Ameritrade account. The account must be logged in; used for getting price quotes.
        cash: available cash, default is 0.0
        portfolio: structured as follows:
            [
                {
                    "symbol": string,
                    "price": float,
                    "quantity": int,
                    "purchase_date": string ("MM/DD/YYYY HH:MM:SS.sss Z")
                }
            ]
        """
        self._account = {
            "cash": cash,
            "portfolio": portfolio,
            "total": 0.0
        }
        # WARNING, DO NOT USE CLIENT TO ACTUALLY BUY/SELL
        self._client = client
        super().__init__()

    def _update_total(self):
        if self._account['portfolio'] is None:
            self._account['total'] = self._account['cash']
            return self._account['total']

        total = 0.0
        for symbol in self._account['portfolio']:
            for purchase in self._account['portfolio'][symbol]:
                total += self.get_quote(symbol).price * purchase['quantity']
        self._account['total'] = total + self._account['cash']
        return self._account['total']

    def get_quote(self, symbol):
        return self._client.get_quote(symbol)

    def buy(self, symbol, quantity, extended=False):
        quote = self.get_quote(symbol)
        if quote is None:
            print("Cannot retrieve quote for {}".format(symbol))
            return
        total = quote.price * quantity
        if total > self._account['cash']:
            # format string for $
            print("Not enough funds in account to buy {} shares of {} at ${}".format(quantity, symbol, quote.price))
            return

        if self._account['portfolio'] is None:
            self._account['portfolio'] = {}
        if symbol not in self._account['portfolio']:
            self._account['portfolio'][symbol] = []
        now = datetime.datetime.now()
        self._account['portfolio'][symbol].append({
            "price": quote.price,
            "quantity": quantity,
            "purchase_date": now.strftime("%d/%m/%Y %H:%M:%S.%f")[:-3] + now.strftime(" %Z")
        })
        self._account['cash'] -= total

    def sell(self, symbol, quantity, extended=False):
        if symbol not in self._account['portfolio']:
            print("short selling not implemented, no margin.")
            return
        quote = self.get_quote(symbol)
        if quote is None:
            print("Cannot retrieve quote for {}".format(symbol))
            return
        total = quote.price * quantity

        if self._account['portfolio'] is None:
            self._account['portfolio'] = {}
        if symbol not in self._account['portfolio']:
            self._account['portfolio'][symbol] = []
        now = datetime.datetime.now()
        # For total portfolio tracking it records all purchasing/selling transactions
        self._account['portfolio'][symbol].append({
            "price": quote.price,
            "quantity": -quantity,
            "purchase_date": now.strftime("%d/%m/%Y %H:%M:%S.%f")[:-3] + now.strftime(" %Z")
        })
        self._account['cash'] += total

    def login(self, username, password):
        self._client.login(username, password)

    def insecure_login(self):
        self._client.insecure_login()

    def logout(self):
        self._client.logout()

    def save(self):
        # self._update_total()
        with open('portfolio.json', 'w') as f:
            json.dump(self._account, f)

    def load(self, location='portfolio.json'):
        with open(location, 'r') as f:
            line = f.readline()
            self._account = json.loads(line)
