from __future__ import annotations
from abc import ABCMeta
from collections.abc import Iterable, Set
from itertools import chain
from typing import TYPE_CHECKING, Any, NamedTuple, is_protocol, get_protocol_members

from slots_class.descriptor import UNSET
from slots_class.exceptions import SlotsClassCreationError

import slots_class.slots_class_meta as scm


def _iter_slots(cls: type):
    for base in cls.mro():
        if base is object:
            continue
        yield from getattr(base, "__slots__", ("__dict__", "__weakref__"))


def get_classvar(name: str, ns: dict[str, Any], base_info: BaseInfo, default=UNSET):
    for space in chain((ns,), (b.__dict__ for b in base_info.all_bases)):
        if name in space:
            return name
    return default


class BaseInfo(NamedTuple):
    base: type
    mixins: list[type]
    all_bases: list[type]
    abstract_attrs: set[str]
    mixin_slots: list[str]

    @property
    def slots(self) -> tuple[str, ...]:
        if isinstance(self.base, scm.SlotsClassMeta):
            return self.base._slot_info_.slots
        return tuple(_iter_slots(self.base))


def _get_abstract(cls: type) -> Iterable[str] | None:

    if isinstance(cls, scm.SlotsClassMeta):
        if (attrs := cls._slot_info_.abstract_attrs) or cls._slot_info_.is_mixin:
            return attrs
        return None
    if isinstance(cls, ABCMeta):
        if attrs := cls.__abstractmethods__:
            return attrs
    return None


def resolve_bases(bases: Iterable[type]) -> BaseInfo:
    """Finds one "true" base class, the rest are mixins, protocols"""
    concrete_base = object
    mixins = list[type]()
    mixin_slots = list[str]()
    abstract_attrs = set[str]()
    _to_remove = list[type]()
    for base in bases:
        if is_protocol(base):
            abstract_attrs.update(get_protocol_members(base))
            _to_remove.append(base)
            continue

        _abstracts = _get_abstract(base)
        if _abstracts is not None:
            abstract_attrs.update(_abstracts)
            mixins.append(base)
            continue

        elif concrete_base is object:
            concrete_base = base
            continue

        else:
            raise SlotsClassCreationError(
                f"Slots Classes can only inherit from 1 concrete, non-mixin class. {base!r} and {concrete_base!r} are both concrete."
            )

    for mixin in mixins:
        if isinstance(mixin, scm.SlotsClassMeta):
            mixin_slots.extend(mixin._slot_info_.slots)

    return BaseInfo(
        base=concrete_base,
        mixins=mixins,
        all_bases=[b for b in bases if b not in _to_remove],
        abstract_attrs=abstract_attrs,
        mixin_slots=list(dict.fromkeys(mixin_slots)),
    )
