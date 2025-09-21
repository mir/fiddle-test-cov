# sphinx-doc__sphinx-8801

**Repository**: sphinx-doc/sphinx
**Created**: 2021-01-31T11:12:59Z
**Version**: 3.5

## Problem Statement

autodoc: The annotation only member in superclass is treated as "undocumented"
**Describe the bug**
autodoc: The annotation only member in superclass is treated as "undocumented".

**To Reproduce**

```
# example.py
class Foo:
    """docstring"""
    attr1: int  #: docstring


class Bar(Foo):
    """docstring"""
    attr2: str  #: docstring
```
```
# index.rst
.. autoclass:: example.Bar
   :members:
   :inherited-members:
```

`Bar.attr1` is not documented. It will be shown if I give `:undoc-members:` option to the autoclass directive call. It seems the attribute is treated as undocumented.

**Expected behavior**
It should be shown.

**Your project**
No

**Screenshots**
No

**Environment info**
- OS: Mac
- Python version: 3.9.1
- Sphinx version: HEAD of 3.x
- Sphinx extensions: sphinx.ext.autodoc
- Extra tools: No

**Additional context**
No



## Patch

```diff

diff --git a/sphinx/ext/autodoc/importer.py b/sphinx/ext/autodoc/importer.py
--- a/sphinx/ext/autodoc/importer.py
+++ b/sphinx/ext/autodoc/importer.py
@@ -294,24 +294,35 @@ def get_class_members(subject: Any, objpath: List[str], attrgetter: Callable
 
     try:
         for cls in getmro(subject):
+            try:
+                modname = safe_getattr(cls, '__module__')
+                qualname = safe_getattr(cls, '__qualname__')
+                analyzer = ModuleAnalyzer.for_module(modname)
+                analyzer.analyze()
+            except AttributeError:
+                qualname = None
+                analyzer = None
+            except PycodeError:
+                analyzer = None
+
             # annotation only member (ex. attr: int)
             for name in getannotations(cls):
                 name = unmangle(cls, name)
                 if name and name not in members:
-                    members[name] = ObjectMember(name, INSTANCEATTR, class_=cls)
+                    if analyzer and (qualname, name) in analyzer.attr_docs:
+                        docstring = '\n'.join(analyzer.attr_docs[qualname, name])
+                    else:
+                        docstring = None
+
+                    members[name] = ObjectMember(name, INSTANCEATTR, class_=cls,
+                                                 docstring=docstring)
 
             # append instance attributes (cf. self.attr1) if analyzer knows
-            try:
-                modname = safe_getattr(cls, '__module__')
-                qualname = safe_getattr(cls, '__qualname__')
-                analyzer = ModuleAnalyzer.for_module(modname)
-                analyzer.analyze()
+            if analyzer:
                 for (ns, name), docstring in analyzer.attr_docs.items():
                     if ns == qualname and name not in members:
                         members[name] = ObjectMember(name, INSTANCEATTR, class_=cls,
                                                      docstring='\n'.join(docstring))
-            except (AttributeError, PycodeError):
-                pass
     except AttributeError:
         pass
 


```

## Test Patch

```diff
diff --git a/tests/roots/test-ext-autodoc/target/uninitialized_attributes.py b/tests/roots/test-ext-autodoc/target/uninitialized_attributes.py
new file mode 100644
--- /dev/null
+++ b/tests/roots/test-ext-autodoc/target/uninitialized_attributes.py
@@ -0,0 +1,8 @@
+class Base:
+    attr1: int  #: docstring
+    attr2: str
+
+
+class Derived(Base):
+    attr3: int  #: docstring
+    attr4: str
diff --git a/tests/test_ext_autodoc_autoclass.py b/tests/test_ext_autodoc_autoclass.py
--- a/tests/test_ext_autodoc_autoclass.py
+++ b/tests/test_ext_autodoc_autoclass.py
@@ -106,6 +106,73 @@ def test_inherited_instance_variable(app):
     ]
 
 
+@pytest.mark.skipif(sys.version_info < (3, 6), reason='py36+ is available since python3.6.')
+@pytest.mark.sphinx('html', testroot='ext-autodoc')
+def test_uninitialized_attributes(app):
+    options = {"members": None,
+               "inherited-members": True}
+    actual = do_autodoc(app, 'class', 'target.uninitialized_attributes.Derived', options)
+    assert list(actual) == [
+        '',
+        '.. py:class:: Derived()',
+        '   :module: target.uninitialized_attributes',
+        '',
+        '',
+        '   .. py:attribute:: Derived.attr1',
+        '      :module: target.uninitialized_attributes',
+        '      :type: int',
+        '',
+        '      docstring',
+        '',
+        '',
+        '   .. py:attribute:: Derived.attr3',
+        '      :module: target.uninitialized_attributes',
+        '      :type: int',
+        '',
+        '      docstring',
+        '',
+    ]
+
+
+@pytest.mark.skipif(sys.version_info < (3, 6), reason='py36+ is available since python3.6.')
+@pytest.mark.sphinx('html', testroot='ext-autodoc')
+def test_undocumented_uninitialized_attributes(app):
+    options = {"members": None,
+               "inherited-members": True,
+               "undoc-members": True}
+    actual = do_autodoc(app, 'class', 'target.uninitialized_attributes.Derived', options)
+    assert list(actual) == [
+        '',
+        '.. py:class:: Derived()',
+        '   :module: target.uninitialized_attributes',
+        '',
+        '',
+        '   .. py:attribute:: Derived.attr1',
+        '      :module: target.uninitialized_attributes',
+        '      :type: int',
+        '',
+        '      docstring',
+        '',
+        '',
+        '   .. py:attribute:: Derived.attr2',
+        '      :module: target.uninitialized_attributes',
+        '      :type: str',
+        '',
+        '',
+        '   .. py:attribute:: Derived.attr3',
+        '      :module: target.uninitialized_attributes',
+        '      :type: int',
+        '',
+        '      docstring',
+        '',
+        '',
+        '   .. py:attribute:: Derived.attr4',
+        '      :module: target.uninitialized_attributes',
+        '      :type: str',
+        '',
+    ]
+
+
 def test_decorators(app):
     actual = do_autodoc(app, 'class', 'target.decorator.Baz')
     assert list(actual) == [

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/test_ext_autodoc_autoclass.py::test_uninitialized_attributes"]

**Tests that should PASS→PASS**: ["tests/test_ext_autodoc_autoclass.py::test_classes", "tests/test_ext_autodoc_autoclass.py::test_instance_variable", "tests/test_ext_autodoc_autoclass.py::test_inherited_instance_variable", "tests/test_ext_autodoc_autoclass.py::test_undocumented_uninitialized_attributes", "tests/test_ext_autodoc_autoclass.py::test_decorators", "tests/test_ext_autodoc_autoclass.py::test_slots_attribute", "tests/test_ext_autodoc_autoclass.py::test_show_inheritance_for_subclass_of_generic_type", "tests/test_ext_autodoc_autoclass.py::test_class_alias"]

**Base Commit**: 7ca279e33aebb60168d35e6be4ed059f4a68f2c1
**Environment Setup Commit**: 4f8cb861e3b29186b38248fe81e4944fd987fcce
