import getpass
import random
import requests


class Configuration:
    def __init__(self):
        self.username = None
        self.password = None
        self.device_id = None


class Quote:
    """
    Used as a base class for quote type.
    Implementations can reimplement the constructor to parse quote objects
    """
    def __init__(self):
        # Last traded price
        self.price = 0.0
        self.bid_price = 0.0
        self.bid_size = 0
        self.ask_price = 0.0
        self.ask_size = 0


class ApiBase:
    DEBUG = False
    INSECURE = False
    VERSION = "1.0"

    @staticmethod
    def gen_client():
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
    
    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
        self.device_id = ApiBase.gen_client()
    
    def prompt_login(self):
        self.login(input("Username: "), getpass.getpass())
    
    def login(self, username, password):
        pass

    def insecure_login(self):
        pass
    
    def account_info(self):
        pass
    
    def logout(self):
        pass
    
    # Market buy
    def buy(self, symbol, quantity, extended=False):
        pass
    
    def limit_buy(self, symbol, price, quantity, extended=False, cancel=None):
        pass
    
    # Market sell
    def sell(self, symbol, quantity, extended=False):
        pass
    
    def limit_sell(self, symbol, price, quantity, extended=False, cancel=None):
        pass
    
    def get_quote(self, symbol):
        pass
    
    # Portfolio of stocks
    def get_positions(self):
        pass
