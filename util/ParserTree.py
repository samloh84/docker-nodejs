import re
import pydash


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
                    pydash.set_(self.pattern_tree, path + [key], re.compile(value))

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
