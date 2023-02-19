import csv
import os
import csv
from generate import clean_data
import matplotlib.pyplot as plt


class InsufficientFundsException(Exception):
    """
    Exception raised when an attempt is made to withdraw more money from a bank account than is available.
    """

    pass


class Bank:
    def __init__(self, balance):
        self.balance = balance
        self.balance_history = [balance]

    def get_balance(self):
        return self.balance

    def deposit(self, amount):
        self.balance += amount
        self.balance_history.append(self.balance)

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFundsException(
                "Not enough funds in the account to withdraw ${}".format(amount)
            )
        self.balance -= amount
        self.balance_history.append(self.balance)

    def filler(self):
        self.balance_history.append(self.balance)

    def get_history(self):
        return self.balance_history


class Brokerage:
    def __init__(self):
        self.position = 0.0
        self.position_history = [0.0]

    def get_position(self):
        return self.position

    def add_position(self, count):
        self.position += count
        self.position_history.append(self.position)

    def reduce_position(self, count):
        if count > self.position:
            raise InsufficientFundsException(
                f"Not enough funds in the account to withdraw {count} shared"
            )
        self.position -= count
        self.position_history.append(self.position)

    def filler(self):
        self.position_history.append(self.position)

    def get_history(self):
        return self.position_history


def write_dicts_to_csv(data, filename):
    """
    Given a list of dictionaries and a filename, writes the dictionaries to a CSV file.
    """
    fieldnames = data[0].keys()
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def determine_actions(bank_history: list):
    """
    Given the bank history, return a list of actions (buy/sell)
    """
    actions = [""]
    for i in range(len(bank_history))[1:]:
        actions.append("sell" if bank_history[i - 1] < bank_history[i] else "buy")

    return actions


def determine_delta(bank_history: list):
    """
    Given the bank history, return a list of profits
    """
    actions = [""]
    for i in range(len(bank_history))[1:]:
        actions.append(bank_history[i] - bank_history[i - 1])

    return actions


def determine_brokerage_values(brokerage_history: list, stock_prices: list):
    """
    Given the brokerage history and stock prices, return a list of the values of brokerage
    """
    brokerage_values = []
    for i in range(len(stock_prices)):
        brokerage_values.append(stock_prices[i] * brokerage_history[i])

    return brokerage_values


def determine_portfolio_values(brokerage_values: list, bank_history: list):
    """
    Given the brokerage values and bank history, return a list of portfolio values
    """
    portfolio_values = []
    for i in range(len(brokerage_values)):
        portfolio_values.append(brokerage_values[i] + bank_history[i])

    return portfolio_values


def create_transaction_sheet(
    stock_prices: list, bank_history: list, brokerage_history: list, file_name: str
):
    """
    Given the list of bank transactions and brokerage transactions, generate a transactions file
    """
    actions = determine_actions(bank_history)
    deltas = determine_delta(bank_history)
    brokerage_values = determine_brokerage_values(brokerage_history, stock_prices)
    portfolio_values = determine_portfolio_values(brokerage_values, bank_history)

    with open(file_name, mode="w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "stock price",
                "cash",
                "my stonks",
                "value of my stocks",
                "action",
                "cash delta",
                "portfolio",
            ],
        )
        writer.writeheader()
        for i in range(len(stock_prices)):
            writer.writerow(
                {
                    "stock price": stock_prices[i],
                    "cash": bank_history[i],
                    "my stonks": brokerage_history[i],
                    "value of my stocks": brokerage_values[i],
                    "action": actions[i],
                    "cash delta": deltas[i],
                    "portfolio": portfolio_values[i],
                }
            )


def maximize_bank_balance(
    prices: list, bank_account: Bank, brokerage: Brokerage, file_name: str
):
    """
    Given a list of stock prices and an initial bank balance, returns the maximum bank balance
    that can be achieved using the buy low sell high strategy, where fractional shares of stock
    can be purchased.
    """
    max_transaction_modifier = 0.5
    transaction_modifier = 0.2
    sell_streak = 1
    buy_streak = 1

    for i in range(len(prices)):
        if i > 0 and prices[i] > prices[i - 1]:
            # Sell
            profit = (
                brokerage.get_position()
                * prices[i]
                * min(transaction_modifier * buy_streak, max_transaction_modifier)
            )
            brokerage.reduce_position(
                brokerage.get_position()
                * min(transaction_modifier * buy_streak, max_transaction_modifier)
            )
            bank_account.deposit(profit)
            sell_streak += 1
            buy_streak = 1
        elif i < len(prices) - 1 and prices[i] < prices[i + 1]:
            # Buy
            shares = (bank_account.get_balance() / prices[i]) * min(
                transaction_modifier * sell_streak, max_transaction_modifier
            )
            purchase_cost = shares * prices[i]
            bank_account.withdraw(purchase_cost)
            brokerage.add_position(shares)
            buy_streak += 1
            sell_streak = 1
        elif i == len(prices) - 2:
            break
        else:
            brokerage.filler()
            bank_account.filler()

    # Sell any remaining shares at the final price
    bank_account.deposit(brokerage.get_position() * prices[-1])
    brokerage.reduce_position(brokerage.get_position())

    create_transaction_sheet(
        prices,
        bank_account.get_history(),
        brokerage.get_history(),
        f"simulate/outputs/transactions/{file_name}",
    )

    return bank_account.get_balance()


def read_stock_prices_from_csv(filename):
    """
    Given a filename, reads a CSV file with one column of stock prices and returns a list of prices.
    """
    with open(filename, "r") as file:
        reader = csv.reader(file)
        prices = [float(row[0]) for row in reader]
        return prices


def get_filenames_in_folder(folder_path):
    """
    Given a folder path, returns a list of filenames in that folder.
    """
    filenames = []
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            filenames.append(filename)
    return filenames


if __name__ == "__main__":
    folder = "simulate/outputs/data"
    files_names = get_filenames_in_folder(folder)
    initial_bank_balance = 100.0
    clean_data(f"./simulate/outputs/transactions/*")

    for file_name in files_names:
        prices = read_stock_prices_from_csv(f"{folder}/{ file_name }")
        bank_balance = maximize_bank_balance(prices, Bank(100), Brokerage(), file_name)

    folder = "simulate/outputs/transactions"
    for file_name in get_filenames_in_folder(folder):
        with open(f"{folder}/{ file_name }", "r") as f:
            reader = csv.reader(f)
            prices = [x[0] for x in reader]
            f.seek(0)
            portfolio = [x[-1] for x in reader]
            plt.cla()
            plt.figure(figsize=(12,6))
            plt.plot([float(x) for x in prices[1:]], label="prices", color="gray")
            plt.plot([float(x) for x in portfolio[1:]], label="portfolio", color="green")
            plt.plot([float(portfolio[1]) for _ in portfolio[1:]], label="baseline", color="black")
            plt.xlabel('Minutes')
            plt.ylabel('$')
            plt.title('Stonks')
            plt.savefig(f"simulate/outputs/images/{file_name}".replace(".csv",".png"))
