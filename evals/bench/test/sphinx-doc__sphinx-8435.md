# sphinx-doc__sphinx-8435

**Repository**: sphinx-doc/sphinx
**Created**: 2020-11-15T17:12:24Z
**Version**: 3.4

## Problem Statement

autodoc_type_aliases does not effect to variables and attributes
**Describe the bug**
autodoc_type_aliases does not effect to variables and attributes

**To Reproduce**

```
# example.py
from __future__ import annotations


#: blah blah blah
var: String


class MyString:
    "mystring"

    #: blah blah blah
    var: String
```
```
# index.rst
.. automodule:: example
   :members:
   :undoc-members:
```
```
# conf.py
autodoc_type_aliases = {
    'String': 'example.MyString'
}
```

**Expected behavior**
`autodoc_type_aliases` should be applied to `example.var` and `example.MyString.var`.

**Your project**
N/A

**Screenshots**
N/A

**Environment info**
- OS: Mac
- Python version: 3.9.0
- Sphinx version: HEAD of 3.x branch
- Sphinx extensions: sphinx.ext.autodoc
- Extra tools: Nothing

**Additional context**
N/A


## Patch

```diff

diff --git a/sphinx/ext/autodoc/__init__.py b/sphinx/ext/autodoc/__init__.py
--- a/sphinx/ext/autodoc/__init__.py
+++ b/sphinx/ext/autodoc/__init__.py
@@ -1702,7 +1702,8 @@ def add_directive_header(self, sig: str) -> None:
         if not self.options.annotation:
             # obtain annotation for this data
             try:
-                annotations = get_type_hints(self.parent)
+                annotations = get_type_hints(self.parent, None,
+                                             self.config.autodoc_type_aliases)
             except NameError:
                 # Failed to evaluate ForwardRef (maybe TYPE_CHECKING)
                 annotations = safe_getattr(self.parent, '__annotations__', {})
@@ -2093,7 +2094,8 @@ def add_directive_header(self, sig: str) -> None:
         if not self.options.annotation:
             # obtain type annotation for this attribute
             try:
-                annotations = get_type_hints(self.parent)
+                annotations = get_type_hints(self.parent, None,
+                                             self.config.autodoc_type_aliases)
             except NameError:
                 # Failed to evaluate ForwardRef (maybe TYPE_CHECKING)
                 annotations = safe_getattr(self.parent, '__annotations__', {})


```

## Test Patch

```diff
diff --git a/tests/roots/test-ext-autodoc/target/annotations.py b/tests/roots/test-ext-autodoc/target/annotations.py
--- a/tests/roots/test-ext-autodoc/target/annotations.py
+++ b/tests/roots/test-ext-autodoc/target/annotations.py
@@ -4,6 +4,9 @@
 
 myint = int
 
+#: docstring
+variable: myint
+
 
 def sum(x: myint, y: myint) -> myint:
     """docstring"""
@@ -23,3 +26,10 @@ def mult(x: float, y: float) -> float:
 def mult(x, y):
     """docstring"""
     return x, y
+
+
+class Foo:
+    """docstring"""
+
+    #: docstring
+    attr: myint
diff --git a/tests/test_ext_autodoc_configs.py b/tests/test_ext_autodoc_configs.py
--- a/tests/test_ext_autodoc_configs.py
+++ b/tests/test_ext_autodoc_configs.py
@@ -700,6 +700,19 @@ def test_autodoc_type_aliases(app):
         '.. py:module:: target.annotations',
         '',
         '',
+        '.. py:class:: Foo()',
+        '   :module: target.annotations',
+        '',
+        '   docstring',
+        '',
+        '',
+        '   .. py:attribute:: Foo.attr',
+        '      :module: target.annotations',
+        '      :type: int',
+        '',
+        '      docstring',
+        '',
+        '',
         '.. py:function:: mult(x: int, y: int) -> int',
         '                 mult(x: float, y: float) -> float',
         '   :module: target.annotations',
@@ -712,6 +725,13 @@ def test_autodoc_type_aliases(app):
         '',
         '   docstring',
         '',
+        '',
+        '.. py:data:: variable',
+        '   :module: target.annotations',
+        '   :type: int',
+        '',
+        '   docstring',
+        '',
     ]
 
     # define aliases
@@ -722,6 +742,19 @@ def test_autodoc_type_aliases(app):
         '.. py:module:: target.annotations',
         '',
         '',
+        '.. py:class:: Foo()',
+        '   :module: target.annotations',
+        '',
+        '   docstring',
+        '',
+        '',
+        '   .. py:attribute:: Foo.attr',
+        '      :module: target.annotations',
+        '      :type: myint',
+        '',
+        '      docstring',
+        '',
+        '',
         '.. py:function:: mult(x: myint, y: myint) -> myint',
         '                 mult(x: float, y: float) -> float',
         '   :module: target.annotations',
@@ -734,6 +767,13 @@ def test_autodoc_type_aliases(app):
         '',
         '   docstring',
         '',
+        '',
+        '.. py:data:: variable',
+        '   :module: target.annotations',
+        '   :type: myint',
+        '',
+        '   docstring',
+        '',
     ]
 
 

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/test_ext_autodoc_configs.py::test_autodoc_type_aliases"]

**Tests that should PASS→PASS**: ["tests/test_ext_autodoc_configs.py::test_autoclass_content_class", "tests/test_ext_autodoc_configs.py::test_autoclass_content_init", "tests/test_ext_autodoc_configs.py::test_autoclass_content_both", "tests/test_ext_autodoc_configs.py::test_autodoc_inherit_docstrings", "tests/test_ext_autodoc_configs.py::test_autodoc_docstring_signature", "tests/test_ext_autodoc_configs.py::test_autoclass_content_and_docstring_signature_class", "tests/test_ext_autodoc_configs.py::test_autoclass_content_and_docstring_signature_init", "tests/test_ext_autodoc_configs.py::test_autoclass_content_and_docstring_signature_both", "tests/test_ext_autodoc_configs.py::test_mocked_module_imports", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_signature", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_none", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_none_for_overload", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_description", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_description_for_invalid_node", "tests/test_ext_autodoc_configs.py::test_autodoc_default_options", "tests/test_ext_autodoc_configs.py::test_autodoc_default_options_with_values"]

**Base Commit**: 5d8d6275a54f2c5fb72b82383b5712c22d337634
**Environment Setup Commit**: 3f560cd67239f75840cc7a439ab54d8509c855f6
