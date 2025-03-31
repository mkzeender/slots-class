from typing import Any

import pytest
from slots_class import SlotsClass


def test_creation():
    class Testit(SlotsClass):
        def __init__(self, wow) -> None:
            self.hoo = "10"
            self.wow = wow

    assert set(Testit._all_slots_) == {"hoo", "wow"}

    v = Testit(10)
    assert v.wow == 10
    assert v.hoo == "10"

    with pytest.raises(AttributeError):
        v.blah = 100  # type: ignore
