import csv
import os
import csv


def maximize_bank_balance(prices, initial_balance):
    """
    Given a list of stock prices and an initial bank balance, returns the maximum bank balance
    that can be achieved using the buy low sell high strategy, where fractional shares of stock
    can be purchased.
    """
    max_balance = initial_balance
    num_shares = 0
    
    for i in range(len(prices)):
        if i > 0 and prices[i] > prices[i-1]:
            # Sell all shares at the current price
            max_balance += num_shares * prices[i]
            num_shares = 0
        elif i < len(prices)-1 and prices[i] < prices[i+1]:
            # Buy as many shares as possible at the current price
            num_shares += max_balance // prices[i]
            max_balance -= num_shares * prices[i]
    
    # Sell any remaining shares at the final price
    max_balance += num_shares * prices[-1]
    
    return max_balance


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
    
    print(f"{'initial balance' : <20}", f"{'finishing bank balance' : ^20}", f"{'profits' : >20}")
    for file_name in files_names:
        prices = read_stock_prices_from_csv(f"{folder}/{ file_name }")
        bank_balance = maximize_bank_balance(prices, initial_bank_balance)
        print(f"{initial_bank_balance : <20}", f"{bank_balance : ^20}", f"{bank_balance - initial_bank_balance: >20}")