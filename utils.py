from types import FunctionType


def stringify(x):
    if type(x) in (str, int, float, bool, list, dict):
        return str(x)
    elif isinstance(x, FunctionType):
        return x.__name__
    else:
        return type(x).__name__

