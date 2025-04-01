from typing import NamedTuple


class MetaData(NamedTuple):
    slots: tuple[str, ...]
    data_descriptors: frozenset[str]
    abstract_attrs: frozenset[str]
    is_mixin: bool
    is_abstract: bool
