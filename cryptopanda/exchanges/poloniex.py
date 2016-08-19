from ..util import create_logger

import time
import hmac
import hashlib
import requests

from urllib.parse import urlencode

PUBLIC_URL = "https://poloniex.com/public"
TRADING_URL = "https://poloniex.com/tradingApi"


class PoloniexAPI:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    # Returns all currently existing loan orders for the specified currency
    def loan_orders(self, currency):
        payload = {"command": "returnLoanOrders",
                   "currency": currency}
        req = requests.get(PUBLIC_URL, params=payload)
        return req.json()

    def api_query(self, command, params=None):
        if params is None:
            params = {}

        params["command"] = command
        params["nonce"] = int(time.time() * 1000)

        sign = hmac.new(self.secret.encode("utf-8"), urlencode(params).encode("utf-8"), hashlib.sha512).hexdigest()
        headers = {
            "Sign": sign,
            "Key": self.key
        }
        req = requests.post(TRADING_URL, headers=headers, data=params)
        return req.json()

    # Returns all !available! balances. Means that provided loans don't count towards your balance.
    def balances(self):
        return self.api_query("returnBalances")

    # Returns the complete balances of the specified account ( exchange | margin | lending ).
    def account_balances(self, account="lending"):
        params = {"account": account}
        return self.api_query("returnAvailableAccountBalances", params)

    # Returns all !available! balance, balance on orders and the estimated BTC value of the balance on all accounts.
    def complete_balance(self):
        params = {"account": "all"}
        return self.api_query("returnCompleteBalances", params)

    # Returns all currently open loan offers
    def open_loan_offers(self):
        return self.api_query("returnOpenLoanOffers")

    # Returns all currently provided loans
    def active_loans(self):
        return self.api_query("returnActiveLoans")

    def create_loan_offer(self, currency, amount, rate, duration=2, renew=0):
        params = {
            "currency": currency,
            "amount": amount,
            "duration": duration,
            "lendingRate": rate,
            "autoRenew": renew
        }
        return self.api_query("createLoanOffer", params)

    def cancel_loan_offer(self, currency, order):
        params = {
            "currency": currency,
            "orderNumber": order
        }
        return self.api_query("cancelLoanOffer", params)


class Poloniex:
    def __init__(self, key, secret, config):
        self.api = PoloniexAPI(key, secret)
        self.options = config["options"]
        self.logger = create_logger(config["name"])

    def lending_balance(self):
        balance = dict(self.api.account_balances()["lending"])
        balance = map(lambda t: (t[0], float(t[1])), balance.items())
        return dict(balance)

    def loan_rates(self, currency):
        loans = self.api.loan_orders(currency)["offers"]
        return list(map(lambda x: float(x["rate"]), loans))

    def sanitize_rate(self, rate):
        if rate < self.options["minLendingRate"]:
            rate = self.options["minLendingRate"]

        if rate > self.options["maxLendingRate"]:
            rate = self.options["maxLendingRate"]

        return rate

    def is_legit(self, balance, rate):
        legit_balance = balance > self.options["minLendingAmount"]
        legit_rate = self.options["minLendingRate"] < rate < self.options["maxLendingRate"]
        return legit_balance and legit_rate

    def loan(self, currency, balance, rate):
        if not self.is_legit(balance, rate):
            msg = """Either the rate is not sanitized or the balance is to low to create an offer!
                    Balance: {} | Rate: {}""".format(balance, rate)
            self.logger.error(msg)
        else:
            offer = self.api.create_loan_offer(currency, balance, rate)
            if offer.get("error"):
                self.logger.error("Failed to create offer. Error: {}".format(offer["error"]))
            else:
                msg = """Created offer to lend {} {} for {}% per day.
                        ID: {}""".format(balance, currency, rate, offer["orderID"])
                self.logger.info(msg)
