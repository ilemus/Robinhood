from datapackage import Package
import sqlite3
import json


def download_nasdaq():
    conn = sqlite3.connect('us_equities.db')
    conn.execute('CREATE TABLE IF NOT EXISTS nasdaq (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol CHARACTER(6), company_name TEXT)')
    conn.commit()
    package = Package('https://datahub.io/core/nasdaq-listings/datapackage.json')

    try:
        for resource in package.resources:
            if 'derivedFrom' not in resource.descriptor['datahub']:
                continue
            if resource.descriptor['datahub']['type'] == 'derived/json' and resource.descriptor['datahub']['derivedFrom'][0] == 'nasdaq-listed-symbols':
                companies = json.loads(resource.raw_read())
                for company in companies:
                    conn.execute(f'SELECT symbol FROM nasdaq WHERE symbol="{company["Symbol"]}"')
                    cur = conn.cursor()
                    if cur.fetchone() is None:
                        conn.execute(f'INSERT INTO nasdaq(symbol, company_name) VALUES("{company["Symbol"]}","{company["Company Name"]}")')
    except Exception:
        conn.close()
        raise
    conn.commit()
    conn.close()


def download_nyse():
    conn = sqlite3.connect('us_equities.db')
    conn.execute('CREATE TABLE IF NOT EXISTS nyse (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol CHARACTER(5), company_name TEXT)')
    conn.commit()
    package = Package('https://datahub.io/core/nyse-other-listings/datapackage.json')

    try:
        for resource in package.resources:
            if 'derivedFrom' not in resource.descriptor['datahub']:
                continue
            if resource.descriptor['datahub']['type'] == 'derived/json' and \
                    resource.descriptor['datahub']['derivedFrom'][0] == 'nyse-listed':
                companies = json.loads(resource.raw_read())
                for company in companies:
                    conn.execute(f'SELECT symbol FROM nyse WHERE symbol="{company["Symbol"]}"')
                    cur = conn.cursor()
                    if cur.fetchone() is None:
                        conn.execute(
                            f'INSERT INTO nyse(symbol, company_name) VALUES("{company["Symbol"]}","{company["Company Name"]}")')
    except Exception:
        conn.close()
        raise
    conn.commit()
    conn.close()


if __name__ == '__main__':
    download_nasdaq()
    download_nyse()
