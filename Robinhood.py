import requests
import json
import getpass

VERSION = 'v1.1'
DEBUG = False

class Uri:
    api = 'https://api.robinhood.com'
    
    def login():
        return Uri.api + '/oauth2/token/'
    
    def logout():
        return Uri.api + '/oauth2/revoke_token/'
    
    def order():
        return Uri.api + '/orders/'
    
    def accounts():
        return Uri.api + '/accounts/'
    
    def instruments(instrumentId=None, option=None):
        '''
        Return information about a specific instrument by providing its instrument id.
        Add extra options for additional information such as "popularity"
        '''
        return api_url + "/instruments/" + ("{id}/".format(id=instrumentId) if instrumentId else "") + ("{_option}/".format(_option=option) if option else "")


class Robinhood:
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
        print('constructed ' + VERSION)
    
    def prompt_login(self):
        self.login(input("Username: "), getpass.getpass())
    
    def login(self, username, password):
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
        resp = self.session.options(Uri.login(), headers=headers)
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
        
        resp = self.session.post(Uri.login(), data=json.dumps(data))
        if DEBUG:
            Robinhood.log_response(resp)
        if resp.status_code is not 200:
            # possibly throw exception instead
            print('login failed')
            return
        obj = json.loads(resp.text)
        self.refresh_token                      = obj['refresh_token']
        self.session.headers['Authorization']   = 'Bearer ' + obj['access_token']
        
        # make account request to get current info
        self.account = self.account_info()
        self.logged_in = True

    def account_info(self):
        resp = self.session.get(Uri.accounts())
        if DEBUG:
            Robinhood.log_response(resp)
        return json.loads(resp.text)
        
    def logout(self):
        data = {
            "client_id":self.client_id,
            "token":self.refresh_token
        }
        resp = self.session.post(Uri.logout(), data=json.dumps(data))
        if DEBUG:
            Robinhood.log_response(resp)
        self.logged_in = False
        
    # symbol, price, quantity are strings
    def limit_buy(self, symbol, price, quantity, extended=False, cancel="gfd"):
        if not logged_in:
            self.prompt_login()
            
        data = {
            "time_in_force":cancel,
            "price":price,
            "quantity":quantity,
            "side":"buy",
            "trigger":"immediate",
            "type":"limit",
            "account":self.account['url'],
            # Instrument needs to be dynamic
            "instrument":"",
            "symbol":symbol,
            # "ref_id":"",
            "extended_hours":extended
        }
    
    def log_response(resp):
        print("--------START--------")
        print(resp.status_code)
        print(resp.reason)
        print(resp.headers)
        print(resp.text)
        print("---------END---------")