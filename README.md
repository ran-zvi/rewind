# rewind
A python library to record calls throughout the lifetime of the running program and create a script from the captured calls

## Example
The next code snippet records function and class calls and generates a script out of them

```python
# person.py
from rewind import record

@record
class Person:
	def __init__(self, name, age):
		self._name = name
		self._age = age

	def greet(self):
		return f"Hello {self._name}, you're {self._age} years old!"

	def get_age_in_10_years(self):
		return self._add(self._age, 10)

	def _add(x, y):
		return x + y

```

```python
# foo.py

from rewind import record

@record
def foo():
	return "bar"
```

```python
# main.py
from rewind import export_rewind_capture

from person import Person
from foo import foo

if __name__ == "__main__":
	for i in range(5):
		p = Person(f"person_{i}", 20 + i)
		p.greet()
		p.get_age_in_10_years()

	foo()

export_rewind_capture("example.py")
```

Will generate the following script under `example.py`:
```python
from person import Person
from foo import foo

if __name__ == "__main__":
	person_1 = Person("person_1", 21)
	person_1.greet()
	person_1.get_age_in_10_years()
	person_2 = Person("person_1", 22)
	person_2.greet()
	person_2.get_age_in_10_years()
	person_3 = Person("person_1", 23)
	person_3.greet()
	person_3.get_age_in_10_years()
	person_4 = Person("person_1", 24)
	person_4.greet()
	person_4.get_age_in_10_years()
	person_5 = Person("person_1", 25)
	person_5.greet()
	person_5.get_age_in_10_years()

	foo()
```
Notice how `Person._add` is not recorded since it's an internal call.

### Purpose
The main purpose for this library is to create runnable scripts of heavily repeatable execution flows in CLI apps. Take for example a CLI app where you have to first authenticate, then pull some data, and then run something on it. Using this library you could record the execution and then replay it whenever you want, e.g:

```python
from client import authenticate
from data import DBreader


if __name__ == "__main__":
	authenticate("username", "password")
	
	dbreader = DBReader("db_url", "db_name")
	dbreader.pull_from_db(limit=100)
	dbreader.show_as_table(colors=True)

```

