class ImportRecord:
    def __init__(self, module_name: str):
        self._module_name = module_name
        self._imports = set()

    def add_dependency(self, dependency: str):
        self._imports.add(dependency)

    def to_import_statement(self) -> str:
        if not self._imports:
            return

        from_statement = f"from {self._module_name} import"
        return f"{from_statement} {', '.join(self._imports)}"

