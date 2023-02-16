"""
Usage:
    ACG-ProcessLog <instance> <out_file>
    ACG-ProcessLog (-h | --version)

Positional Arguments:
    <instance>  Name of config.ini entry
    <out_file>  Path and filename to output

Options:
    -h          Show this screen
    --version   Show version information

© Copyright 2023 - ACGI (http://www.acgi.com)
"""
import pandas as pd
from TM1py import TM1Service
from docopt import docopt

from utilities import get_tm1_config

APP_NAME = 'ACG-ProcessLog'
APP_VERSION = '1.0'


def main(file: str, instance: str) -> None:
    msg = []

    config = get_tm1_config(instance=instance)
    with TM1Service(**config) as tm1:
        messages = tm1.server.get_message_log_entries(reverse=True)
    for message in messages:
        if message['Logger'] == "TM1.Process":
            if "user" in message['Message'] or "finished" in message['Message']:
                tmst = message['TimeStamp'].split("T")
                msg.append((tmst[0], tmst[1].replace('Z', ''), message['Message'].replace("\r\n", " ")))

    df = pd.DataFrame(msg)
    df.columns = ['Date', 'Time', 'Message']
    df.to_csv(file, index=False)


if __name__ == '__main__':
    cmd_args = docopt(__doc__, version=f"Application: {APP_NAME}, Version={APP_VERSION} "
                                       f"\n© Copyright 2023 - ACGI (http://www.acgi.com)")
    _file = cmd_args.get("<out_file>")
    _instance = cmd_args.get("<instance>")
    main(file=_file, instance=_instance)
