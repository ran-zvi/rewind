from functools import partial, wraps
from types import MethodType

from constants import MAIN_MODULE
from call import MethodCall, InitCall, InstanceRecord, Call
from rewind import _Rewind
from _import import ImportRecord


class _MethodHook:
    def __init__(self, m: MethodType):
        self._method = m
        self._instance = None

    def __call__(self, *args, **kwargs):
        if not _Rewind.total_order.is_even():
            return self._method(*args, **kwargs)
        else:
            _Rewind._class_calls[self._instance].add_call(
                MethodCall.from_func(
                    self._method,
                    args,
                    kwargs,
                ))
            with _Rewind.total_order.advance():
                return self._method(*args, **kwargs)

    def __get__(self, instance: object, owner: type):
        self._instance = instance
        return partial(self.__call__, instance)


def _method_hook(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not _Rewind.total_order.is_even():
            return method(self, *args, **kwargs)
        else:
            _Rewind._class_calls[self].add_call(
                MethodCall.from_func(
                    method,
                    args,
                    kwargs,
                ))
            with _Rewind.total_order.advance():
                return method(self, *args, **kwargs)
    return wrapper


def __new__hook(cls, *args, **kwargs):
    if not _Rewind.total_order.is_even():
        return object.__new__(cls)
    else:
        record = InstanceRecord(InitCall.from_func(cls, args, kwargs))
        with _Rewind.total_order.advance():
            obj = object.__new__(cls)
        _Rewind._class_calls[obj] = record
        return obj
