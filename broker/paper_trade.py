from .api_base import ApiBase


class Client(ApiBase):
    def __init__(self, client=None, cash=0.0, portfolio=None):
        """
        client: either Robinhood or TD Ameritrade account. The account must be logged in; used for getting price quotes.
        cash: available cash, default is 0.0
        portfolio: structured as follows:
            {
                "symbol": string,
                "purchase_price": float,
                "purchase_date": string ("MM/DD/YY HH:MM:SS.sss Z")
            }
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
        self._account['total'] = self._account['cash']\
                                 + (0.0 if self._account['portfolio'] is None
                                    else sum(self.get_quote(v['symbol']).price for v in self._account['portfolio']))

    def get_quote(self, symbol):
        self.client.get_quote(symbol)
