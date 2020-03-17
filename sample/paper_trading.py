from broker.paper_trade import Paper
from broker.robinhood_api import Robinhood


def main():
    c = Robinhood()
    # c.prompt_login()
    paper_trader = Paper(client=c, cash=100000.0)
    return paper_trader


client = None
if __name__ == "__main__":
    Robinhood.INSECURE = True
    client = main()
