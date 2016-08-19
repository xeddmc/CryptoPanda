"""
CryptoPanda v0.1

Usage:
    run.py --poloniex=<s>
    run.py (-h | --help)
    run.py (-v | --version)

Options:
    -h --help           Show this screen.
    -v --version        Show installed version.
    --poloniex=<s>      Provide secret for Poloniex API key.
"""

from cryptopanda.exchanges import Poloniex
from .lending import lend
from .util import create_logger

from decimal import Decimal

CLI = __doc__
SATOSHI = Decimal(10) ** -8
