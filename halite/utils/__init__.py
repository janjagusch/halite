"""
This package defines helpful code for the rest of the project.
"""

from collections import ChainMap
import re

from .mixins import RepresentationMixin, DataClassYamlMixin


def merge_dicts(dicts):
    """
    Merges lsit of dicts into one big dict.

    Args:
        dicts (list[dict]): List of dicts.

    Returns:
        dict: One big dict.
    """
    return dict(ChainMap(*dicts))


def merge_lists(lists):
    """
    Merges list of lists into one big list.

    Args:
        lists (list[list]): List of lists.

    Returns:
        list: One big list.
    """
    return [item for l in lists for item in l]


def camel_to_snake(term: str) -> str:
    """
    Converts a CamedCased term into a snake_cased term.
    """
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    return pattern.sub("_", term).lower()


def snake_to_camel(term: str) -> str:
    """
    Converts a snake_cased term into a CamelCased term.
    """
    components = term.split("_")
    return components[0] + "".join(word.title() for word in components[1:])
