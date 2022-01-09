# Configure cache for backward compatability
import sys
import math
from .Constants import SERVER_TO_EPOCH_TIME_DIVISOR, EPOCH_TIME_DIGITS
from python_log_indenter import IndentedLoggerAdapter
import time
import logging
from termcolor import colored
from colorama import init
init()
if sys.version_info[1] == 7:
    from functools import lru_cache
    cache = lru_cache(maxsize=500)
else:
    from functools import cache


def get_current_epoch() -> float:
    """ Get current time in epoch """
    return time.time()


def rfc339_to_epoch(rfc339time: str) -> float:
    """ Converts RFC339 time to epoch i.e 2021-11-04T22:00:00Z ->  1636059600.0"""
    return time.mktime(time.strptime(rfc339time, '%Y-%m-%dT%H:%M:%SZ'))


def to_rfc339(t: time.struct_time) -> str:
    """ Converts time.struct to RFC339 time"""
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', t)


def fix_epoch(x: float) -> float:
    """ Fixes the epoch time what we know is acceptable! i.e 10 digits
        Normally, the times we get from servers have 13 digits and its
        not acceptable by the any time or datetime modules"""
    x = float(x)
    digits = int(math.log10(x)) + 1
    return int(x / 10**int(digits - EPOCH_TIME_DIGITS)) if digits > 10 else x


def get_local_time() -> int:
    return time.mktime(time.localtime())


def get_local_offset(Time: float) -> int:
    return Time - get_local_time()


def add_time_offset(Time: float, Offset=0.0) -> float:
    return Time + Offset


def get_local_time_str():
    return get_time_str(get_local_time())


def get_time_str(Time: float) -> str:
    """ Human readable time format """
    if int(math.log10(Time)) + 1 > 10:
        Time = Time / SERVER_TO_EPOCH_TIME_DIVISOR
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Time))


def get_date_str(Time: float) -> str:
    """ Human readable date format """
    if int(math.log10(Time)) + 1 > 10:
        Time = Time / SERVER_TO_EPOCH_TIME_DIVISOR
    return time.strftime('%Y-%m-%d', time.localtime(Time))


def get_local_date_str():
    return get_date_str(get_local_time())


def get_date_str(Time: float) -> str:
    """ Human readable Date format """
    if int(math.log10(Time)) + 1 > 10:
        Time = Time / SERVER_TO_EPOCH_TIME_DIVISOR
    return time.strftime('%Y-%m-%d', time.localtime(Time))


def get_minutes_str(Seconds: float) -> str:
    return f'{round(Seconds)/60}m'


def api_delay(Time=0.1):
    # Stop from weighting out the API calls
    time.sleep(Time)


class Colors:
    # https://stackoverflow.com/a/287944
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def BLUE(x: str) -> str:
    return colored(x, 'blue')


def GREEN(x: str) -> str:
    return colored(x, 'green')


def RED(x: str) -> str:
    return colored(x, 'red')


def BOLD(x: str) -> str:
    return colored(x, attrs='bold')


def color(x: float) -> str:
    return RED(x) if x < 0.0 else GREEN(x)


def change_percent(Initial: float, Final: float) -> float:
    assert Initial != 0.0
    return round(((Final - Initial) / Initial) * 100, 3)


def get_indentedLogger(loggername:str) -> IndentedLoggerAdapter:
    return IndentedLoggerAdapter(
        logging.getLogger(loggername),
        indent_char='.',
        spaces=4)
