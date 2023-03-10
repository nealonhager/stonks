import random
import matplotlib.pyplot as plt
import time
import calendar
import csv
import os
import glob
import csv
import random


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
    iterations = 10

    # Generate daily stock prices
    for _ in range(iterations):
        price_history = [initial_price]
        for _ in range(1, timeline):
            # Calculate the new price based on the previous day's price
            last_price = price_history[-1]
            price_change = price_variance * random.gauss(0.0001, .5)
            new_price = last_price + price_change
            # Add the new price to the price history list
            price_history.append(new_price)

        first_price = price_history[0]
        last_price = price_history[-1]
        write_numbers_to_csv(price_history, f"simulate/outputs/data/{initial_price}_{first_price}_{last_price}.csv")


if __name__ == "__main__":
    generate_data()