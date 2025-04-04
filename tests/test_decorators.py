

from functools import cached_property

from pytest import raises
from slots_class.slots_class import SlotsClass


def test_cached_prop():
    class Thing(SlotsClass):
        @cached_property
        def hi(self):
            self.__name__ = 'hi'
            return 10

    v = Thing()

    assert v.hi == 10

    del v.hi

    with raises(AttributeError):
        del v.hi

    v.hi = 11

    assert v.hi == 11

    del v.hi 

    assert v.hi == 10