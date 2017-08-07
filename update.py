#!/usr/bin/env python2

import os, sys, json, re, urlparse, errno, time, argparse
from datetime import datetime, timedelta
import yaml, semver, requests, grequests, jinja2
from bs4 import BeautifulSoup

NODEJS_DISTRIBUTION_URL = "https://nodejs.org/dist/"


def http_get(url, headers=None):
    return requests.get(url, headers=headers)


def http_multiget(urls, headers=None):
    return zip(urls, grequests.map([grequests.get(url, headers=headers) for url in urls]))


def list_docker_hub_image_tags(repository):
    url = "https://hub.docker.com/v2/repositories/" + repository + "/tags"
    request_headers = {'Accept': 'application/json'}

    tags = []

    while url is not None:
        response_data = http_get(url, headers=request_headers).json()
        tags += response_data["results"]
        url = response_data["next"]

    return tags


def list_nodejs_versions():
    nodejs_distribution_html = requests.get(NODEJS_DISTRIBUTION_URL).text
    nodejs_distribution_soup = BeautifulSoup(nodejs_distribution_html, 'html.parser')

    version_pattern = re.compile('^v(\d+\.\d+\.\d+)/$')

    nodejs_version_links = nodejs_distribution_soup.find_all('a', href=version_pattern)

    nodejs_versions = {}
    for nodejs_version_link in nodejs_version_links:
        nodejs_version = version_pattern.match(nodejs_version_link['href']).group(1)
        nodejs_version_url = urlparse.urljoin(NODEJS_DISTRIBUTION_URL, nodejs_version_link['href'])

        nodejs_versions[nodejs_version] = {'link': nodejs_version_url}

    return nodejs_versions


def list_nodejs_version_files(nodejs_versions):
    def parse_html(nodejs_version_url, nodejs_version_html):
        patterns = {
            'signatures': re.compile('^SHASUMS256(\.txt(\.asc|\.sig)?)$'),
            'binaries': re.compile('^node-v\d+\.\d+\.\d+-linux-x64(\.tar\.(gz|xz))$'),
            'source': re.compile('^node-v\d+\.\d+\.\d+(\.tar\.(gz|xz))$')
        }

        nodejs_version_soup = BeautifulSoup(nodejs_version_html, 'html.parser')

        nodejs_version_data = {}

        for key, pattern in patterns.iteritems():
            nodejs_version_data[key] = {}
            nodejs_version_file_links = nodejs_version_soup.find_all('a', href=pattern)
            for nodejs_version_file_link in nodejs_version_file_links:
                filename = nodejs_version_file_link['href']
                file_extension = pattern.match(filename).group(1)
                nodejs_version_file_url = urlparse.urljoin(nodejs_version_url, nodejs_version_file_link['href'])
                nodejs_version_data[key][file_extension] = {
                    'filename': filename,
                    'url': nodejs_version_file_url
                }

        return nodejs_version_data

    nodejs_version_urls = map(lambda version: urlparse.urljoin(NODEJS_DISTRIBUTION_URL, 'v' + version + '/'),
                              nodejs_versions)
    nodejs_version_responses = http_multiget(nodejs_version_urls)
    nodejs_version_html = map(lambda response_tuple: response_tuple[1].text, nodejs_version_responses)

    version_data = {}
    for nodejs_version, nodejs_version_url, nodejs_version_html in zip(nodejs_versions, nodejs_version_urls,
                                                                       nodejs_version_html):
        version_data[nodejs_version] = parse_html(nodejs_version_url, nodejs_version_html)
    return version_data


def filter_latest_major_versions(versions, min_ver=None, max_ver=None):
    major_versions = {}

    for version in versions:
        version_info = semver.parse_version_info(version)

        if min_ver is not None and not semver.match(version, min_ver):
            continue

        if max_ver is not None and not semver.match(version, max_ver):
            continue

        major_version = str(version_info.major)
        current_major_version = major_versions.get(major_version)
        if current_major_version is None or semver.compare(version, current_major_version) > 0:
            major_versions[major_version] = version

    return major_versions.values()


def load_file(filename):
    filename = os.path.abspath(filename)
    with open(filename, 'r') as f:
        return f.read()


def load_yaml(filename):
    return yaml.safe_load(load_file(filename))


def write_file(filename, data):
    filename = os.path.abspath(filename)
    file_dir = os.path.dirname(filename)
    mkdirp(file_dir)
    with open(filename, 'w') as f:
        f.write(data)


def write_yaml(filename, data):
    write_file(filename, yaml.safe_dump(data))


def datetime_to_timestamp(date=None):
    if date is None:
        date = datetime.now()
    return int(time.mktime(date.timetuple()))


def timestamp_to_datetime(timestamp):
    if timestamp is None or timestamp == "":
        return None
    return datetime.fromtimestamp(int(timestamp))


def mkdirp(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass


def load_nodejs_data(config, data_file, force_update=False, update_all_versions=False):
    current_datetime = datetime.now()
    current_timestamp = datetime_to_timestamp(current_datetime)

    nodejs_data = {'versions': {}}
    last_updated = None
    nodejs_data_updated = False

    try:
        if os.path.isfile(data_file):
            nodejs_data = load_yaml(data_file)
            last_updated = timestamp_to_datetime(nodejs_data['last_updated'])
    except:
        pass

    update = force_update or last_updated is None or last_updated + timedelta(days=1) <= current_datetime

    if update:
        versions = list_nodejs_versions()
        for version in versions:
            if nodejs_data['versions'].get(version) is None:
                nodejs_data['versions'][version] = {}
        nodejs_data_updated = True
    else:
        versions = nodejs_data['versions'].keys()

    latest_major_versions = filter_latest_major_versions(versions, config.get('min_version'), config.get('max_version'))

    if update_all_versions:
        versions_to_update = versions
    else:
        versions_to_update = [version for version in latest_major_versions if
                              nodejs_data['versions'][version].get('files') is None]

    if versions_to_update:
        nodejs_version_files = list_nodejs_version_files(versions_to_update)
        for version, version_files in nodejs_version_files.iteritems():
            if nodejs_data['versions'][version].get('files') is None:
                nodejs_data['versions'][version]['files'] = {}
            nodejs_data['versions'][version]['files'].update(version_files)
        nodejs_data_updated = True

    if nodejs_data_updated:
        nodejs_data['last_updated'] = datetime_to_timestamp()
        write_yaml(data_file, nodejs_data)

    return nodejs_data, versions_to_update


def render_dockerfiles(config, nodejs_data, versions_to_update, force_update=False):
    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.abspath('templates')))

    for base_repository in config['base_repositories']:
        base_repository_tags = [base_repository_tag['name'] for base_repository_tag in
                                list_docker_hub_image_tags(base_repository) if base_repository_tag['name'] != 'latest']

        base_os = base_repository[base_repository.rfind('/') + 1:]

        dockerfile_template = jinja2_env.select_template(['Dockerfile.' + base_os + '.j2', 'Dockerfile.j2'])
        makefile_template = jinja2_env.select_template(['Makefile.' + base_os + '.j2', 'Makefile.j2'])

        for base_repository_tag in base_repository_tags:
            base_image_name = base_repository + ':' + base_repository_tag
            tag_suffix = base_os + base_repository_tag

            for version in versions_to_update:
                image_tags = [version, version + '-' + tag_suffix]
                dockerfile_context = os.path.join(os.getcwd(), version, tag_suffix)

                dockerfile_path = os.path.join(dockerfile_context, 'Dockerfile')
                makefile_path = os.path.join(dockerfile_context, 'Makefile')

                dockerfile_exists = os.path.exists(dockerfile_path)
                makefile_exists = os.path.exists(makefile_path)

                if force_update or not dockerfile_exists or not makefile_exists:
                    render_data = {
                        'version': version,
                        'repository_name': config['repository_name'],
                        'base_os': base_os,
                        'base_image_name': base_image_name,
                        'tag_suffix': tag_suffix,
                        'dockerfile_context': dockerfile_context,
                        'image_tags': image_tags
                    }

                    render_data.update(nodejs_data['versions'][version])

                    if force_update or not dockerfile_exists:
                        write_file(dockerfile_path, dockerfile_template.render(render_data))
                    if force_update or not makefile_exists:
                        write_file(makefile_path, makefile_template.render(render_data))


def main(argv):
    parser = argparse.ArgumentParser(description='Updates NodeJS data file with version URLs and Dockerfiles.')
    parser.add_argument('--data-file', nargs=1, dest='data_file', default=os.path.abspath('nodejs.yml'))
    parser.add_argument('--config-file', nargs=1, dest='config_file', default=os.path.abspath('config.yml'))
    parser.add_argument('-f', '--force-update', dest='force_update', action='store_true')
    parser.add_argument('-a', '--update-all', dest='update_all', action='store_true')

    parsed_args = vars(parser.parse_args())

    config_file = parsed_args.get('config_file')
    data_file = parsed_args.get('data_file')
    force_update = parsed_args.get('force_update')
    update_all = parsed_args.get('update_all')

    config = load_yaml(config_file)

    nodejs_data, versions_to_update = load_nodejs_data(config, data_file, force_update, update_all)
    render_dockerfiles(config, nodejs_data, versions_to_update, force_update)


if __name__ == '__main__':
    main(sys.argv)
