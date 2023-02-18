from json.tool import main
import robin_stocks.robinhood as r
import robin_stocks.robinhood.stocks as stonks
import robin_stocks.robinhood.orders as orders
import robin_stocks.robinhood.account as account
from dotenv import load_dotenv
import os
import json
import schedule
import time


def setup():
    load_dotenv()
    r.login(
        os.getenv("ROBINHOOD_USERNAME"),
        os.getenv("ROBINHOOD_PASSWORD")
    )


def teardown():
    r.logout()


def get_buying_power():
    buying_power = r.profiles.load_account_profile()["cash_balances"]["buying_power"]
    print(f"buying_power {buying_power}")
    return buying_power


def main():
    setup()
    get_buying_power()
    schedule.every().minute.do(get_buying_power)
    
    while True:
        schedule.run_pending()
        time.sleep(10)

    # orders.order_buy_fractional_by_price(symbol, amountInDollars, timeInForce='gfd', extendedHours=False, jsonify=True)
    # https://robin-stocks.readthedocs.io/en/latest/robinhood.html#robin_stocks.robinhood.orders.order_buy_fractional_by_price
    # 'gtc' = good until cancelled. 'gfd' = good for the day. 'ioc' = immediate or cancel. 'opg' execute at opening.


if __name__ == '__main__':
    main()
    