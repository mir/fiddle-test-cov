# pylint-dev__astroid-1978

**Repository**: pylint-dev/astroid
**Created**: 2023-01-28T06:14:39Z
**Version**: 2.14

## Problem Statement

Deprecation warnings from numpy
### Steps to reproduce

1. Run pylint over the following test case:

```
"""Test case"""

import numpy as np
value = np.random.seed(1234)
```

### Current behavior
```
/home/bje/source/nemo/myenv/lib/python3.10/site-packages/astroid/raw_building.py:470: FutureWarning: In the future `np.long` will be defined as the corresponding NumPy scalar.  (This may have returned Python scalars in past versions.
  getattr(sys.modules[modname], name)
/home/bje/source/nemo/myenv/lib/python3.10/site-packages/astroid/raw_building.py:470: FutureWarning: In the future `np.long` will be defined as the corresponding NumPy scalar.  (This may have returned Python scalars in past versions.
  getattr(sys.modules[modname], name)
```

### Expected behavior
There should be no future warnings.

### python -c "from astroid import __pkginfo__; print(__pkginfo__.version)" output
2.12.13


## Hints

This seems very similar to https://github.com/PyCQA/astroid/pull/1514 that was fixed in 2.12.0.
I'm running 2.12.13 (> 2.12.0), so the fix isn't working in this case?
I don't know why #1514 did not fix this, I think we were capturing both stdout and stderr, so this will need some investigation. My guess would be that there's somewhere else to apply the same method to.
Hello, 
I see the same error with pylint on our tool [demcompare](https://github.com/CNES/demcompare). Pylint version:
```
pylint --version
pylint 2.15.9
astroid 2.12.13
Python 3.8.10 (default, Nov 14 2022, 12:59:47) 
[GCC 9.4.0]
```
I confirm the weird astroid lower warning and I don't know how to bypass it with pylint checking. 

```
pylint demcompare 
/home/duboise/work/src/demcompare/venv/lib/python3.8/site-packages/astroid/raw_building.py:470: FutureWarning: In the future `np.long` will be defined as the corresponding NumPy scalar.  (This may have returned Python scalars in past versions.
  getattr(sys.modules[modname], name)
... (four times)
```

Thanks in advance if there is a solution
Cordially

> Thanks in advance if there is a solution

while annoying the warning does not make pylint fail. Just ignore it. In a CI you can just check pylint return code. It will return 0 as expected
I agree, even if annoying because it feels our code as a problem somewhere, the CI with pylint doesn't fail indeed. Thanks for the answer that confirm to not bother for now. 
That might be fine in a CI environment, but for users, ultimately, ignoring warnings becomes difficult when there are too many such warnings. I would like to see this fixed.
Oh, it was not an argument in favour of not fixing it. It was just to point out that it is not a breaking problem. It is "just" a lot of quite annoying warnings. I am following the issue because it annoys me too. So I am in the same "I hope they will fix it" boat
> I don't know why https://github.com/PyCQA/astroid/pull/1514 did not fix this, I think we were capturing both stdout and stderr, so this will need some investigation. My guess would be that there's somewhere else to apply the same method to.

That PR only addressed import-time. This `FutureWarning` is emitted by numpy's package-level `__getattr__` method, not during import.

## Patch

```diff

diff --git a/astroid/raw_building.py b/astroid/raw_building.py
--- a/astroid/raw_building.py
+++ b/astroid/raw_building.py
@@ -10,11 +10,14 @@
 
 import builtins
 import inspect
+import io
+import logging
 import os
 import sys
 import types
 import warnings
 from collections.abc import Iterable
+from contextlib import redirect_stderr, redirect_stdout
 from typing import Any, Union
 
 from astroid import bases, nodes
@@ -22,6 +25,9 @@
 from astroid.manager import AstroidManager
 from astroid.nodes import node_classes
 
+logger = logging.getLogger(__name__)
+
+
 _FunctionTypes = Union[
     types.FunctionType,
     types.MethodType,
@@ -471,7 +477,26 @@ def imported_member(self, node, member, name: str) -> bool:
             # check if it sounds valid and then add an import node, else use a
             # dummy node
             try:
-                getattr(sys.modules[modname], name)
+                with redirect_stderr(io.StringIO()) as stderr, redirect_stdout(
+                    io.StringIO()
+                ) as stdout:
+                    getattr(sys.modules[modname], name)
+                    stderr_value = stderr.getvalue()
+                    if stderr_value:
+                        logger.error(
+                            "Captured stderr while getting %s from %s:\n%s",
+                            name,
+                            sys.modules[modname],
+                            stderr_value,
+                        )
+                    stdout_value = stdout.getvalue()
+                    if stdout_value:
+                        logger.info(
+                            "Captured stdout while getting %s from %s:\n%s",
+                            name,
+                            sys.modules[modname],
+                            stdout_value,
+                        )
             except (KeyError, AttributeError):
                 attach_dummy_node(node, name, member)
             else:


```

## Test Patch

```diff
diff --git a/tests/unittest_raw_building.py b/tests/unittest_raw_building.py
--- a/tests/unittest_raw_building.py
+++ b/tests/unittest_raw_building.py
@@ -8,8 +8,15 @@
 # For details: https://github.com/PyCQA/astroid/blob/main/LICENSE
 # Copyright (c) https://github.com/PyCQA/astroid/blob/main/CONTRIBUTORS.txt
 
+from __future__ import annotations
+
+import logging
+import os
+import sys
 import types
 import unittest
+from typing import Any
+from unittest import mock
 
 import _io
 import pytest
@@ -117,5 +124,45 @@ def test_module_object_with_broken_getattr(self) -> None:
         AstroidBuilder().inspect_build(fm_getattr, "test")
 
 
+@pytest.mark.skipif(
+    "posix" not in sys.builtin_module_names, reason="Platform doesn't support posix"
+)
+def test_build_module_getattr_catch_output(
+    capsys: pytest.CaptureFixture[str],
+    caplog: pytest.LogCaptureFixture,
+) -> None:
+    """Catch stdout and stderr in module __getattr__ calls when building a module.
+
+    Usually raised by DeprecationWarning or FutureWarning.
+    """
+    caplog.set_level(logging.INFO)
+    original_sys = sys.modules
+    original_module = sys.modules["posix"]
+    expected_out = "INFO (TEST): Welcome to posix!"
+    expected_err = "WARNING (TEST): Monkey-patched version of posix - module getattr"
+
+    class CustomGetattr:
+        def __getattr__(self, name: str) -> Any:
+            print(f"{expected_out}")
+            print(expected_err, file=sys.stderr)
+            return getattr(original_module, name)
+
+    def mocked_sys_modules_getitem(name: str) -> types.ModuleType | CustomGetattr:
+        if name != "posix":
+            return original_sys[name]
+        return CustomGetattr()
+
+    with mock.patch("astroid.raw_building.sys.modules") as sys_mock:
+        sys_mock.__getitem__.side_effect = mocked_sys_modules_getitem
+        builder = AstroidBuilder()
+        builder.inspect_build(os)
+
+    out, err = capsys.readouterr()
+    assert expected_out in caplog.text
+    assert expected_err in caplog.text
+    assert not out
+    assert not err
+
+
 if __name__ == "__main__":
     unittest.main()

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/unittest_raw_building.py::test_build_module_getattr_catch_output"]

**Tests that should PASS→PASS**: ["tests/unittest_raw_building.py::RawBuildingTC::test_attach_dummy_node", "tests/unittest_raw_building.py::RawBuildingTC::test_build_class", "tests/unittest_raw_building.py::RawBuildingTC::test_build_from_import", "tests/unittest_raw_building.py::RawBuildingTC::test_build_function", "tests/unittest_raw_building.py::RawBuildingTC::test_build_function_args", "tests/unittest_raw_building.py::RawBuildingTC::test_build_function_deepinspect_deprecation", "tests/unittest_raw_building.py::RawBuildingTC::test_build_function_defaults", "tests/unittest_raw_building.py::RawBuildingTC::test_build_function_kwonlyargs", "tests/unittest_raw_building.py::RawBuildingTC::test_build_function_posonlyargs", "tests/unittest_raw_building.py::RawBuildingTC::test_build_module", "tests/unittest_raw_building.py::RawBuildingTC::test_io_is__io", "tests/unittest_raw_building.py::RawBuildingTC::test_module_object_with_broken_getattr"]

**Base Commit**: 0c9ab0fe56703fa83c73e514a1020d398d23fa7f
**Environment Setup Commit**: 0c9ab0fe56703fa83c73e514a1020d398d23fa7f
