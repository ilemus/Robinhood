import getpass

class ApiBase:
    def prompt_login(self):
        self.login(input("Username: "), getpass.getpass())
    
    def login(self, username, password):
        pass
    
    def account_info(self):
        pass
    
    def logout(self):
        pass
    
    # Market buy
    def buy(self, symbol, quantity, extened=False):
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