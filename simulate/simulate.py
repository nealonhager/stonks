import csv
import os
import csv
from generate import write_numbers_to_csv


class InsufficientFundsException(Exception):
    """
    Exception raised when an attempt is made to withdraw more money from a bank account than is available.
    """
    pass


class Bank:
    def __init__(self, balance):
        self.balance = balance
        self.balance_history=[balance]

    def get_balance(self):
        return self.balance

    def deposit(self, amount):
        self.balance += amount
        self.balance_history.append(self.balance)

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFundsException("Not enough funds in the account to withdraw ${}".format(amount))
        self.balance -= amount
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
            raise InsufficientFundsException(f"Not enough funds in the account to withdraw {count} shared")
        self.position -= count
        self.position_history.append(self.position)

    def get_history(self):
        return self.position_history


def write_dicts_to_csv(data, filename):
    """
    Given a list of dictionaries and a filename, writes the dictionaries to a CSV file.
    """
    fieldnames = data[0].keys()
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def maximize_bank_balance(prices: list, bank_account: Bank, brokerage: Brokerage):
    """
    Given a list of stock prices and an initial bank balance, returns the maximum bank balance
    that can be achieved using the buy low sell high strategy, where fractional shares of stock
    can be purchased.
    """
    log = []
    transaction_modifier = 0.5
    
    for i in range(len(prices)):
        temp = {"price":prices[i]}
        if i > 0 and prices[i] > prices[i-1]:
            # Sell all shares at the current price
            temp["action"] = "sell"
            profit = brokerage.get_position() * prices[i] * transaction_modifier
            brokerage.reduce_position(brokerage.get_position() * transaction_modifier)
            bank_account.deposit(profit)
        elif i < len(prices)-1 and prices[i] < prices[i+1]:
            # Buy
            shares = (bank_account.get_balance() // prices[i]) * transaction_modifier
            purchase_cost = shares * prices[i]
            bank_account.withdraw(purchase_cost)
            brokerage.add_position(shares)
            temp["action"] = "buy"

        log.append(temp)
    
    # Sell any remaining shares at the final price
    bank_account.deposit(brokerage.get_position() * prices[-1])
    brokerage.reduce_position(brokerage.get_position())

    # Make transaction CSVs
    write_dicts_to_csv(log, "log.csv")
    write_numbers_to_csv(bank_account.get_history(),"bank.csv")
    write_numbers_to_csv(brokerage.get_history(), "brokerage.csv")
    
    return bank_account.get_balance()


def read_stock_prices_from_csv(filename):
    """
    Given a filename, reads a CSV file with one column of stock prices and returns a list of prices.
    """
    with open(filename, 'r') as file:
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
    
    # print(f"{'initial balance' : <20}", f"{'finishing bank balance' : ^20}", f"{'profits' : >20}")
    for file_name in files_names[:1]:
        prices = read_stock_prices_from_csv(f"{folder}/{ file_name }")
        bank_balance = maximize_bank_balance(prices, Bank(100), Brokerage())
        # print(f"{initial_bank_balance : <20}", f"{bank_balance : ^20}", f"{bank_balance - initial_bank_balance: >20}")