from statistics import mean, median


# Currently simplistic, more sophisticated version coming soon...
def _calc_rate(loans):
    loans = loans[:10]
    return max(mean(loans), median(loans))


def lend(exchange):
    balances = exchange.lending_balance()
    for currency, balance in balances.items():
        rate = exchange.sanitize_rate(_calc_rate(exchange.loan_rates(currency)))
        exchange.loan(currency, balance, rate)
