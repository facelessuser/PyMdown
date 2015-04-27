import yaml
from collections import OrderedDict

__all__ = ["reduce_list", "yaml_load"]


def yaml_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """
    Make all YAML dictionaries load as ordered Dicts.
    http://stackoverflow.com/a/21912744/3609487
    """
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping
    )

    return yaml.load(stream, OrderedLoader)


def reduce_list(data_set):
    """ Reduce duplicate items in a list and preserve order """
    seen = set()
    return [item for item in data_set if item not in seen and not seen.add(item)]


if __name__ == "__main__":
    text = '''
test:
    key1: 1
    key2: 2
    key3: 3
    key4: 4
    key5: 5
    key5: 6
    key3: 7
'''

    obj = yaml_load(text)

    print('Dict is ordered')
    print(obj)
    print('List is reduced with order')
    print(reduce_list([1, 2, 3, 4, 5, 5, 2, 4, 6, 7, 8]))
