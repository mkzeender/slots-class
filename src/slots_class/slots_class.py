from typing import Any, dataclass_transform
from slots_class.slots_class_meta import SlotsClassMeta

from slots_class.py_descriptor import NullDescriptor

_null_desc = NullDescriptor()


class SlotsClass(metaclass=SlotsClassMeta):
    def __init__(self, **kwargs: Any) -> None:
        d = type(self).__dict__
        k = ""
        try:
            for k, v in kwargs.items():
                d[k].__set__(self, v)
        except (KeyError, AttributeError):
            raise TypeError(f'Invalid keyword argument "{k}"') from None


# def _init_slotclass():
#     def __init__(self, **kwargs):
#         for k, v in kwargs.items():
#             setattr(self, k, v)

#     return __init__


@dataclass_transform(
    eq_default=False, order_default=False, kw_only_default=True, frozen_default=False
)
class SlotsDataclass(SlotsClass):
    def __init_subclass__(cls) -> None:
        if cls.__dict__.get("__init__", None) is None:
            cls.__init__ = SlotsClass.__init__  # type: ignore
        return super().__init_subclass__()
