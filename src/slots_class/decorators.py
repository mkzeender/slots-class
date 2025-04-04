from __future__ import annotations
from collections.abc import Callable
from typing import Any, Self
from slots_class.descriptor import SlotDescriptor


class CachedProperty[T, O=Any](SlotDescriptor[T, SlotDescriptor, O]):
    __slots__ = ('_get',)
    
    def __init__(self, getter: Callable[[O], T]) -> None:
        super().__init__()
        self._get = getter

    def _inst_get_(self, inst: O) -> T:
        try:
            return super()._inst_get_(inst)
        except AttributeError:
            val = self._get(inst)
            self._inst_set_(inst, val)
            return val
    