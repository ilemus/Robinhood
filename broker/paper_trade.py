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
        self.client = client
        super().__init__()

    def _update_total(self):
        self._account['total'] = self._account['cash'] \
                                 + (0.0 if self._account['portfolio'] is None
                                    else sum(self.get_quote(v['symbol']).price * v['quantity']
                                             for v in self._account['portfolio']))

    def get_quote(self, symbol):
        return self.client.get_quote(symbol)

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
            self._account['portfolio'] = []
        now = datetime.datetime.now()
        self._account['portfolio'].append({
            "symbol": symbol,
            "price": quote.price,
            "quantity": quantity,
            "purchase_date": now.strftime("%d/%m/%Y %H:%M:%S.%f")[:-3] + now.strftime(" %Z")
        })
        self._account['cash'] -= total

    def save(self):
        with open('portfolio.json', 'w') as f:
            json.dump(self._account, f)

    def load(self):
        with open('portfolio.json', 'r') as f:
            self._account = json.loads(f)
