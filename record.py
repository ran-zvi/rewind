import sys
from functools import wraps
from typing import Callable
from types import FunctionType

from call import Call
from constants import CLASS_BUILTINS
from rewind import _Rewind
from hooks import __new__hook, _MethodHook, _method_hook


def record(obj: Callable):
    if isinstance(obj, type):
        return _record_decorate_class(obj)
    else:
        @wraps(obj)
        def decorator(*args, **kwargs):
            if not _Rewind.total_order.is_even():
                return obj(*args, **kwargs)
            else:
                _Rewind._calls.append(
                    Call.from_func(
                        obj,
                        args,
                        kwargs,
                    ))
                with _Rewind.total_order.advance():
                    return obj(*args, **kwargs)
        return decorator


def _record_decorate_class(cls: type) -> type:
    cls.__new__ = __new__hook
    attrs = {
        k: v for k, v in cls.__dict__.items()
        if k not in CLASS_BUILTINS or not k.startswith('__')
    }
    for name in attrs:
        attr = attrs[name]
        if isinstance(attr, FunctionType):
            setattr(cls, name,  _method_hook(attr))
    return cls

