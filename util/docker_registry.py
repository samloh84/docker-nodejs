from pprint import pprint
import requests


def login_to_dockerhub(repository, username=None, password=None):
    url = "https://auth.docker.io/token"
    params = {
        'service': 'registry.docker.io',
        'scope': 'repository:' + repository + ':pull,push'
    }
    auth = None
    if username is not None and password is not None:
        auth = requests.auth.HTTPBasicAuth(username, password)
    response = requests.get(url, params=params, auth=auth)
    pprint(response.text)
    data = response.json()
    return data['token']


def list_repository_tags(repository,
                         username=None,
                         password=None,
                         token=None,
                         registry=None,
                         verify=None):
    if registry is None:
        registry = 'index.docker.io'

    url = "https://" + registry + "/v2/" + repository + "/tags/list"
    response = requests.get(url, verify=verify)
    if response.status_code == 401:
        if registry == 'index.docker.io':
            if token is None:
                token = login_to_dockerhub(repository, username, password)
            headers = {'Authorization': 'Bearer ' + token}
            response = requests.get(url, headers=headers, verify=verify)
        else:
            auth = requests.auth.HTTPBasicAuth(username, password)
            response = requests.get(url, auth=auth, verify=verify)

    pprint(response.text)
    data = response.json()
    pprint(data)

    return data['tags']


def group_tags(tags):
    tag_groups = []
    for tag in tags:
        append = True
        for tag_group in tag_groups:
            for tag_group_tag in tag_group:
                if tag.startswith(tag_group_tag) or tag_group_tag.startswith(tag):
                    append = False
                    tag_group.append(tag)
                    break
        if append:
            tag_groups.append([tag])
    for tag_group in tag_groups:
        tag_group.sort(lambda x, y: -cmp(len(x), len(y)))
    return tag_groups
