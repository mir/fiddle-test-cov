# sphinx-doc__sphinx-8627

**Repository**: sphinx-doc/sphinx
**Created**: 2020-12-31T05:21:06Z
**Version**: 3.5

## Problem Statement

autodoc isn't able to resolve struct.Struct type annotations
**Describe the bug**
If `struct.Struct` is declared in any type annotations, I get `class reference target not found: Struct`

**To Reproduce**
Simple `index.rst`
```
Hello World
===========

code docs
=========

.. automodule:: helloworld.helloworld
```

Simple `helloworld.py`
```
import struct
import pathlib

def consume_struct(_: struct.Struct) -> None:
    pass

def make_struct() -> struct.Struct:
    mystruct = struct.Struct('HH')
    return mystruct

def make_path() -> pathlib.Path:
    return pathlib.Path()
```

Command line:
```
python3 -m sphinx -b html docs/ doc-out -nvWT
```

**Expected behavior**
If you comment out the 2 functions that have `Struct` type annotations, you'll see that `pathlib.Path` resolves fine and shows up in the resulting documentation. I'd expect that `Struct` would also resolve correctly.

**Your project**
n/a

**Screenshots**
n/a

**Environment info**
- OS: Ubuntu 18.04, 20.04
- Python version: 3.8.2
- Sphinx version: 3.2.1
- Sphinx extensions:  'sphinx.ext.autodoc',
              'sphinx.ext.autosectionlabel',
              'sphinx.ext.intersphinx',
              'sphinx.ext.doctest',
              'sphinx.ext.todo'
- Extra tools: 

**Additional context**


- [e.g. URL or Ticket]




## Hints

Unfortunately, the `struct.Struct` class does not have the correct module-info. So it is difficult to support.
```
Python 3.8.2 (default, Mar  2 2020, 00:44:41)
[Clang 11.0.0 (clang-1100.0.33.17)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import struct
>>> struct.Struct.__module__
'builtins'
```

Note: In python3.9, it returns the correct module-info. But it answers the internal module name: `_struct`.
```
Python 3.9.1 (default, Dec 18 2020, 00:18:40)
[Clang 11.0.3 (clang-1103.0.32.59)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import struct
>>> struct.Struct.__module__
'_struct'
```

So it would better to use `autodoc_type_aliases` to correct it forcedly.
```
# helloworld.py
from __future__ import annotations  # important!
from struct import Struct

def consume_struct(_: Struct) -> None:
    pass
```
```
# conf.py
autodoc_type_aliases = {
    'Struct': 'struct.Struct',
}
```

Then, it working fine.

## Patch

```diff

diff --git a/sphinx/util/typing.py b/sphinx/util/typing.py
--- a/sphinx/util/typing.py
+++ b/sphinx/util/typing.py
@@ -10,6 +10,7 @@
 
 import sys
 import typing
+from struct import Struct
 from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, TypeVar, Union
 
 from docutils import nodes
@@ -94,6 +95,9 @@ def restify(cls: Optional["Type"]) -> str:
         return ':obj:`None`'
     elif cls is Ellipsis:
         return '...'
+    elif cls is Struct:
+        # Before Python 3.9, struct.Struct class has incorrect __module__.
+        return ':class:`struct.Struct`'
     elif inspect.isNewType(cls):
         return ':class:`%s`' % cls.__name__
     elif cls.__module__ in ('__builtin__', 'builtins'):
@@ -305,6 +309,9 @@ def stringify(annotation: Any) -> str:
         return annotation.__qualname__
     elif annotation is Ellipsis:
         return '...'
+    elif annotation is Struct:
+        # Before Python 3.9, struct.Struct class has incorrect __module__.
+        return 'struct.Struct'
 
     if sys.version_info >= (3, 7):  # py37+
         return _stringify_py37(annotation)


```

## Test Patch

```diff
diff --git a/tests/test_util_typing.py b/tests/test_util_typing.py
--- a/tests/test_util_typing.py
+++ b/tests/test_util_typing.py
@@ -10,6 +10,7 @@
 
 import sys
 from numbers import Integral
+from struct import Struct
 from typing import (Any, Callable, Dict, Generator, List, NewType, Optional, Tuple, TypeVar,
                     Union)
 
@@ -43,6 +44,7 @@ def test_restify():
     assert restify(str) == ":class:`str`"
     assert restify(None) == ":obj:`None`"
     assert restify(Integral) == ":class:`numbers.Integral`"
+    assert restify(Struct) == ":class:`struct.Struct`"
     assert restify(Any) == ":obj:`Any`"
 
 
@@ -124,6 +126,7 @@ def test_stringify():
     assert stringify(str) == "str"
     assert stringify(None) == "None"
     assert stringify(Integral) == "numbers.Integral"
+    assert restify(Struct) == ":class:`struct.Struct`"
     assert stringify(Any) == "Any"
 
 

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/test_util_typing.py::test_restify", "tests/test_util_typing.py::test_stringify"]

**Tests that should PASS→PASS**: ["tests/test_util_typing.py::test_restify_type_hints_containers", "tests/test_util_typing.py::test_restify_type_hints_Callable", "tests/test_util_typing.py::test_restify_type_hints_Union", "tests/test_util_typing.py::test_restify_type_hints_typevars", "tests/test_util_typing.py::test_restify_type_hints_custom_class", "tests/test_util_typing.py::test_restify_type_hints_alias", "tests/test_util_typing.py::test_restify_type_ForwardRef", "tests/test_util_typing.py::test_restify_broken_type_hints", "tests/test_util_typing.py::test_stringify_type_hints_containers", "tests/test_util_typing.py::test_stringify_Annotated", "tests/test_util_typing.py::test_stringify_type_hints_string", "tests/test_util_typing.py::test_stringify_type_hints_Callable", "tests/test_util_typing.py::test_stringify_type_hints_Union", "tests/test_util_typing.py::test_stringify_type_hints_typevars", "tests/test_util_typing.py::test_stringify_type_hints_custom_class", "tests/test_util_typing.py::test_stringify_type_hints_alias", "tests/test_util_typing.py::test_stringify_broken_type_hints"]

**Base Commit**: 332d80ba8433aea41c3709fa52737ede4405072b
**Environment Setup Commit**: 4f8cb861e3b29186b38248fe81e4944fd987fcce
