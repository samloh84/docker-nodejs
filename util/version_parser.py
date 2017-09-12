import re

import pydash
import semver


def parse_versions(versions, normalize_version=None):
    def parse_lambda(version):
        if normalize_version is not None:
            normalized_version = normalize_version(version)
        else:
            normalized_version = version

        version_info = semver.parse_version_info(normalized_version)
        return version, normalized_version, version_info

    versions = map(parse_lambda, versions)

    return versions


def filter_versions(versions, version_constraints, normalize_version=None, return_version_info=False):
    def match_version_constraints(versions_element):
        def match_version_constraint(version_constraint):
            return semver.match(normalized_version, version_constraint)

        version, normalized_version, version_info = versions_element
        return all(map(match_version_constraint, version_constraints))

    if not isinstance(version_constraints, list):
        version_constraints = [version_constraints]

    versions = parse_versions(versions, normalize_version=normalize_version)
    filtered_versions = filter(match_version_constraints, versions)

    if not return_version_info:
        filtered_versions = map(lambda filtered_version: filtered_version[0], filtered_versions)

    return filtered_versions


def filter_latest_versions(versions,
                           version_constraints=None,
                           sort_criteria=None,
                           normalize_version=None,
                           return_version_info=False):
    if sort_criteria is None:
        sort_criteria = ['major']

    if version_constraints is not None:
        if not isinstance(version_constraints, list):
            version_constraints = [version_constraints]

    if version_constraints is not None:
        versions = filter_versions(versions, version_constraints,
                                   normalize_version=normalize_version,
                                   return_version_info=True)
    else:
        versions = parse_versions(versions,
                                  normalize_version=normalize_version)

    latest_versions = {}

    for version_element in versions:
        normalized_version = version_element[1]
        version_info = version_element[2]
        path = map(lambda criteria: str(getattr(version_info, criteria)), sort_criteria)

        latest_version_element = pydash.get(latest_versions, path)

        if latest_version_element is None:
            pydash.set_(latest_versions, path, version_element)
        else:
            latest_normalized_version = latest_version_element[1]
            if semver.compare(normalized_version, latest_normalized_version) > 0:
                pydash.set_(latest_versions, path, version_element)

    latest_versions = pydash.collections.flat_map_depth(latest_versions, depth=len(sort_criteria) - 1)

    if not return_version_info:
        latest_versions = map(lambda latest_version: latest_version[0], latest_versions)

    return latest_versions


def get_latest_version(versions, version_constraints=None,
                       latest_version_constraint=None,
                       sort_criteria=None,
                       normalize_version=None,
                       return_version_info=False):
    latest_versions = filter_latest_versions(versions,
                                             version_constraints=version_constraints,
                                             sort_criteria=sort_criteria,
                                             normalize_version=normalize_version,
                                             return_version_info=True)

    latest_version = max(latest_versions, key=lambda latest_version_info: latest_version_info[2])

    if not return_version_info:
        latest_version = latest_version[0]

    return latest_version


def normalize_version_to_semver(version):
    return version
