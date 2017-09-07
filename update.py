#!/usr/bin/env python2
import argparse
import sys
from pprint import pprint

from jinja2 import Environment, FileSystemLoader
from pydash import get as _get, set_ as _set
from pydash.objects import merge as _merge

from scraper import *

from util import *


def update_nodejs_data(data, config, update_all_versions=False):
    scraper = NodeJsScraper(config)
    versions = scraper.list_version_urls().keys()

    if update_all_versions:
        versions_to_update = versions
    else:
        versions_to_update = filter_versions(versions, config.get('version_constraints'))

    _merge(data, {'versions': scraper.list_version_files(versions)}, {'last_updated': datetime_to_timestamp()})
    return data


def render_nodejs_dockerfiles(data, config, update_all_versions=False, force_update=False):
    env = Environment(loader=FileSystemLoader(os.path.abspath('templates')))
    repository_name = config['repository_name']
    base_repositories = config['base_repositories']
    template_files = config['templates']

    versions = data['versions'].keys()

    if update_all_versions:
        versions_to_update = versions
    else:
        versions_to_update = filter_versions(versions, config.get('version_constraints'))

    for version in versions_to_update:
        version_files = data['versions'][version]

        for base_repository in base_repositories:
            base_repository_name = base_repository[base_repository.rfind('/') + 1:]
            base_repository_tags = [tag['name'] for tag in list_docker_hub_image_tags(base_repository) if
                                    tag['name'] != 'latest']

            for base_repository_tag in base_repository_tags:
                base_image_name = base_repository + ':' + base_repository_tag

                dockerfile_context = os.path.join(os.getcwd(), version, base_repository_name + base_repository_tag)

                tags = [version, version + '-' + base_repository_name + base_repository_tag]
                version_info = semver.parse_version_info(version)

                base_os = re.compile('centos|alpine|ubuntu|debian|fedora|rhel').search(
                    base_repository_name + base_repository_tag).group(0)

                render_data = {
                    'version': version,
                    'version_info': version_info,
                    'files': version_files,
                    'base_repository_name': base_repository_name,
                    'base_image_name': base_image_name,
                    'base_os': base_os,
                    'config': config,
                    'repository_name': repository_name,
                    'tags': tags
                }

                for template_file in template_files:
                    template_filenames = [
                        template_file + '.' + base_repository_name + base_repository_tag + '.' + '.j2',
                        template_file + '.' + base_repository_name + '.j2',
                        template_file + '.j2'
                    ]

                    template = env.select_template(template_filenames)

                    template_render_path = os.path.join(dockerfile_context, template_file)
                    if not os.path.exists(template_render_path) or force_update:
                        write_file(template_render_path, template.render(render_data))
                        print 'Rendered template: ' + template_render_path


def main(argv):
    parser = argparse.ArgumentParser(description='Updates data file with urls and renders Dockerfiles.')
    parser.add_argument('--data-file', nargs='?', dest='data_file', default=os.path.abspath('nodejs.yml'))
    parser.add_argument('--config-file', nargs='?', dest='config_file', default=os.path.abspath('config.yml'))
    parser.add_argument('-f', '--force-update', dest='force_update', action='store_true')
    parser.add_argument('-a', '--update-all', dest='update_all', action='store_true')

    parsed_args = vars(parser.parse_args())

    config_file = parsed_args.get('config_file')
    data_file = parsed_args.get('data_file')
    force_update = parsed_args.get('force_update')
    update_all = parsed_args.get('update_all')

    config = load_yaml(config_file)

    saved_data = load_data_file(data_file)
    if saved_data is not None:
        data, _, update = saved_data
        perform_update = update or force_update
    else:
        data = {'versions': {}}
        perform_update = True

    if perform_update:
        data = update_nodejs_data(data, config, update_all)
        write_yaml(data_file, data)

    render_nodejs_dockerfiles(data, config, update_all, force_update)


if __name__ == '__main__':
    main(sys.argv)
