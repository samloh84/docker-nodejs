import urlparse

import grequests
import pydash
import requests
from bs4 import BeautifulSoup


def http_get(url, headers=None, auth=None, verify=None):
    return requests.get(url, headers=headers)


def http_multiget(urls, headers=None):
    return zip(urls, grequests.map([grequests.get(url, headers=headers) for url in urls]))


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


def parse_response_for_urls(response, regex_filters=None):
    if isinstance(response, list):
        return map(lambda r: parse_response_for_urls(r, regex_filters), response)
    return parse_html_for_urls(response.text, response.url, regex_filters)


def deep_scrape(starting_urls, depth=-1, url_patterns=None):
    if not isinstance(starting_urls, list):
        starting_urls = [starting_urls]

    if url_patterns is not None and not isinstance(url_patterns, list):
        url_patterns = [url_patterns]

    responses = []

    urls_to_parse = starting_urls

    while len(urls_to_parse) > 0 and depth != 0:
        curr_responses = http_multiget(urls_to_parse)
        responses += curr_responses
        parsed_urls = [url for (url, _) in responses]
        urls_to_parse = map(lambda (_, response): parse_response_for_urls(response, url_patterns), responses)
        urls_to_parse = pydash.flatten(urls_to_parse)
        urls_to_parse = [url for url in urls_to_parse if url not in parsed_urls]
        depth -= 1

    return responses
