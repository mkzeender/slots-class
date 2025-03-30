from __future__ import annotations

from typing import Any, Never, Protocol, TypeIs


class PyDescriptor[PropType, ObjectType = Any](Protocol):
    __name__: str
    def __get__(self, obj: ObjectType | None, objtype: type[ObjectType], /) -> PropType: ...


class PyDataDescriptor[PropType, ObjectType = Any](PyDescriptor[PropType], Protocol):
    def __set__(self, obj: ObjectType, value: PropType, /) -> None: ...
    def __delete__(self, obj: ObjectType, /) -> None: ...


def is_py_descriptor(obj: object) -> TypeIs[PyDescriptor]:
    return hasattr(type(obj), "__get__")


def is_py_data_descriptor(obj: object) -> TypeIs[PyDataDescriptor]:
    tp = type(obj)
    return hasattr(tp, "__set__") or hasattr(tp, "__delete__")


def _raise_error(desc: PyDescriptor|type, obj, setter:bool) -> Never:
        object_name = (
            f"class '{obj!r}'"
            if isinstance(obj, type) else
            f"'{type(obj)!r}' object"

        )
        raise AttributeError(
            (
                f'Cannot set attribute "{desc.__name__}" on {object_name}.'
                if setter else
                f'Cannot access attribute "{desc.__name__}" on {object_name}'
            ),
            name=desc.__name__,
            obj=obj
        )


class NullDescriptor:
    __slots__ = ('__name__',)
    def __set_name__(self, owner:type, name:str):
        self.__name__ = name
    def __get__(self, obj, objtype) -> Never:
        if obj is None:
            _raise_error(self, objtype, False)
        _raise_error(self, obj, False)
    def __set__(self, obj, value) -> Never:
        _raise_error(self, obj, True)