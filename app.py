from json.tool import main
import robin_stocks.robinhood as r
from dotenv import load_dotenv
import os


def main():
    load_dotenv()
    login = r.login(
        os.getenv("ROBINHOOD_USERNAME"),
        os.getenv("ROBINHOOD_PASSWORD")
    )


if __name__ == '__main__':
    main()
    