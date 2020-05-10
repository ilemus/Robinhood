import json
import sqlite3
import os
import struct
from argparse import ArgumentParser

import errno
from datetime import datetime
from datetime import timezone

from broker.ameritrade_api import Ameritrade
from broker.api_base import ApiBase
from broker.robinhood_api import Robinhood


def create_argument_parser():
    parser = ArgumentParser()
    # This is replaced by a database
    # parser.add_argument('-s', '--stocks', nargs='+', required=True, help='A list of stocks to collect')
    parser.add_argument('-b', '--broker', nargs='?', choices=['robinhood', 'ameritrade'], help='A broker to use')
    parser.add_argument('-u', '--username', required=True, help='Broker login info, the username is not stored locally.')
    parser.add_argument('-p', '--password', required=True, help='Broker login info, the password is not stored locally.')
    parser.add_argument('-o', '--output', nargs='?', help='Output older to write to')
    parser.add_argument('-c', '--compress', action="store_true", help='Use compression')
    parser.add_argument('-v', '--verbose', action="store_true", help='Log verbose information')
    parser.add_argument('-i', '--insecure', action="store_true", help='Warning USERNAME AND PASSWORD WILL BE SAVED!!!')
    return parser


def create_stock_list():
    conn = sqlite3.connect('us_equities.db')
    cursor = conn.cursor()
    result = {
        'nasdaq': [_ for _ in cursor.execute("SELECT symbol FROM nasdaq WHERE 1=1").fetchall()],
        'nyse': [_ for _ in cursor.execute("SELECT symbol FROM nyse WHERE 1=1").fetchall()]
    }
    return result


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
    # Use a database to load the stock lists since there are so many
    stocks = create_stock_list()
    broker = args.broker
    out = None
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
        try:
            os.makedirs(write_to)
            os.makedirs(f'{write_to}\\nasdaq')
            os.makedirs(f'{write_to}\\nyse')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        update_str_format = "%d/%m/%y %H:%M:%S"
        if os.path.isfile(f'{write_to}\\config.json'):
            config_file = open(f'{write_to}\\config.json', 'r+')
            config = json.load(config_file)
            last_updated = datetime.strptime(config['last_updated'], update_str_format)
        else:
            config_file = open(f'{write_to}\\config.json', 'w')
            config = {}

    verbose = args.verbose
    failed = []
    number_of_stocks = float(len(stocks['nasdaq']) + len(stocks['nyse']))
    current_count = 0

    for stock in stocks['nasdaq']:
        if verbose:
            current_count = current_count + 1
        try:
            five_mins = client.get_historical(stock[0], client.Interval.FIVE_MINUTES, client.Span.ONE_DAY)
            # Why not just write to file, no need to convert it in any way
            # five_mins = format_prices(broker, five_mins)
            if write:
                out = open(f'{write_to}\\nasdaq\\{stock[0]}', 'ab')
                for window in five_mins['historicals']:
                    out.write(struct.pack('d', float(window['open_price'])))
                    out.write(struct.pack('d', float(window['close_price'])))
                    out.write(struct.pack('d', float(window['high_price'])))
                    out.write(struct.pack('d', float(window['low_price'])))
                    out.write(struct.pack('L', int(window['volume'])))
                out.close()
                if verbose and current_count % 10 == 0:
                    print(f'\r{current_count / number_of_stocks * 100}% Complete', end='')
            elif verbose:
                print(five_mins)
        except Exception:
            if verbose:
                failed.append(f'NASDAQ.{stock[0]}')
            continue
    for stock in stocks['nyse']:
        try:
            five_mins = client.get_historical(stock, client.Interval.FIVE_MINUTES, client.Span.ONE_DAY)
            if write:
                out = open(f'{write_to}\\nyse\\{stock[0]}', 'ab')
                for window in five_mins['historicals']:
                    out.write(struct.pack('d', float(window['open_price'])))
                    out.write(struct.pack('d', float(window['close_price'])))
                    out.write(struct.pack('d', float(window['high_price'])))
                    out.write(struct.pack('d', float(window['low_price'])))
                    out.write(struct.pack('L', int(window['volume'])))
                out.close()
                if verbose and current_count % 10 == 0:
                    print(f'\r{current_count / number_of_stocks * 100}% Complete', end='')
            elif verbose:
                print(five_mins)
        except Exception:
            if verbose:
                failed.append(f'NYSE.{stock[0]}')
            continue

    if verbose:
        print(f'\r100% Complete')
        num_of_failed = len(failed)
        print(f'success: {int(number_of_stocks) - num_of_failed}, failed: {num_of_failed}')
    if write:
        config['last_updated'] = datetime.now(tz=timezone.utc).strftime(update_str_format)
        json.dump(config, config_file, indent=2)


if __name__ == '__main__':
    run()
