import json
import logging

import os
from os import path


LOG_DIR = "log"


def read_json(filename):
    with open(filename) as file:
        data = json.load(file)
    return data


def create_logger(name):
    if not path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(path.join(LOG_DIR, "{}.log".format(name)))
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger
