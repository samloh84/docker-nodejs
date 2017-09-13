import re

docker_image_alphanumeric_pattern = re.compile('[a-z0-9]+')
docker_image_separator_pattern = re.compile('(?:[._]|__|[-]*)')
docker_image_name_component_pattern = re.compile(
    '%(alphanumeric_pattern)s(?:(?:%(separator_pattern)s%(alphanumeric_pattern)s)+)?'
    % {'alphanumeric_pattern': docker_image_alphanumeric_pattern.pattern,
       'separator_pattern': docker_image_separator_pattern.pattern})

docker_image_hostname_component_pattern = re.compile('(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])')
docker_image_hostname_pattern = re.compile(
    '%(hostname_component_pattern)s(?:(?:\.%(hostname_component_pattern)s)+)(?::[0-9]+)?'
    % {'hostname_component_pattern': docker_image_hostname_component_pattern.pattern})

docker_image_anchored_hostname_pattern = re.compile(
    '^(%(hostname_component_pattern)s(?:(?:\.%(hostname_component_pattern)s)+))(?::([0-9]+))?$'
    % {'hostname_component_pattern': docker_image_hostname_component_pattern.pattern})

docker_image_tag_pattern = re.compile('[\w][\w.-]{0,127}')

docker_image_anchored_tag_pattern = re.compile('^%(tag_pattern)s$' % {'tag_pattern': docker_image_tag_pattern.pattern})

docker_image_digest_pattern = re.compile('[A-Za-z][A-Za-z0-9]*(?:[-_+.][A-Za-z][A-Za-z0-9]*)*[:][0-9A-Fa-f]{32,}')

docker_image_anchored_digest_pattern = re.compile(
    '^%(digest_pattern)s$' % {'digest_pattern': docker_image_digest_pattern.pattern})

docker_image_name_pattern = re.compile(
    '(?:%(hostname_pattern)s/)?%(name_component_pattern)s(?:(?:/%(name_component_pattern)s)+)?' %
    {
        'hostname_pattern': docker_image_hostname_pattern.pattern,
        'name_component_pattern': docker_image_name_component_pattern.pattern
    })

docker_image_anchored_name_pattern = re.compile(
    '^(?:(%(hostname_pattern)s)/)?(%(name_component_pattern)s(?:(?:/%(name_component_pattern)s)+)?)$' %
    {
        'hostname_pattern': docker_image_hostname_pattern.pattern,
        'name_component_pattern': docker_image_name_component_pattern.pattern
    })

docker_image_reference_pattern = re.compile(
    '^(%(name_pattern)s)(?::(%(tag_pattern)s))?(?:@(%(digest_pattern)s))?$' %
    {
        'name_pattern': docker_image_name_pattern.pattern,
        'tag_pattern': docker_image_tag_pattern.pattern,
        'digest_pattern': docker_image_digest_pattern.pattern
    })


def parse_image_name(image_name):
    full_repo = None
    repo = None
    tag = None
    digest = None
    registry = None

    match = docker_image_reference_pattern.match(image_name)
    if match is not None:
        full_repo = match.group(1)
        tag = match.group(2)
        digest = match.group(3)

    if full_repo is not None:
        match = docker_image_anchored_name_pattern.match(full_repo)
        if match is not None:
            registry = match.group(1)
            repo = match.group(2)
        else:
            repo = full_repo

    return {'full_repo': full_repo, 'tag': tag, 'digest': digest, 'registry': registry, 'repo': repo}
