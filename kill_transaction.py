"""
Usage:
    ACG-KillTransactionLogger <instance>
    ACG-KillTransactionLogger ( -h | --version)

Positional Arguments:
    <instance>      Config instance name

Options:
    -h              Show this screen
    --version       Show Version Information
"""
from TM1py import TM1Service
from docopt import docopt
from TM1py.Exceptions import TM1pyException
from configparser import ConfigParser
import os
import sys
from utilities import DB, PySecrets

APP_NAME = 'ACG-KillTransactionLogger'
APP_VERSION = '1.0'
FILE = ''


def set_current_directory() -> None:
    global FILE
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(__file__)
    directory = os.path.dirname(application_path)
    FILE = os.path.join(application_path, 'config.ini')
    os.chdir(directory)


def get_tm1_config(instance: str) -> dict:
    _user = None
    _pass = None
    config = ConfigParser()
    config.read(FILE)
    base_url = config[instance]['base_url']
    db = DB()
    secret = PySecrets()
    results = db.retrieve_secrets(secret=instance)
    for result in results:
        _user = result.username
        _pass = result.password
    username = secret.make_public(secret=_user)
    password = secret.make_public(secret=_pass)
    _config = {
        'base_url': base_url,
        'namespace': 'LDAP',
        'user': username,
        'password': password,
        'ssl': True,
        'verify': True,
        'async_requests_mode': True
    }
    return _config


def main(instance: str) -> None:
    config = get_tm1_config(instance=instance)
    try:
        with TM1Service(**config) as tm1:
            threads = tm1.monitoring.get_threads()
            for thread in threads:
                if thread['Context'] == 'ACG-GetTransactions':
                    tm1.monitoring.cancel_thread(thread['ID'])
    except TM1pyException as t:
        print(t)


if __name__ == '__main__':
    cmd_args = docopt(__doc__, version=f"{APP_NAME}, Version: {APP_VERSION}")
    _instance = cmd_args.get("<instance>")
    set_current_directory()
    main(instance=_instance)
