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
    
    def limit_buy(self, symbol, price, quantity, extened=False, cancel=None):
        self.client.limit_buy(symbol, price, quantity, extened, cancel)
        
    def cancel_order(self):
        length = len(self.client.pending_orders)
        if length is 1:
            self.client.cancel_order(0)
        elif length is 0:
            print('No orders to cancel')
            return
        else:
            for i in range(0, len(self.client.pending_orders)):
                # SYMBOL\tquantity\tprice
                print(str(i) + ": " + self.client.get_symbol_from_instrument(self.client.pending_orders[i]["instrument"]) \
                      + "\t" + str(int(float(self.client.pending_orders[i]["quantity"]))) \
                      + "\t" + str(float(self.client.pending_orders[i]["price"])))
            num = input("Enter order number to cancel: ")
            if num >= 0 and num < length:
                self.client.cancel_order(num)
            else:
                print("Forbidden order number: " + str(num))
            
    
    def logout(self):
        self.client.logout()
