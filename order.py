from contextlib import contextmanager


class TotalOrder:
    def __init__(self):
        self._order = 0

    @property
    def order(self) -> int:
        return self._order

    def is_even(self) -> bool:
        return self._order % 2 == 0

    @contextmanager
    def advance(self):
        self._order += 1
        yield
        self._order += 1


