#!/usr/bin/env python2

import sys

from pydash import set_ as _set, flatten as _flatten

from util import *


class NodeJsScraper:
    def __init__(self, config):
        self.distribution_url = config['distribution_url']
        self.version_url_pattern = re.compile(config['version_url_pattern'])
        self.pattern_tree = PatternTree(config['file_patterns'])

    def list_version_urls(self):
        distribution_html = http_get(self.distribution_url).text
        parsed_urls = parse_html_for_urls(distribution_html, self.distribution_url)
        version_urls = {}
        for parsed_url in parsed_urls:
            match = self.version_url_pattern.search(parsed_url)
            if match is not None:
                version = match.group(1)
                version_urls[version] = parsed_url
        return version_urls

    def list_version_files(self, version, return_unmatched_urls=False):
        if not isinstance(version, list):
            versions = [version]
        else:
            versions = version

        urls_to_parse = [urlparse.urljoin(self.distribution_url, 'v' + version + '/') for version in versions]

        responses = http_multiget(urls_to_parse)

        parsed_urls = _flatten([parse_html_for_urls(response.text, url) for (url, response) in responses])

        version_files = {}
        unmatched_urls = []

        for parsed_url in parsed_urls:

            pattern_match = self.pattern_tree.search(parsed_url)

            if pattern_match is not None:
                match, path = pattern_match
                file_type = path[0]

                if file_type == 'binaries':
                    url_version = match.group(1)
                    filename = match.group(2)
                    system = match.group(3)
                    extension = match.group(4)
                    _set(version_files, [url_version, file_type, system, extension], {
                        'filename': filename,
                        'url': parsed_url
                    })
                else:
                    url_version = match.group(1)
                    filename = match.group(2)
                    extension = match.group(3)
                    _set(version_files, [url_version, file_type,  extension], {
                        'filename': filename,
                        'url': parsed_url
                    })

            else:
                unmatched_urls.append(parsed_url)
        if return_unmatched_urls:
            version_files['unmatched_urls'] = unmatched_urls
        return version_files


def main(argv):
    config = load_yaml('config.yml')
    scraper = NodeJsScraper(config)
    versions = scraper.list_version_urls()
    print_yaml(versions)
    filtered_versions = filter_versions(versions.keys(), config.get('version_constraints'))
    print_yaml(filtered_versions)
    files = scraper.list_version_files(filtered_versions)
    print_yaml(files)


if __name__ == '__main__':
    main(sys.argv)
