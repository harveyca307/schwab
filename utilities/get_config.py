from utilities import DB, PySecrets
from configparser import ConfigParser
from baselogger import application_path, APP_NAME
from getpass import getpass
import os

FILE = os.path.join(application_path, "config.ini")


def get_tm1_config(instance: str) -> dict:
    _user = None
    _pass = None
    config = ConfigParser()
    config.read(FILE)
    if not config.has_section(instance):
        _config = create_section(instance=instance, config=config)
    else:
        base_url = config[instance]['base_url']
        db = DB()
        results = db.retrieve_secrets(secret=instance)
        for result in results:
            _user = result.username
            _pass = result.password
        secrets = PySecrets()
        username = secrets.make_public(secret=_user)
        password = secrets.make_public(secret=_pass)
        _config = {
            'base_url': base_url,
            'namespace': 'LDAP',
            'user': username,
            'password': password,
            'ssl': True,
            'verify': True,
            'async_requests_mode': True,
            'session_context': APP_NAME
        }
    return _config


def create_section(instance: str, config: ConfigParser) -> dict:
    while True:
        baseurl = input(f"Enter base url for {instance}: ")
        if not baseurl:
            print("BaseURL is required")
            continue
        else:
            break
    if baseurl.endswith('/'):
        baseurl = baseurl[:-1]
    while True:
        servername = input(f"Enter server name for {instance}: ")
        if not servername:
            print("Servername is required")
            continue
        else:
            break
    while True:
        username = input(f"Enter non-interactive username for {instance}: ")
        if not username:
            print("Username is required")
            continue
        else:
            break
    while True:
        password = getpass(f"Enter password for {username}: ")
        if not password:
            print("Password is required")
            continue
        else:
            break
    secrets = PySecrets()
    _user = secrets.make_secret(secret=username)
    _pass = secrets.make_secret(secret=password)
    db = DB()
    db.create_secrets(secret=instance, username=_user, password=_pass)
    _config = {
        'base_url': baseurl + "/tm1/api/" + servername,
        'namespace': 'LDAP',
        'ssl': True,
        'verify': True,
        'async_requests_mode': True,
        'session_context': APP_NAME
    }
    config[instance] = _config
    config.write(open(FILE, 'w'))
    _config['user'] = username
    _config['password'] = password
    return _config
