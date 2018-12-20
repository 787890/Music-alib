# -*- coding: utf-8 -*-

import logging
import json

LOG_LEVEL = logging.DEBUG   # DEBUG|INFO|WARNING|ERROR|CRITICAL
LOG_FILE = 'download.log' or False
LOG_FORMAT = '%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s'


def get_logger():
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)
    ch.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(ch)

    # if LOG_FILE:
    #     fh = logging.FileHandler(LOG_FILE)
    #     fh.setLevel(LOG_LEVEL)
    #     fh.setFormatter(formatter)
    #     logger.addHandler(fh)

    return logger


def json_format(data, indent=4, ensure_ascii=False):
    return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)

