from __future__ import annotations
from abc import ABCMeta
from itertools import chain
from typing import TYPE_CHECKING, Any, Iterable

from slots_class._base_info import get_classvar, resolve_bases
from slots_class._metadata import MetaData
from slots_class.exceptions import SlotsClassCreationError, SlotsClassMixinError
from slots_class.descriptor import (
    UNSET,
    ClassvarWrapper,
    SlotClassDescriptor,
    is_data_descriptor,
)
from slots_class._annotations import annotations_from_ns
from slots_class.py_descriptor import NullDescriptor

NO_SLOTS = {
    "_slot_info_",
    "__classcell__",
    "__abstractmethods__",
    "__class__",
    "__delattr__",
    "__dir__",
    "__doc__",
    "__eq__",
    "__format__",
    "__ge__",
    "__getattribute__",
    "__getstate__",
    "__gt__",
    "__hash__",
    "__init__",
    "__init_subclass__",
    "__le__",
    "__lt__",
    "__module__",
    "__ne__",
    "__new__",
    "__reduce__",
    "__reduce_ex__",
    "__repr__",
    "__setattr__",
    "__sizeof__",
    "__slots__",
    "__str__",
    "__subclasshook__",
}
IGNORE_CLASSVARS = NO_SLOTS | {
    "__dict__",
    "__weakref__",
}


class SlotsClassMeta(ABCMeta):
    _slot_info_: MetaData
    __slots__: tuple[str, ...]

    def __new__(
        meta,  # pyright: ignore[reportSelfClsParameterName]
        name: str,
        bases: tuple[type, ...],
        ns: dict[str, Any],
        *,
        is_mixin: bool | None = None,
    ) -> SlotsClassMeta:

        # get info about base classes
        base_info = resolve_bases(bases)

        if "__slots__" in ns:
            raise SlotsClassCreationError(
                "__slots__ should be determined automatically"
            )

        # resolve candidates for slots
        explicit_slots = annotations_from_ns(ns)
        maybe_slots: tuple[str, ...] = (
            *base_info.mixin_slots,
            *explicit_slots,
            *ns["__static_attributes__"],
        )

        # determine what slots should be added to the current class
        slots = list[str]()
        classvar_descriptors = dict[str, Any]()
        data_descriptors = set[str]()
        for candidate in dict.fromkeys(maybe_slots):
            if candidate in NO_SLOTS:
                continue

            # if the slot is inherited from the base class.
            if candidate in base_info.slots:
                # block access to private attributes on base classes
                if (
                    candidate.startswith("_")
                    and not candidate.endswith("_")
                    and candidate not in explicit_slots
                ):
                    raise SlotsClassCreationError(
                        f"Private attr '{candidate}' belongs to a base class. To force access, declare the slot explicitly in the class body."
                    )

                continue

            cls_var = get_classvar(candidate, ns, base_info)

            # don't create the slot if it is a data descriptor.
            if is_data_descriptor(cls_var):
                data_descriptors.add(candidate)
                continue

            # non-data descriptor
            if cls_var is not UNSET:
                ns.pop(candidate, None)
                classvar_descriptors[candidate] = cls_var

            slots.append(candidate)

        # resolve abstract methods
        abstract_attrs = set(base_info.abstract_attrs)
        for name, classvar in ns.items():
            if getattr(classvar, "__abstractmethod__", False):
                abstract_attrs |= {name}
            else:
                abstract_attrs -= {name}

        # abstract classes must also be mixins
        if is_abstract := bool(abstract_attrs):
            if is_mixin is False:
                raise SlotsClassCreationError(
                    "Abstract classes must also be mixin classes."
                )
            is_mixin = True
        elif is_mixin is None:
            is_mixin = False

        if not is_mixin:
            ns["__slots__"] = slots

        ns["_slot_info_"] = MetaData(
            slots=(*slots, *base_info.slots),
            data_descriptors=frozenset(data_descriptors),
            is_mixin=is_mixin,
            is_abstract=is_abstract,
            abstract_attrs=frozenset(abstract_attrs),
        )

        cls = type.__new__(meta, name, bases, ns)

        for name, classvar in classvar_descriptors.items():
            if not isinstance(classvar, SlotClassDescriptor):
                classvar = ClassvarWrapper(classvar)
            classvar._set_metadata_(cls, name, getattr(cls, name, NullDescriptor()))
            type.__setattr__(cls, name, classvar)

        return cls

    def __setattr__(cls, name: str, value: Any) -> None:
        if (old := cls.__dict__.get(name, UNSET)) is UNSET:
            return super().__setattr__(name, value)
        if isinstance(old, SlotClassDescriptor):
            old._cls_set_(cls, value)

    if __debug__:
        if not TYPE_CHECKING:

            def __call__(cls, *args, **kwds):
                if cls._slot_info_.is_mixin:
                    raise SlotsClassMixinError("Mixin classes cannot have instances.")
                return super().__call__(*args, **kwds)
