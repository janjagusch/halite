"""
This package defines helpful code for the rest of the project.
"""

from collections import ChainMap

from .representation_mixin import RepresentationMixin
from .logger import setup_logger


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
