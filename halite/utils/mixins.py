"""
This module defines a default representation mixin.
"""
from abc import ABC

from dataclasses_json import DataClassJsonMixin
import yaml


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


class DataClassYamlMixin(DataClassJsonMixin, ABC):
    @staticmethod
    def _read_yaml(file_path):
        with open(file_path, mode="r") as file_pointer:
            return yaml.full_load(file_pointer)

    @staticmethod
    def _write_yaml(obj, file_path):
        with open(file_path, mode="w") as file_pointer:
            yaml.dump(obj, file_pointer)

    @classmethod
    def from_yaml(cls, file_path):
        return cls.from_dict(cls._read_yaml(file_path))

    def to_yaml(self, file_path):
        self._write_yaml(self.to_dict(), file_path)
