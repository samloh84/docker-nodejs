import errno
import re
import urlparse

import grequests
import os
from datetime import datetime, timedelta
import time

import requests
import semver
import yaml
from bs4 import BeautifulSoup

from pydash import get as _get, set_ as _set, flatten as _flatten
from pydash.collections import some as _some, every as _every, flat_map_deep as _flat_map_deep


def http_get(url, headers=None):
    return requests.get(url, headers=headers)


def http_multiget(urls, headers=None):
    return zip(urls, grequests.map([grequests.get(url, headers=headers) for url in urls]))


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


def datetime_to_timestamp(date=None):
    if date is None:
        date = datetime.now()
    return int(time.mktime(date.timetuple()))


def timestamp_to_datetime(timestamp):
    if timestamp is None or timestamp == "":
        return None
    return datetime.fromtimestamp(int(timestamp))


def mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass


def parse_html_for_urls(html, url, regex_filters=None):
    bs = BeautifulSoup(html, 'html.parser')
    links = bs.find_all('a', href=True)
    urls = map(lambda link: urlparse.urljoin(url, link['href'], allow_fragments=False), links)

    if regex_filters is None:
        return urls

    if not isinstance(regex_filters, list):
        regex_filters = [regex_filters]

    filtered_urls = []
    if isinstance(regex_filters, list):
        for url in urls:
            for regex_filter in regex_filters:
                if regex_filter.search(url) is not None:
                    filtered_urls.append(url)
                    break
    return filtered_urls


class PatternTree:
    def __init__(self, tree):
        self.pattern_tree = {}

        def build_pattern_tree(subtree, path=None):
            if path is None:
                path = []
            for key, value in subtree.iteritems():
                if isinstance(value, dict):
                    build_pattern_tree(value, path + [key])
                else:
                    _set(self.pattern_tree, path + [key], re.compile(value))

        build_pattern_tree(tree)

    def search(self, string):
        def search_pattern_tree(subtree, path=None):
            if path is None:
                path = []
            for key, value in subtree.iteritems():
                if isinstance(value, dict):
                    recursive_return = search_pattern_tree(value, path + [key])
                    if recursive_return is not None:
                        return recursive_return
                else:
                    match = value.search(string)
                    if match is not None:
                        return match, path if key == 'pattern' else path + [key]
            return None

        return search_pattern_tree(self.pattern_tree)


def filter_versions(versions, version_constraints=None, sort_criteria=None):
    if sort_criteria is None:
        sort_criteria = ['major']

    if version_constraints is not None:
        if not isinstance(version_constraints, list):
            version_constraints = [version_constraints]

    filtered_versions = {}

    for version in versions:
        version_info = semver.parse_version_info(version)

        if version_constraints is not None:
            semver_match_lambda = lambda vc: semver.match(version, vc)
            vc_lambda = lambda vc: _some(vc, semver_match_lambda) if isinstance(vc, list) else semver_match_lambda(vc)

            if not _every(version_constraints, vc_lambda):
                continue

        path = map(lambda criteria: str(getattr(version_info, criteria)), sort_criteria)

        current_version = _get(filtered_versions, path)
        if current_version is None or semver.compare(version, current_version) > 0:
            _set(filtered_versions, path, version)

    filtered_versions = _flat_map_deep(filtered_versions)

    return filtered_versions


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


def list_docker_hub_image_tags(repository):
    url = "https://hub.docker.com/v2/repositories/" + repository + "/tags"
    request_headers = {'Accept': 'application/json'}

    tags = []

    while url is not None:
        response_data = http_get(url, headers=request_headers).json()
        tags += response_data["results"]
        url = response_data["next"]

    return tags
