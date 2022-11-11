"""
Usage:
    get_transactions <instance> <cube> <since>
    get_transactions (-h | --version)

Positional Arguments:
    <instance>  Config instance name
    <cube>      Cube name to retrieve
    <since>     Timestamp of first entry to retrieve

Options:
    -h          Show this screen
    --version   Show Version Information
"""
import time

import pandas as pd
from TM1py import TM1Service
from TM1py.Exceptions import TM1pyException
from docopt import docopt

from baselogger import logger, APP_NAME, application_path
from utilities import get_tm1_config
from datetime import datetime

APP_VERSION = '1.0'


def main(instance: str, cube: str, since: datetime):
    config = get_tm1_config(instance=instance)
    try:
        with TM1Service(**config) as tm1:
            entries = tm1.server.get_transaction_log_entries(cube=cube, since=since)
        df = pd.DataFrame(entries)
        df.to_csv(fr"{application_path}\{cube}.csv", index=False)
    except TM1pyException as t:
        logger.info(t)


if __name__ == '__main__':
    start = time.perf_counter()
    cmd_args = docopt(__doc__, version=f"{APP_NAME}, Version: {APP_VERSION}")
    logger.info(f"Starting {APP_NAME}.  Searching transactions for '{cmd_args['<cube>']}', "
                f"since '{cmd_args['<since>']}'")
    _instance = cmd_args.get('<instance>')
    _cube = cmd_args.get('<cube>')
    _since_time = cmd_args.get('<since>')
    year = int(_since_time[0:4])
    month = int(_since_time[5:7])
    day = int(_since_time[8:10])
    hour = int(_since_time[11:13])
    minute = int(_since_time[14:16])
    second = int(_since_time[17:19])
    since_time = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    main(instance=_instance, cube=_cube, since=since_time)
    end = time.perf_counter()
    logger.info(f"Finished process in {round(end - start, 2)} seconds")
