from __future__ import annotations
from abc import ABCMeta
from typing import Any, Iterable

from slots_class.descriptor import (
    UNSET,
    ClassvarWrapper,
    SlotClassDataDescriptor,
    SlotClassDescriptor,
    is_data_descriptor,
)
from slots_class._annotations import annotations_from_ns

NO_SLOTS = {
    "_descriptors_",
    "_fields_",
    "_all_slots_",
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


class SlotsClassCreationError(TypeError):
    pass


class SlotsClassMeta(ABCMeta):
    _descriptors_: tuple[str]
    # _class_vars_: tuple[str]
    _all_slots_: tuple[str]
    __slots__: tuple[str, ...] = ()

    def __new__(
        meta,  # pyright: ignore[reportSelfClsParameterName]
        name: str,
        bases: tuple[type, ...],
        ns: dict[str, Any],
    ) -> SlotsClassMeta:

        # resolve candidates for slots
        if "__slots__" in ns:
            raise SlotsClassCreationError(
                "__slots__ should be determined automatically"
            )
        maybe_slots: tuple[str, ...] = (
            *annotations_from_ns(ns),
            *ns["__static_attributes__"],
        )

        # get info about base classes
        base_data_descriptors = set[str]()
        base_slots = set[str]()

        for base in bases:
            if not isinstance(base, SlotsClassMeta):
                raise SlotsClassCreationError("Must inherit from another SlotsObj")
            base_data_descriptors.update(base._descriptors_)
            base_slots.update(base._all_slots_)

        # search for data descriptors (which must not become slots)
        data_descriptors = set[str]()
        for name, value in ns.items():
            if name in IGNORE_CLASSVARS:
                continue
            if is_data_descriptor(value):
                data_descriptors.add(name)

        # determine what slots should be added to the current class
        slots = tuple[str, ...]()
        classvars = dict[str, Any]()
        for candidate in dict.fromkeys(maybe_slots):
            if candidate in NO_SLOTS:
                continue

            if candidate in base_data_descriptors or candidate in base_slots:
                # block access to private attributes on base classes
                if candidate.startswith("_") and not candidate.endswith("_"):
                    raise SlotsClassCreationError(
                        f"Private attr '{candidate}' belongs to a base class. To force access, declare the name in __slots__"
                    )

                continue
            if candidate in data_descriptors:
                continue
            slots += (candidate,)

            for base in bases:
                for parent in base.mro():
                    if (val := parent.__dict__.get(candidate, UNSET)) is not UNSET:
                        classvars[candidate] = val
                        break

        ns["_descriptors_"] = tuple(data_descriptors | base_data_descriptors)
        ns["_all_slots_"] = (*slots, *base_slots)
        ns["__slots__"] = slots

        cls = type.__new__(meta, name, bases, ns)

        for name, classvar in classvars.items():
            if not isinstance(classvar, SlotClassDescriptor):
                classvar = ClassvarWrapper(classvar)
            classvar._set_metadata_(cls, name, cls.__dict__[name])
            type.__setattr__(cls, name, classvar)

        return cls

    def __setattr__(cls, name: str, value: Any) -> None:
        if (old := cls.__dict__.get(name, UNSET)) is UNSET:
            return super().__setattr__(name, value)
        if isinstance(old, SlotClassDescriptor):
            old._cls_set_(cls, value)
