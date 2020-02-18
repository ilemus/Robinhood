import requests
import json
import getpass
import pickle
import random

from src.ApiBase import ApiBase
from src.Url import Url


class Quote:
    def __init__(self, obj):
        self.price = float(obj['last_trade_price'])
        self.bid_price = float(obj['bid_price'])
        self.bid_size = obj['bid_size']
        self.ask_price = float(obj['ask_price'])
        self.ask_size = obj['ask_size']
        self.prev_close = float(obj['adjusted_previous_close'])
        
    def __str__(self):
        return "{ " + "price: " + str(self.price) + ", bid_price: " + str(self.bid_price) + ", bid_size: " \
            + str(self.bid_size) + ", ask_price: " + str(self.ask_price) + ", ask_size: " + str(self.ask_size) + ", prev_close: " + str(self.prev_close) + " }"


class Configuration:
    def __init__(self):
        self.username = None
        self.password = None
        self.device_id = None
    
    
def gen_token():
    str = ""
    for i in range(0, 8):
        str += "{:01x}".format(random.randint(0, 15))
    str += "-"
    for i in range(0, 4):
        str += "{:01x}".format(random.randint(0, 15))
    str += "-"
    for i in range(0, 4):
        str += "{:01x}".format(random.randint(0, 15))
    str += "-"
    for i in range(0, 4):
        str += "{:01x}".format(random.randint(0, 15))
    str += "-"
    for i in range(0, 12):
        str += "{:01x}".format(random.randint(0, 15))
    return str

    
class Client(ApiBase):
    DEBUG = False
    INSECURE = False
    VERSION = "1.0"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'X-Robinhood-API-Version': '1.275.0',
            'Connection': 'keep-alive',
            'DNT': '1',
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
        self.device_id = gen_token()
        # print('constructed ' + Client.VERSION)
    
    def get_device_token(self):
        # clientId: "abcd-1938adf-192398192afasd-1239a"
        resp = self.session.get(Url.login_page())
        if Client.DEBUG:
            print(resp.status_code)
    
    def sms_confirm(self, username, password):
        data = {
            "grant_type":"password",
            "scope":"internal",
            "client_id":self.client_id,
            "expires_in":86400,
            # Device token should be user-input
            "device_token":self.device_id,
            "username":username,
            "password":password,
            "challenge_type": "sms"
        }
        string = json.dumps(data)
        if Client.DEBUG:
            print(Url.login())
            print(self.session.headers)
            print(string)
            print(len(string))
        
        resp = self.session.post(Url.login(), data=string, headers={'Content-Type': 'application/json', 'Content-Length': str(len(string))})
        if Client.DEBUG:
            Client.log_response(resp)
        # when login fails, 400 error code is returned
        if resp.status_code is 200:
            return
        
        obj = json.loads(resp.text)
        c_id = obj['challenge']['id']
        sms = input("SMS Code: ")
        data_resp = {
            'response': sms
        }
        resp = self.session.post(Url.challenge(c_id), data=json.dumps(data_resp), headers={'Content-Type': 'application/json'})
        if Client.DEBUG:
            Client.log_response(resp)
        # successful challenge accepted
        if resp.status_code is not 200:
            # possibly throw an exception instead
            print('Wrong SMS code, login failed.')
        else:
            resp = self.session.post(Url.login(), data=json.dumps(data), headers={'Content-Type': 'application/json', 'X-ROBINHOOD-CHALLENGE-RESPONSE-ID': c_id})
            if Client.DEBUG:
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
    login: make login request, and then get account info (ignore if logged in already)
    username: "test@mail.com"
    password: "password"
    '''
    def login(self, username, password):
        if self.logged_in:
            return
        device_token = ""
        # self.get_device_token()
        self.sms_confirm(username, password)
        ###### INSECURE LOGIN, FILE SAVED LOCALLY. POTENTIALLY MALICIOUS APPLICATIONS CAN FIND THIS FILE ######
        # TODO ENCRYPT/DECRYPT CONFIGURATION FILE
        if Client.INSECURE:
            config = Configuration()
            config.username = username
            config.password = password
            with open('configuration.pkl', 'wb') as f:
                pickle.dump(config, f, pickle.HIGHEST_PROTOCOL)
        
    '''
    Insecure login
    '''
    def insecure_login(self):
        if not Client.INSECURE:
            return
        ###### INSECURE LOGIN, FILE SAVED LOCALLY. POTENTIALLY MALICIOUS APPLICATIONS CAN FIND THIS FILE ######
        config = None
        try:
            with open('configuration.pkl', 'rb') as f:
                config = pickle.load(f)
        except FileNotFoundError:
            self.prompt_login()
            return
        self.session.cookies['device_id'] = self.device_id
        data = {
            "grant_type":"password",
            "scope":"internal",
            "client_id":self.client_id,
            "expires_in":86400,
            # Device token should be user-input
            "device_token":self.device_id,
            "username":config.username,
            "password":config.password
        }

        resp = self.session.post(Url.login(), data=json.dumps(data), headers={'Content-Type': 'application/json'})
        if Client.DEBUG:
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
        if Client.DEBUG:
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
        resp = self.session.post(Url.logout(), data=json.dumps(data), headers={'Content-Type': 'application/json'})
        if Client.DEBUG:
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
    def limit_buy(self, symbol, price, quantity, extended=False, cancel=None):
        if not self.logged_in:
            self.prompt_login()
        # This also will update stock_ids
        symbol = symbol.upper()
        instrument = self.get_instrument(symbol)
        if cancel is None:
            cancel = "gfd"
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
        if Client.DEBUG:
            print(data)
        
        resp = self.session.post(Url.order(), data=json.dumps(data), headers={'Content-Type': 'application/json'})
        obj = json.loads(resp.text)
        self.pending_orders.append(obj)
        if Client.DEBUG:
            Client.log_response(resp)
        return obj
    
    def buy(self, symbol, quantity, extended=False, cancel=None):
        if not self.logged_in:
            self.prompt_login()
        # This also updates stock_ids
        symbol = symbol.upper()
        instrument = self.get_instrument(symbol)
        if cancel is None:
            cancel = "gfd"
        data = {
            "time_in_force":cancel,
            "quantity":quantity,
            "side":"buy",
            "trigger":"immediate",
            "type":"market",
            "account":self.account['url'],
            "instrument":instrument,
            "symbol":symbol,
            # "ref_id":"",
            "extended_hours":extended
        }
        if Client.DEBUG:
            print(data)
        
        resp = self.session.post(Url.order(), data=json.dumps(data), headers={'Content-Type': 'application/json'})
        obj = json.loads(resp.text)
        self.pending_orders.append(obj)
        if Client.DEBUG:
            Client.log_response(resp)
        return obj
    
    def limit_sell(self, symbol, price, quantity, extended=False, cancel=None):
        if not self.logged_in:
            self.prompt_login()
        # This also will update stock_ids
        symbol = symbol.upper()
        instrument = self.get_instrument(symbol)
        if cancel is None:
            cancel = "gfd"
        data = {
            "time_in_force":cancel,
            "price":price,
            "quantity":quantity,
            "side":"sell",
            "trigger":"immediate",
            "type":"limit",
            "account":self.account['url'],
            "instrument":instrument,
            "symbol":symbol,
            # "ref_id":"",
            "extended_hours":extended
        }
        if Client.DEBUG:
            print(data)
        
        resp = self.session.post(Url.order(), data=json.dumps(data), headers={'Content-Type': 'application/json'})
        obj = json.loads(resp.text)
        self.pending_orders.append(obj)
        if Client.DEBUG:
            Client.log_response(resp)
        return obj
    
    def sell(self, symbol, quantity, extended=False, cancel=None):
        if not self.logged_in:
            self.prompt_login()
        # This also updates stock_ids
        symbol = symbol.upper()
        instrument = self.get_instrument(symbol)
        if cancel is None:
            cancel = "gfd"
        
        data = {
            "time_in_force":cancel,
            "quantity":quantity,
            "side":"sell",
            "trigger":"immediate",
            "type":"market",
            "account":self.account['url'],
            "instrument":instrument,
            "symbol":symbol,
            # "ref_id":"",
            "extended_hours":extended
        }
        if Client.DEBUG:
            print(data)
        
        resp = self.session.post(Url.order(), data=json.dumps(data), headers={'Content-Type': 'application/json'})
        obj = json.loads(resp.text)
        self.pending_orders.append(obj)
        if Client.DEBUG:
            Client.log_response(resp)
        return obj
    
    def get_instrument(self, symbol):
        if symbol in self.instruments.keys():
            return self.instruments[symbol]
        else:
            resp = self.session.get(Url.instruments(symbol=symbol))
            if Client.DEBUG:
                Client.log_response(resp)
            obj = json.loads(resp.text)
            url = obj['results'][0]['url']
            self.instruments[symbol] = url
            self.stock_ids[symbol] = obj['results'][0]['id']
            self.symbols[obj['results'][0]['id']] = symbol
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
        if Client.DEBUG:
            Client.log_response(resp)
        return Quote(json.loads(resp.text))
    
    # https://api.robinhood.com/marketdata/historicals/SPY/?bounds=trading&interval=5minute&span=day
    # symbol = "SPY"
    # interval = 5minute, 10minute, day, week
    # span = day, month, year, 5year
    '''
    {
        "quote":"https://api.robinhood.com/quotes/8f92e76f-1e0e-4478-8580-16a6ffcfaef5/",
        "symbol":"SPY",
        "interval":"5minute",
        "span":"day",
        "bounds":"trading",
        "previous_close_price":"292.620000",
        "previous_close_time":"2019-08-02T20:00:00Z",
        "open_price":"288.200000",
        "open_time":"2019-08-05T13:00:00Z",
        "instrument":"https://api.robinhood.com/instruments/8f92e76f-1e0e-4478-8580-16a6ffcfaef5/",
        "historicals":
        [{
            "begins_at":"2019-08-05T13:00:00Z",
            "open_price":"288.200000",
            "close_price":"288.190000",
            "high_price":"288.240000",
            "low_price":"287.970000",
            "volume":74159,
            "session":"pre",
            "interpolated":false
        }]
    }
    '''
    def get_historical(self, symbol, interval, span):
        symbol = symbol.upper()
        resp = self.session.get(Url.historical(symbol, interval, span))
        if Client.DEBUG:
            Client.log_response(resp)
        return json.loads(resp.text)
    
    '''
    'bids' {
        [{'side': 'bid', 'price': {'amount': '198.000000', 'currency_code': 'USD'}, 'quantity': 500}]
    },
    'asks' {
        [{'side': 'ask', 'price': {'amount': '198.010000', 'currency_code': 'USD'}, 'quantity': 500}]
    }
    '''
    def get_book(self, symbol):
        if not self.logged_in:
            return None
        symbol = symbol.upper()
        self.get_instrument(symbol)
        resp = self.session.get(Url.book(self.stock_ids[symbol]))
        if Client.DEBUG:
            Client.log_response(resp)
        return json.loads(resp.text)
    
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
            if Client.DEBUG:
                Client.log_response(resp)
            obj = json.loads(resp.text)
            self.symbols[string] = obj['symbol']
            self.instruments[obj['symbol']] = instrument
            self.stock_ids[obj['symbol']] = string
            return obj['symbol']
    
    def cancel_order(self, order_pos):
        if order_pos >= len(self.pending_orders):
            return
        
        resp = self.session.post(self.pending_orders[order_pos]['cancel'])
        if Client.DEBUG:
            Client.log_response(resp)
        del self.pending_orders[order_pos]
    
    def log_response(resp):
        print("--------START--------")
        print(resp.status_code)
        print(resp.reason)
        print(resp.headers)
        print(resp.text)
        print("---------END---------")
