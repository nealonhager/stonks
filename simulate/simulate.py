import random
import matplotlib.pyplot as plt
import time
import calendar
import csv
import os
import glob
import csv
import random


def plot_numbers(numbers, filename, override=False):
    """
    Plots a line graph of a list of numbers and saves it as an image
    """
    plt.plot(numbers)
    plt.xlabel('Minutes')
    plt.ylabel('$')
    plt.title('Stonks')
    if override:
        plt.savefig("simulate/outputs/graph.png")
    else:
        plt.savefig(filename)
    plt.gca().set_prop_cycle(None)


def write_numbers_to_csv(numbers, filename):
    """
    Writes a list of numbers to a CSV file
    """
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for num in numbers:
            writer.writerow([num])


def clean_data(path):
    files = glob.glob(path)
    for f in files:
        os.remove(f)


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


def generate_data():
    """
    Generates sample stock data for a single trading day
    """
    clean_data("./simulate/outputs/data/*")
    clean_data("./simulate/outputs/images/*")

    # Define initial variables
    timeline = 390 # 390 trading minutes in a day
    initial_price = 100
    price_variance = 0.1
    price_history = [initial_price]
    iterations = 10

    # Generate daily stock prices
    for _ in range(iterations):
        for _ in range(1, timeline):
            # Calculate the new price based on the previous day's price
            last_price = price_history[-1]
            price_change = price_variance * random.gauss(0.0001, .5)
            new_price = last_price + price_change
            # Add the new price to the price history list
            price_history.append(new_price)

        now = calendar.timegm(time.gmtime())
        plot_numbers(price_history, f"simulate/outputs/images/{now}_{price_history[-1]-price_history[0]}.png")
        write_numbers_to_csv(price_history, f"simulate/outputs/data/{now}_{price_history[-1]-price_history[0]}.csv")


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