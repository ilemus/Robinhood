from argparse import ArgumentParser

from broker.ameritrade_api import Ameritrade
from broker.api_base import ApiBase
from broker.robinhood_api import Robinhood


def create_argument_parser():
    parser = ArgumentParser()
    parser.add_argument('-s', '--stocks', nargs='+', required=True, help='A list of stocks to collect')
    parser.add_argument('-b', '--broker', nargs='?', choices=['robinhood', 'ameritrade'], help='A broker to use')
    parser.add_argument('-u', '--username', required=True, help='Broker login info, the username is not stored locally.')
    parser.add_argument('-p', '--password', required=True, help='Broker login info, the password is not stored locally.')
    parser.add_argument('-o', '--output', nargs='?', help='Output older to write to')
    parser.add_argument('-c', '--compress', action="store_true", help='Use compression')
    parser.add_argument('-v', '--verbose', action="store_true", help='Log verbose information')
    parser.add_argument('-i', '--insecure', action="store_true", help='Warning USERNAME AND PASSWORD WILL BE SAVED!!!')
    return parser


def format_robinhood(prices):
    return prices


def format_ameritrade(prices):
    return prices


def format_prices(broker, prices):
    switch = {
        'robinhood': format_robinhood,
        'ameritrade': format_ameritrade
    }
    return switch[broker](prices)


def run():
    parser = create_argument_parser()
    args = parser.parse_args()
    stocks = args.stocks
    broker = args.broker
    if broker == 'robinhood':
        client = Robinhood()
    elif broker == 'ameritrade':
        client = Ameritrade()
    else:
        client = None
    if args.insecure:
        ApiBase.INSECURE = True
        if not client.insecure_login():
            client.login(args.username, args.password)
    else:
        client.login(args.username, args.password)
    write = args.output is not None
    if write:
        write_to = args.output
        out = open(write_to, 'a')
    verbose = args.verbose

    for stock in stocks:
        five_mins = client.get_historical(stock, client.Interval.FIVE_MINUTES, client.Span.ONE_DAY)
        five_mins = format_prices(broker, five_mins)
        if write:
            out.write(five_mins)
        elif verbose:
            print(five_mins)

    if write:
        out.close()


if __name__ == '__main__':
    run()
