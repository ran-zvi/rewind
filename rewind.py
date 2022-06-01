from itertools import chain

from order import TotalOrder


class _Rewind:
    _calls = []
    _class_calls = {}
    _imports = {}
    total_order = TotalOrder()

    @staticmethod
    def parse_calls() -> str:
        parsed_calls = []

        for record in _Rewind._imports.values():
            parsed_calls.append(record.to_import_statement()) 
            
        parsed_calls.append("\n\nif __name__ == \"__main__\":\n")

        all_calls = []
        for c in _Rewind._calls:
            all_calls.append(c.get_ordered_statement())
        for c in chain(_Rewind._class_calls.values()):
            all_calls.extend(c.get_all_ordered_statements())
        for order, call in sorted(all_calls, key=lambda call: call[0]):
            parsed_calls.append(f"\t{call}")

        return '\n'.join(parsed_calls)


def export_rewind_capture(file_name: str):
    with open(file_name, 'w') as py:
        parsed_calls = _Rewind.parse_calls()
        py.write(parsed_calls)

