# pylint-dev__astroid-1196

**Repository**: pylint-dev/astroid
**Created**: 2021-10-03T15:58:07Z
**Version**: 2.12

## Problem Statement

getitem does not infer the actual unpacked value
When trying to call `Dict.getitem()` on a context where we have a dict unpacking of anything beside a real dict, astroid currently raises an `AttributeError: 'getitem'`, which has 2 problems:

- The object might be a reference against something constant, this pattern is usually seen when we have different sets of dicts that extend each other, and all of their values are inferrable. 
- We can have something that is uninferable, but in that case instead of an `AttributeError` I think it makes sense to raise the usual `AstroidIndexError` which is supposed to be already handled by the downstream.


Here is a short reproducer;

```py
from astroid import parse


source = """
X = {
    'A': 'B'
}

Y = {
    **X
}

KEY = 'A'
"""

tree = parse(source)

first_dict = tree.body[0].value
second_dict = tree.body[1].value
key = tree.body[2].value

print(f'{first_dict.getitem(key).value = }')
print(f'{second_dict.getitem(key).value = }')


```

The current output;

```
 $ python t1.py                                                                                                 3ms
first_dict.getitem(key).value = 'B'
Traceback (most recent call last):
  File "/home/isidentical/projects/astroid/t1.py", line 23, in <module>
    print(f'{second_dict.getitem(key).value = }')
  File "/home/isidentical/projects/astroid/astroid/nodes/node_classes.py", line 2254, in getitem
    return value.getitem(index, context)
AttributeError: 'Name' object has no attribute 'getitem'
```

Expeceted output;
```
 $ python t1.py                                                                                                 4ms
first_dict.getitem(key).value = 'B'
second_dict.getitem(key).value = 'B'

```



## Patch

```diff

diff --git a/astroid/nodes/node_classes.py b/astroid/nodes/node_classes.py
--- a/astroid/nodes/node_classes.py
+++ b/astroid/nodes/node_classes.py
@@ -2346,24 +2346,33 @@ def itered(self):
         """
         return [key for (key, _) in self.items]
 
-    def getitem(self, index, context=None):
+    def getitem(
+        self, index: Const | Slice, context: InferenceContext | None = None
+    ) -> NodeNG:
         """Get an item from this node.
 
         :param index: The node to use as a subscript index.
-        :type index: Const or Slice
 
         :raises AstroidTypeError: When the given index cannot be used as a
             subscript index, or if this node is not subscriptable.
         :raises AstroidIndexError: If the given index does not exist in the
             dictionary.
         """
+        # pylint: disable-next=import-outside-toplevel; circular import
+        from astroid.helpers import safe_infer
+
         for key, value in self.items:
             # TODO(cpopa): no support for overriding yet, {1:2, **{1: 3}}.
             if isinstance(key, DictUnpack):
+                inferred_value = safe_infer(value, context)
+                if not isinstance(inferred_value, Dict):
+                    continue
+
                 try:
-                    return value.getitem(index, context)
+                    return inferred_value.getitem(index, context)
                 except (AstroidTypeError, AstroidIndexError):
                     continue
+
             for inferredkey in key.infer(context):
                 if inferredkey is util.Uninferable:
                     continue


```

## Test Patch

```diff
diff --git a/tests/unittest_python3.py b/tests/unittest_python3.py
--- a/tests/unittest_python3.py
+++ b/tests/unittest_python3.py
@@ -5,7 +5,9 @@
 import unittest
 from textwrap import dedent
 
-from astroid import nodes
+import pytest
+
+from astroid import exceptions, nodes
 from astroid.builder import AstroidBuilder, extract_node
 from astroid.test_utils import require_version
 
@@ -285,6 +287,33 @@ def test_unpacking_in_dict_getitem(self) -> None:
             self.assertIsInstance(value, nodes.Const)
             self.assertEqual(value.value, expected)
 
+    @staticmethod
+    def test_unpacking_in_dict_getitem_with_ref() -> None:
+        node = extract_node(
+            """
+        a = {1: 2}
+        {**a, 2: 3}  #@
+        """
+        )
+        assert isinstance(node, nodes.Dict)
+
+        for key, expected in ((1, 2), (2, 3)):
+            value = node.getitem(nodes.Const(key))
+            assert isinstance(value, nodes.Const)
+            assert value.value == expected
+
+    @staticmethod
+    def test_unpacking_in_dict_getitem_uninferable() -> None:
+        node = extract_node("{**a, 2: 3}")
+        assert isinstance(node, nodes.Dict)
+
+        with pytest.raises(exceptions.AstroidIndexError):
+            node.getitem(nodes.Const(1))
+
+        value = node.getitem(nodes.Const(2))
+        assert isinstance(value, nodes.Const)
+        assert value.value == 3
+
     def test_format_string(self) -> None:
         code = "f'{greetings} {person}'"
         node = extract_node(code)

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/unittest_python3.py::Python3TC::test_unpacking_in_dict_getitem_uninferable", "tests/unittest_python3.py::Python3TC::test_unpacking_in_dict_getitem_with_ref"]

**Tests that should PASS→PASS**: ["tests/unittest_python3.py::Python3TC::test_annotation_as_string", "tests/unittest_python3.py::Python3TC::test_annotation_support", "tests/unittest_python3.py::Python3TC::test_as_string", "tests/unittest_python3.py::Python3TC::test_async_comprehensions", "tests/unittest_python3.py::Python3TC::test_async_comprehensions_as_string", "tests/unittest_python3.py::Python3TC::test_async_comprehensions_outside_coroutine", "tests/unittest_python3.py::Python3TC::test_format_string", "tests/unittest_python3.py::Python3TC::test_kwonlyargs_annotations_supper", "tests/unittest_python3.py::Python3TC::test_metaclass_ancestors", "tests/unittest_python3.py::Python3TC::test_metaclass_error", "tests/unittest_python3.py::Python3TC::test_metaclass_imported", "tests/unittest_python3.py::Python3TC::test_metaclass_multiple_keywords", "tests/unittest_python3.py::Python3TC::test_metaclass_yes_leak", "tests/unittest_python3.py::Python3TC::test_nested_unpacking_in_dicts", "tests/unittest_python3.py::Python3TC::test_old_syntax_works", "tests/unittest_python3.py::Python3TC::test_parent_metaclass", "tests/unittest_python3.py::Python3TC::test_simple_metaclass", "tests/unittest_python3.py::Python3TC::test_starred_notation", "tests/unittest_python3.py::Python3TC::test_underscores_in_numeral_literal", "tests/unittest_python3.py::Python3TC::test_unpacking_in_dict_getitem", "tests/unittest_python3.py::Python3TC::test_unpacking_in_dicts", "tests/unittest_python3.py::Python3TC::test_yield_from", "tests/unittest_python3.py::Python3TC::test_yield_from_as_string", "tests/unittest_python3.py::Python3TC::test_yield_from_is_generator"]

**Base Commit**: 39c2a9805970ca57093d32bbaf0e6a63e05041d8
**Environment Setup Commit**: 52f6d2d7722db383af035be929f18af5e9fe8cd5
