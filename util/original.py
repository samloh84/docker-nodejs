import errno
import re
import urlparse

import grequests
import os
import requests
import semver
import yaml
from bs4 import BeautifulSoup
from pydash import get as _get, set_ as _set, flatten as _flatten
from pydash.collections import some as _some, every as _every, flat_map_deep as _flat_map_deep, \
    flat_map_depth as _flat_map_depth
