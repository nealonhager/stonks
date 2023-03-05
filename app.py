from json.tool import main
import robin_stocks.robinhood as r
import robin_stocks.robinhood.stocks as stonks
import robin_stocks.robinhood.orders as orders
import robin_stocks.robinhood.account as account
import robin_stocks.robinhood.markets as markets
from dotenv import load_dotenv
import os
import json
import schedule
import time
from datetime import datetime, timezone


class Stonks:
    def __init__(self, ticker, debug=False):
        self.MAX_TRANSACTION_MODIFIER = 0.5
        self.TRANSACTION_MODIFIER = 0.2
        self.TICKER = ticker
        self.DEBUG = debug
        self.historical = []
        self.sell_streak = 1
        self.buy_streak = 1

    def setup(self):
        if self.DEBUG:
            print("Setting up")
        load_dotenv()
        r.login(
            os.getenv("ROBINHOOD_USERNAME"),
            os.getenv("ROBINHOOD_PASSWORD")
        )

    def teardown(self):
        if self.DEBUG:
            print("Tearing Down")
        r.logout()
        historical = []

    def get_buying_power(self):
        buying_power = r.profiles.load_account_profile()["cash_balances"]["buying_power"]
        return buying_power

    def buy(self, symbol:str, value: float):
        if self.DEBUG:
            print({
                "symbol": symbol,
                "value": value,
                "action": "buy"
            })

        order = orders.order_buy_fractional_by_price(symbol, value, timeInForce='gfd', jsonify=True)
        self.buy_streak += 1
        self.sell_streak = 1

        return order

    def sell(self, symbol:str, value: float):
        if self.DEBUG:
            print({
                "symbol": symbol,
                "value": value,
                "action": "sell"
            })

        order = orders.order_sell_fractional_by_price(symbol, value, timeInForce='gfd', jsonify=True)
        self.sell_streak += 1
        self.buy_streak = 1

        return order

    def in_trading_hours(self):
        market_open = markets.get_market_today_hours("XNYS")["is_open"]

        return market_open

    def trade(self):
        latest_price = stonks.get_latest_price(self.TICKER)[0]
        buying_power = self.get_buying_power()

        if not self.in_trading_hours():
            print("Market Closed")
            return

        self.historical.append({
            "time": datetime.now(timezone.utc),
            "price": latest_price
        })

        if len( self.historical ) == 1:
            pass
        elif self.historical[-2]["price"] < self.historical[-1]["price"]:
            self.sell(symbol=self.TICKER, value=1)
        else:
            self.buy(symbol=self.TICKER, value=1)


def main():
    s = Stonks("SPY", debug=True)
    s.setup()
    schedule.every(10).seconds.do(s.trade)
    
    while True:
        schedule.run_pending()
        print(".", end="")
        time.sleep(1)

    s.teardown()


if __name__ == '__main__':
    main()
    