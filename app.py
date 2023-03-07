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
    """
    Robo-trader
    """

    def __init__(self, ticker: str, debug: bool = False):
        """
        Constructor

        Args:
            ticker (str): Stock ticker symbol
            debug (bool, optional): Whether or not to print debug statements.
                Defaults to False.
        """
        self.MAX_TRANSACTION_MODIFIER = 0.5
        self.TRANSACTION_MODIFIER = 0.2
        self.TICKER = ticker
        self.DEBUG = debug
        self.prices = []
        self.sell_streak = 1
        self.buy_streak = 1

    def setup(self):
        """
        Login and load env variables
        """
        if self.DEBUG:
            print("Setting up")
        load_dotenv()
        r.login(os.getenv("ROBINHOOD_USERNAME"), os.getenv("ROBINHOOD_PASSWORD"))

    def teardown(self):
        """
        Logs out and resets
        """
        if self.DEBUG:
            print("Tearing Down")
        r.logout()

    def get_buying_power(self):
        """
        Returns buyings power (USD)

        Returns:
            float: Buying power (USD)
        """
        buying_power = r.profiles.load_account_profile()["cash_balances"][
            "buying_power"
        ]
        return float(buying_power)

    def get_equity(self, symbol: str):
        """
        Returns equity for a symbol

        Args:
            symbol (str): Stock ticker symbol

        Returns:
            float: Equity of symbol
        """
        equity = account.build_holdings()[symbol]["equity"]
        return float(equity)

    def buy(self, symbol: str, value: float):
        """
        Buys a dollar amount of a stock

        Args:
            symbol (str): Stock ticker symbol
            value (float): USD

        Returns:
            dict: Order data
        """
        if self.DEBUG:
            print({"symbol": symbol, "value": value, "action": "buy"})

        order = orders.order_buy_fractional_by_price(
            symbol,
            value,
            timeInForce="gfd",
            jsonify=True,
        )
        self.buy_streak += 1
        self.sell_streak = 1

        return order

    def sell(self, symbol: str, value: float):
        """
        Sells a dollar amount of a stock

        Args:
            symbol (str): Stock ticker symbol
            value (float): USD

        Returns:
            dict: Order data
        """
        if self.DEBUG:
            print({"symbol": symbol, "value": value, "action": "sell"})

        order = orders.order_sell_fractional_by_price(
            symbol,
            value,
            timeInForce="gfd",
            jsonify=True,
        )
        self.sell_streak += 1
        self.buy_streak = 1

        return order

    def in_trading_hours(self):
        """
        Determines if able to buy/sell

        Returns:
            bool: Ability to trade
        """
        market_open = markets.get_market_today_hours("XNYS")["is_open"]

        return market_open

    def trade(self):
        """
        Buy/sell
        """
        latest_price = stonks.get_latest_price(self.TICKER)[0]

        if not self.in_trading_hours():
            print("Market Closed")
            return

        self.prices.append({"time": datetime.now(timezone.utc), "price": latest_price})

        if len(self.prices) == 1:
            pass
        elif self.prices[-2]["price"] < self.prices[-1]["price"]:
            # Sell
            amount = self.get_equity(self.TICKER) * min(
                self.TRANSACTION_MODIFIER * self.sell_streak,
                self.MAX_TRANSACTION_MODIFIER,
            )
            self.sell(symbol=self.TICKER, value=amount)
        else:
            # Buy
            amount = self.get_buying_power() * min(
                self.TRANSACTION_MODIFIER * self.buy_streak,
                self.MAX_TRANSACTION_MODIFIER,
            )
            self.buy(symbol=self.TICKER, value=amount)


def main():
    s = Stonks("SPY", debug=True)
    s.setup()
    schedule.every(10).seconds.do(s.trade)

    while True:
        schedule.run_pending()
        print(".", end="")
        time.sleep(1)


if __name__ == "__main__":
    main()
