from slots_class.slots_class import SlotsClass

__all__ = ["main", "SlotsClass"]


def main() -> None:
    print("Hello from slots-object!")

    class wut(SlotsClass):
        def __init__(self) -> None:
            super().__init__()
            self.deer = 10
            self._priv = 1

        @property
        def hi(self):
            self.goa = 1
            return 1

        @hi.setter
        def hi(self, val):
            self.goa = val

    class sub(wut):
        def __init__(self) -> None:
            super().__init__()
            self.deer = 2
            self._priv = 10

    print("slots are ", sub.__slots__, sub._all_slots_, sub._descriptors_)

    w = sub()
    print(w.hi, w.goa, w.deer, w._priv)
