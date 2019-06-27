from Client import Client

class Robinhood:
    def __init__(self, client):
        self.client = client
        
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
