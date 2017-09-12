#!/usr/bin/env python2

import sys

import pydash
from util import *


class NodeJsScraper:
    def __init__(self, config):
        self.starting_url = config['starting_url']

        scraper_url_patterns = config['scraper_url_patterns']
        if scraper_url_patterns is not None and not isinstance(scraper_url_patterns, list):
            scraper_url_patterns = [scraper_url_patterns]
        self.scraper_url_patterns = [re.compile(pattern) for pattern in scraper_url_patterns]
        self.depth = config.get('scraper_depth')

        version_url_patterns = config['version_url_patterns']
        if not isinstance(version_url_patterns, list):
            version_url_patterns = [version_url_patterns]
        self.version_url_patterns = [re.compile(pattern) for pattern in version_url_patterns]

        self.pattern_tree = PatternTree(config['file_patterns'])

    def list_version_urls(self):
        responses = deep_scrape(self.starting_url, url_patterns=self.scraper_url_patterns)
        parse_lambda = lambda (_, response): parse_response_for_urls(response, regex_filters=self.scraper_url_patterns)
        parsed_urls = map(parse_lambda, responses)
        parsed_urls = pydash.flatten(parsed_urls)
        version_urls = {}
        for parsed_url in parsed_urls:
            for version_url_pattern in self.version_url_patterns:
                match = version_url_pattern.search(parsed_url)
                if match is not None:
                    version = match.group(1)
                    version_urls[version] = parsed_url
                    break
        return version_urls

    def list_version_files(self, version, return_unmatched_urls=False):
        if not isinstance(version, list):
            versions = [version]
        else:
            versions = version

        urls_to_parse = []

        for version in versions:
            version_url = urlparse.urljoin(self.starting_url, 'v' + version + '/')
            urls_to_parse.append(version_url)

        responses = http_multiget(urls_to_parse)

        parsed_urls = pydash.flatten([parse_response_for_urls(response) for (_, response) in responses])

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
                    pydash.set_(version_files, [url_version, file_type, system, extension], {
                        'filename': filename,
                        'url': parsed_url
                    })
                else:
                    url_version = match.group(1)
                    filename = match.group(2)
                    extension = match.group(3)
                    pydash.set_(version_files, [url_version, file_type, extension], {
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
    filtered_versions = filter_latest_versions(versions.keys(), version_constraints=config.get('version_constraints'))
    print_yaml(filtered_versions)
    files = scraper.list_version_files(filtered_versions)
    print_yaml(files)


if __name__ == '__main__':
    main(sys.argv)
