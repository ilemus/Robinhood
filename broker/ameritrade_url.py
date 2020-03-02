class Url:
    @staticmethod
    def oauth():
        return "https://auth.tdameritrade.com/auth"

    @staticmethod
    def quote():
        return "https://api.tdameritrade.com/v1/marketdata/{}/quotes"
