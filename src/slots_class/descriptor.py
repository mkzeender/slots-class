from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, TypeIs, final, overload

from slots_class.py_descriptor import PyDataDescriptor, _raise_error, is_py_data_descriptor, is_py_descriptor


class UnsetType(Enum):
    UNSET = object()
    def __repr__(self):
        return f'{__name__}.UNSET'
UNSET = UnsetType.UNSET

def _null(*args, **kwargs) -> None: pass

def is_data_descriptor(obj:Any) -> TypeIs[PyDataDescriptor|SlotClassDataDescriptor]:
    if isinstance(obj, SlotClassDataDescriptor):
        return True
    if isinstance(obj, SlotClassDescriptor):
        return False
    return is_py_data_descriptor(obj)

class SlotClassDescriptor[ValueType, ClassvarType, ObjectType = Any]:
    __slots__ = ('__name__', '__qualname__', '_slot_viewer_')
    __name__: str
    __qualname__: str

    
    def _cls_set_(self, cls: type[ObjectType], value: ClassvarType, /) -> None:
        _raise_error(self, cls, True)

    def _cls_get_(self, cls: type[ObjectType], /) -> ClassvarType:
        _raise_error(self, cls, False)
    
    def _inst_set_(self, inst: ObjectType, value: ValueType, /) -> None:
        self._slot_viewer_.__set__(inst, value)

    def _inst_get_(self, inst: ObjectType, /) -> ValueType:
        return self._slot_viewer_.__get__(inst, type(inst))

    def _inst_del_(self, inst: ObjectType, /) -> None:
        self._slot_viewer_.__delete__(inst)

    def _set_metadata_(self, owner: ObjectType, name: str, slot_viewer: PyDataDescriptor[ValueType, ObjectType]) -> None:
        self.__name__ = name
        if hasattr(owner, '__qualname__'):
            self.__qualname__ = owner.__qualname__ + '.' + name
        else:
            self.__qualname__ = self.__name__
        getattr(slot_viewer, '__set_name__', _null)(owner, name)
        self._slot_viewer_: PyDataDescriptor = slot_viewer

    @overload
    def __get__(self, inst: ObjectType, objtype: type[ObjectType]|None=None, /) -> ValueType: ...
    @overload
    def __get__(self, inst: None, objtype:type[ObjectType], /) -> ClassvarType: ...
    @final
    def __get__(self, inst, objtype=None):
        if inst is None:
            return self._cls_get_(objtype) # type: ignore
        return self._inst_get_(inst)

    @final
    def __set__(self, inst: ObjectType, value: ValueType) -> None:
        self._inst_set_(inst, value)

    @final
    def __delete__(self, inst: ObjectType) -> None:
        self._inst_del_(inst)


class SlotClassDataDescriptor[ValueType, ObjectType=Any](SlotClassDescriptor[ValueType, ObjectType]):
    pass


class ClassvarWrapper[T, O = Any](SlotClassDescriptor[T, T, O]):

    def __init__(self, classvar: T):
        self.value = classvar
        self.is_descriptor = is_py_descriptor(classvar)

    def _inst_get_(self, inst: O) -> T:
        try:
            return super()._inst_get_(inst)
        except AttributeError:
            return self._cls_get_(type(inst), inst)

    def _cls_get_(self, cls: type[O], inst=None) -> T:
        if self.is_descriptor:
            return self.value.__get__(inst, cls) # type: ignore
        return self.value


    def _cls_set_(self, objtype: type, value: T):
        self.value = value
        self.is_descriptor = is_py_descriptor(value)


