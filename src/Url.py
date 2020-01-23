class Url:
    api = 'https://api.robinhood.com'
    def accounts():
        return Url.api + '/accounts/'
    
    def book(s_id):
        return Url.api + '/marketdata/pricebook/snapshots/' + s_id + '/'
    
    def challenge(c_id):
        return Url.api + "/challenge/" + c_id + "/respond/"
    
    def historical(symbol, interval, span):
        return Url.api + "/marketdata/historicals/" + symbol + "/?bounds=regular&interval=" + interval + "&span=" + span
    
    def instruments(symbol):
        return Url.api + "/instruments/?symbol=" + symbol
    
    def login():
        return Url.api + '/oauth2/token/'
        
    def login_page():
        return "https://robinhood.com/login"
    
    def logout():
        return Url.api + '/oauth2/revoke_token/'
    
    def order():
        return Url.api + '/orders/'
    
    def positions():
        return Url.api + "/positions/?nonzero=true"
    
    def quote(s_id):
        return Url.api + "/marketdata/quotes/" + s_id + "/?include_inactive=true"