from collections import Counter
from typing import Any, Optional
from types import FunctionType, MethodType

from constants import MAIN_MODULE
from rewind import _Rewind
from utils import stringify
from _import import ImportRecord


class Call:
    __slots__ = ("order", "_module", "_name", "_call_args", "_call_kwargs")

    def __init__(
        self,
        order: int,
        module: str,
        name: str,
        args: Any,
        kwargs: Any
    ):
        self.order = order
        self._module = module
        self._name = name
        self._call_args = args
        self._call_kwargs = kwargs

        self._add_import_dependency_to_rewind()

    @classmethod
    def from_func(cls, func: FunctionType, args, kwargs) -> 'Call':
        return cls(
            module=func.__module__,
            name=func.__name__,
            args=args,
            kwargs=kwargs,
            order=_Rewind.total_order.order
        )

    def get_ordered_statement(self) -> tuple[int, str]:
        args = []
        kwargs = []
        for a in self._call_args:
            args.append(stringify(a))
        for k, v in self._call_kwargs.items():
            key = stringify(k)
            val = stringify(v)
            kwargs.append(f"{key}={val}")
        args = ', '.join(args)
        kwargs = ', '.join(kwargs)
        if kwargs: 
            return self.order, f"{self._name}({args}, {kwargs})"
        else: 
            return self.order, f"{self._name}({args})"

    def _add_import_dependency_to_rewind(self):
        module_name = self._module
        if module_name == MAIN_MODULE:
            module_name = 'main'

        if module_name not in _Rewind._imports:
            record = ImportRecord(module_name)
            _Rewind._imports[module_name] = record
        else:
            record = _Rewind._imports[module_name]
        record.add_dependency(self._name)


class MethodCall(Call):
    @classmethod
    def from_func(cls, method: MethodType, args, kwargs) -> 'Call':
        return cls(
            module=method.__module__,
            name=method.__name__,
            args=args,
            kwargs=kwargs,
            order=_Rewind.total_order.order
        )

    def get_ordered_statement(self, instance_name: str):
        order, statement = super().get_ordered_statement()
        return order, f"{instance_name}.{statement}"

    def _add_import_dependency_to_rewind(self):
        return


class InitCall(Call):
    _class_instance_counter = Counter()

    def __init__(
        self,
        order: int,
        module: str,
        name: str,
        args: Any,
        kwargs: Any
    ):
        super().__init__(order, module, name, args, kwargs)
        InitCall._class_instance_counter[name] += 1
        self._instance_name = f"{name.lower()}_{InitCall._class_instance_counter[name]}"

    def get_ordered_statement(self):
        return self.order, f"{self._instance_name} = {super().get_ordered_statement()[-1]}"


class InstanceRecord:
    def __init__(self, init_call: InitCall):
        self._init_call = init_call
        self._method_calls = []

    def get_all_ordered_statements(self) -> list[tuple[int, str]]:
        instance_name = self._init_call._instance_name
        init_statement = self._init_call.get_ordered_statement()
        return [init_statement] + [call.get_ordered_statement(instance_name) for call in self._method_calls]

    def add_call(self, call: Call):
        self._method_calls.append(call)

