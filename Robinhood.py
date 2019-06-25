import requests
import json

VERSION = 'v1.1'
DEBUG = True

class Robinhood:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'Host': 'api.robinhood.com',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'X-Robinhood-API-Version': '1.275.0',
            'Connection': 'keep-alive',
            # 'Content-Length': '236',
            'TE': 'Trailers'
        }
        self.session.headers = self.headers
        print('constructed ' + VERSION)
    
    def login(self, username, password):
        print('logging in...')
        # I think we need to do options first
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
        if DEBUG:
            print('OPTIONS /oauth2/token/')
        resp = self.session.options('https://api.robinhood.com/oauth2/token/', headers=headers)
        if DEBUG:
            print(resp.status_code)
            print(resp.reason)
            print(resp.headers)
            print(resp.text)
        
        data = {
            "grant_type":"password",
            "scope":"internal",
            "client_id":"c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS",
            "expires_in":86400,
            "device_token":"c2774eb3-e401-46d4-afa3-1e7421adfdc8",
            "username":username,
            "password":password
        }
        
        req = requests.Request('POST','https://api.robinhood.com/oauth2/token/', data=json.dumps(data), headers=self.headers)
        req = req.prepare()
        
        if DEBUG:
            print(req.method)
            print(req.url)
            print('\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()))
            print(req.body)
        
        resp = self.session.send(req)
        if DEBUG:
            print(resp.status_code)
            print(resp.reason)
            print(resp.headers)
            print(resp.text)
        
        json.loads(resp.text)
