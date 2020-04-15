"""
This module defines a default representation mixin.
"""
from abc import ABC


class RepresentationMixin(ABC):
    """
    An abstract class that defines a default representation.
    """

    @property
    def _repr_attrs(self):
        return {
            key: value for key, value in vars(self).items() if not key.startswith("_")
        }

    def __repr__(self):
        joined_attrs = ", ".join(
            [f"{key}={value}" for key, value in self._repr_attrs.items()]
        )
        return f"{self.__class__.__name__}" f"({joined_attrs})"
