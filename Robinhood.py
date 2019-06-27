import requests
import json
import getpass

VERSION = 'v1.1'
DEBUG = True

class Url:
    api = 'https://api.robinhood.com'
    def accounts():
        return Url.api + '/accounts/'
    
    def instruments(symbol):
        return Url.api + "/instruments/?symbol=" + symbol
    
    def login():
        return Url.api + '/oauth2/token/'
    
    def logout():
        return Url.api + '/oauth2/revoke_token/'
    
    def order():
        return Url.api + '/orders/'
    
    def positions():
        return Url.api + "/positions/?nonzero=true"
    
    def quote(s_id):
        return Url.api + "/marketdata/quotes/" + s_id + "/?include_inactive=true"


class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'Host': 'api.robinhood.com',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'X-Robinhood-API-Version': '1.275.0',
            'Connection': 'keep-alive',
            'TE': 'Trailers'
        }
        self.client_id = "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS"
        self.refresh_token = None
        self.account = None
        self.logged_in = False
        self.instruments = {}
        self.stock_ids = {}
        self.symbols = {}
        self.pending_orders = []
        print('constructed ' + VERSION)
    
    def prompt_login(self):
        self.login(input("Username: "), getpass.getpass())
    
    '''
    login: make login request, and then get account info (ignore if logged in already)
    username: "test@mail.com"
    password: "password"
    '''
    def login(self, username, password):
        if self.logged_in:
            return
        print('logging in...')
        # I think we need to do OPTIONS request first ??
        '''
        headers = {
            'Host': 'api.robinhood.com',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type,x-robinhood-api-version',
            'Connection': 'keep-alive',
            'TE': 'Trailers'
        }
        resp = self.session.options(Url.login(), headers=headers)
        '''
        
        data = {
            "grant_type":"password",
            "scope":"internal",
            "client_id":self.client_id,
            "expires_in":86400,
            # Device token should be user-input
            "device_token":"c2774eb3-e401-46d4-afa3-1e7421adfdc8",
            "username":username,
            "password":password
        }
        
        resp = self.session.post(Url.login(), data=json.dumps(data))
        if DEBUG:
            Client.log_response(resp)
        if resp.status_code is not 200:
            # possibly throw exception instead
            print('login failed')
            return
        obj = json.loads(resp.text)
        self.refresh_token                      = obj['refresh_token']
        self.session.headers['Authorization']   = 'Bearer ' + obj['access_token']
        self.logged_in = True
        # make account request to get current info
        self.account = self.account_info()['results'][0]

    '''
    account_info: requires to be logged in
    return: json object of /accounts/ request
    '''
    def account_info(self):
        if not self.logged_in:
            return None
        resp = self.session.get(Url.accounts())
        if DEBUG:
            Client.log_response(resp)
        return json.loads(resp.text)

    '''
    logout: requires to be logged in, requests token to be removed
    TODO: which token is used???
    '''
    def logout(self):
        if not self.logged_in:
            return
        data = {
            "client_id":self.client_id,
            "token":self.refresh_token
        }
        resp = self.session.post(Url.logout(), data=json.dumps(data))
        if DEBUG:
            Client.log_response(resp)
        self.logged_in = False

    '''
    limit_buy: buy a stock at a limit price (usually lower than current price)
    symbol: "ABC"
    price: "10.01"
    quantity: "10"
    extended: True
    cancel: "gtc"
    '''
    def limit_buy(self, symbol, price, quantity, extended=False, cancel="gfd"):
        if not self.logged_in:
            self.prompt_login()
        # This also will update stock_ids
        symbol = symbol.upper()
        instrument = self.get_instrument(symbol)
        
        data = {
            "time_in_force":cancel,
            "price":price,
            "quantity":quantity,
            "side":"buy",
            "trigger":"immediate",
            "type":"limit",
            "account":self.account['url'],
            "instrument":instrument,
            "symbol":symbol,
            # "ref_id":"",
            "extended_hours":extended
        }
        if DEBUG:
            print(data)
        
        resp = self.session.post(Url.order(), data=json.dumps(data))
        self.pending_orders.add(json.loads(resp.text))
        if DEBUG:
            Client.log_response(resp)
    
    def get_instrument(self, symbol):
        if symbol in self.instruments.keys():
            return self.instruments[symbol]
        else:
            resp = self.session.get(Url.instruments(symbol=symbol))
            if DEBUG:
                Client.log_response(resp)
            obj = json.loads(resp.text)
            url = obj['results'][0]['url']
            self.instruments[symbol] = url
            self.stock_ids[symbol] = obj['results'][0]['id']
            self.symbols['id'] = symbol
            return url
    
    '''
    get_quote: returns quote
    symbol: Tradable stock symbol name
    {
      "ask_price": "48.190000",
      "ask_size": 2300,
      "bid_price": "48.180000",
      "bid_size": 2900,
      "last_trade_price": "48.309300",
      "last_extended_hours_trade_price": null,
      "previous_close": "46.850000",
      "adjusted_previous_close": "46.850000",
      "previous_close_date": "2019-06-25",
      "symbol": "INTC",
      "trading_halted": false,
      "has_traded": true,
      "last_trade_price_source": "nls",
      "updated_at": "2019-06-26T17:52:07Z",
      "instrument": "https:\/\/api.robinhood.com\/instruments\/ad059c69-0c1c-4c6b-8322-f53f1bbd69d4\/"
    }
    '''
    def get_quote(self, symbol):
        symbol = symbol.upper()
        self.get_instrument(symbol)
        # stock_ids is updated
        s_id = self.stock_ids[symbol]
        resp = self.session.get(Url.quote(s_id))
        if DEBUG:
            Client.log_response(resp)
        return resp
    
    '''
    {
      "shares_held_for_stock_grants": "0.0000",
      "account": "https:\/\/api.robinhood.com\/accounts\/5RX37639\/",
      "pending_average_buy_price": "160.7200",
      "shares_held_for_options_events": "0.0000",
      "intraday_average_buy_price": "0.0000",
      "url": "https:\/\/api.robinhood.com\/positions\/5RX37639\/9c53326c-d07e-4b82-82d2-b108ec5d9530\/",
      "shares_held_for_options_collateral": "0.0000",
      "created_at": "2018-04-03T17:15:10.913191Z",
      "updated_at": "2018-04-03T17:18:47.026106Z",
      "shares_held_for_buys": "0.0000",
      "average_buy_price": "160.7200",
      "instrument": "https:\/\/api.robinhood.com\/instruments\/9c53326c-d07e-4b82-82d2-b108ec5d9530\/",
      "intraday_quantity": "0.0000",
      "shares_held_for_sells": "0.0000",
      "shares_pending_from_options_events": "0.0000",
      "quantity": "1.0000"
    }
    '''
    def get_positions(self):
        if not self.logged_in:
            return None
        resp = self.session.get(Url.positions())
        return json.loads(resp.text)['results']
    
    def get_symbol_from_instrument(self, instrument):
        # 9c53326c-d07e-4b82-82d2-b108ec5d9530
        length = len(instrument)
        START_INDEX = 37
        END_INDEX = 1
        string = instrument[length - START_INDEX:length - END_INDEX]
        if string in self.symbols.keys():
            return self.symbols[string]
        else:
            resp = self.session.get(instrument)
            if DEBUG:
                Client.log_response(resp)
            obj = json.loads(resp.text)
            self.symbols[string] = obj['symbol']
            self.instruments[obj['symbol']] = instrument
            self.stock_ids[obj['symbol']] = string
            return obj['symbol']
    
    def log_response(resp):
        print("--------START--------")
        print(resp.status_code)
        print(resp.reason)
        print(resp.headers)
        print(resp.text)
        print("---------END---------")

class Robinhood:
    def __init__(self):
        self.client = Client()
        global DEBUG
        DEBUG = False
        
    def login(self):
        self.client.prompt_login()
    
    '''
    Format portfolio by printing:
    [index]\t[shares]\t[average price]
    '''
    def portfolio(self):
        pos = self.client.get_positions()
        if pos is None:
            return
        for p in pos:
            symbol = self.client.get_symbol_from_instrument(p['instrument'])
            quantity = int(float(p['quantity']))
            price = float(p['average_buy_price'])
            print(f"{symbol}\t{quantity}\t{price}")
    
    def logout(self):
        self.client.logout()
