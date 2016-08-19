from cryptopanda import CLI
from cryptopanda.exchanges import Poloniex
from cryptopanda.lending import lend
from cryptopanda.util import read_json, create_logger

import time
import schedule
from docopt import docopt


if __name__ == "__main__":
    arguments = docopt(CLI, version="CryptoPanda 0.1")
    config = read_json("config.json")

    polo = Poloniex(config["key"], arguments["--poloniex"], config)

    schedule.every(5).minutes.do(lend, polo)

    while True:
        schedule.run_pending()
        time.sleep(1)
