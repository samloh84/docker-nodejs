import errno
import os
import yaml
from datetime import timedelta, datetime

from timestamp import *


def load_file(filename):
    filename = os.path.abspath(filename)
    with open(filename, 'r') as f:
        return f.read()


def load_yaml(filename):
    return yaml.safe_load(load_file(filename))


def print_yaml(data):
    print(yaml.safe_dump(data, default_flow_style=False))


def write_file(filename, data):
    filename = os.path.abspath(filename)
    file_dir = os.path.dirname(filename)
    mkdirs(file_dir)
    with open(filename, 'w') as f:
        f.write(data.encode('utf8'))


def write_yaml(filename, data):
    write_file(filename, yaml.safe_dump(data, default_flow_style=False))


def mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass


def load_data_file(filename):
    current_datetime = datetime.now()
    current_timestamp = datetime_to_timestamp(current_datetime)
    try:
        data = load_yaml(filename)
        last_updated = data.get('last_updated')
        update = False
        if last_updated is not None:
            last_updated = timestamp_to_datetime(data.get('last_updated'))
            if last_updated + timedelta(days=1) <= current_datetime:
                update = True
        return data, last_updated, update
    except:
        pass

    return None
