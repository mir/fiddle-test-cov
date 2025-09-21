# sphinx-doc__sphinx-10325

**Repository**: sphinx-doc/sphinx
**Created**: 2022-04-02T17:05:02Z
**Version**: 5.0

## Problem Statement

inherited-members should support more than one class
**Is your feature request related to a problem? Please describe.**
I have two situations:
- A class inherits from multiple other classes. I want to document members from some of the base classes but ignore some of the base classes
- A module contains several class definitions that inherit from different classes that should all be ignored (e.g., classes that inherit from list or set or tuple). I want to ignore members from list, set, and tuple while documenting all other inherited members in classes in the module.

**Describe the solution you'd like**
The :inherited-members: option to automodule should accept a list of classes. If any of these classes are encountered as base classes when instantiating autoclass documentation, they should be ignored.

**Describe alternatives you've considered**
The alternative is to not use automodule, but instead manually enumerate several autoclass blocks for a module. This only addresses the second bullet in the problem description and not the first. It is also tedious for modules containing many class definitions.




## Hints

+1: Acceptable change.
>A class inherits from multiple other classes. I want to document members from some of the base classes but ignore some of the base classes

For example, there is a class that inherits multiple base classes:
```
class MyClass(Parent1, Parent2, Parent3, ...):
    pass
```
and

```
.. autoclass:: example.MyClass
   :inherited-members: Parent2
```

How should the new `:inherited-members:` work? Do you mean that the member of Parent2 are ignored and the Parent1's and Parent3's are documented? And how about the methods of the super classes of `Parent1`?

Note: The current behavior is ignoring Parent2, Parent3, and the super classes of them (including Parent1's also). In python words, the classes after `Parent2` in MRO list are all ignored.

## Patch

```diff

diff --git a/sphinx/ext/autodoc/__init__.py b/sphinx/ext/autodoc/__init__.py
--- a/sphinx/ext/autodoc/__init__.py
+++ b/sphinx/ext/autodoc/__init__.py
@@ -109,12 +109,14 @@ def exclude_members_option(arg: Any) -> Union[object, Set[str]]:
     return {x.strip() for x in arg.split(',') if x.strip()}
 
 
-def inherited_members_option(arg: Any) -> Union[object, Set[str]]:
+def inherited_members_option(arg: Any) -> Set[str]:
     """Used to convert the :members: option to auto directives."""
     if arg in (None, True):
-        return 'object'
+        return {'object'}
+    elif arg:
+        return set(x.strip() for x in arg.split(','))
     else:
-        return arg
+        return set()
 
 
 def member_order_option(arg: Any) -> Optional[str]:
@@ -680,9 +682,11 @@ def filter_members(self, members: ObjectMembers, want_all: bool
         ``autodoc-skip-member`` event.
         """
         def is_filtered_inherited_member(name: str, obj: Any) -> bool:
+            inherited_members = self.options.inherited_members or set()
+
             if inspect.isclass(self.object):
                 for cls in self.object.__mro__:
-                    if cls.__name__ == self.options.inherited_members and cls != self.object:
+                    if cls.__name__ in inherited_members and cls != self.object:
                         # given member is a member of specified *super class*
                         return True
                     elif name in cls.__dict__:


```

## Test Patch

```diff
diff --git a/tests/roots/test-ext-autodoc/target/inheritance.py b/tests/roots/test-ext-autodoc/target/inheritance.py
--- a/tests/roots/test-ext-autodoc/target/inheritance.py
+++ b/tests/roots/test-ext-autodoc/target/inheritance.py
@@ -15,3 +15,8 @@ class Derived(Base):
     def inheritedmeth(self):
         # no docstring here
         pass
+
+
+class MyList(list):
+    def meth(self):
+        """docstring"""
diff --git a/tests/test_ext_autodoc_automodule.py b/tests/test_ext_autodoc_automodule.py
--- a/tests/test_ext_autodoc_automodule.py
+++ b/tests/test_ext_autodoc_automodule.py
@@ -113,6 +113,68 @@ def test_automodule_special_members(app):
     ]
 
 
+@pytest.mark.sphinx('html', testroot='ext-autodoc')
+def test_automodule_inherited_members(app):
+    if sys.version_info < (3, 7):
+        args = ''
+    else:
+        args = '(iterable=(), /)'
+
+    options = {'members': None,
+               'undoc-members': None,
+               'inherited-members': 'Base, list'}
+    actual = do_autodoc(app, 'module', 'target.inheritance', options)
+    assert list(actual) == [
+        '',
+        '.. py:module:: target.inheritance',
+        '',
+        '',
+        '.. py:class:: Base()',
+        '   :module: target.inheritance',
+        '',
+        '',
+        '   .. py:method:: Base.inheritedclassmeth()',
+        '      :module: target.inheritance',
+        '      :classmethod:',
+        '',
+        '      Inherited class method.',
+        '',
+        '',
+        '   .. py:method:: Base.inheritedmeth()',
+        '      :module: target.inheritance',
+        '',
+        '      Inherited function.',
+        '',
+        '',
+        '   .. py:method:: Base.inheritedstaticmeth(cls)',
+        '      :module: target.inheritance',
+        '      :staticmethod:',
+        '',
+        '      Inherited static method.',
+        '',
+        '',
+        '.. py:class:: Derived()',
+        '   :module: target.inheritance',
+        '',
+        '',
+        '   .. py:method:: Derived.inheritedmeth()',
+        '      :module: target.inheritance',
+        '',
+        '      Inherited function.',
+        '',
+        '',
+        '.. py:class:: MyList%s' % args,
+        '   :module: target.inheritance',
+        '',
+        '',
+        '   .. py:method:: MyList.meth()',
+        '      :module: target.inheritance',
+        '',
+        '      docstring',
+        '',
+    ]
+
+
 @pytest.mark.sphinx('html', testroot='ext-autodoc',
                     confoverrides={'autodoc_mock_imports': ['missing_module',
                                                             'missing_package1',

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/test_ext_autodoc_automodule.py::test_automodule_inherited_members"]

**Tests that should PASS→PASS**: ["tests/test_ext_autodoc_automodule.py::test_empty_all", "tests/test_ext_autodoc_automodule.py::test_automodule", "tests/test_ext_autodoc_automodule.py::test_automodule_undoc_members", "tests/test_ext_autodoc_automodule.py::test_automodule_special_members", "tests/test_ext_autodoc_automodule.py::test_subclass_of_mocked_object"]

**Base Commit**: 7bdc11e87c7d86dcc2a087eccb7a7c129a473415
**Environment Setup Commit**: 60775ec4c4ea08509eee4b564cbf90f316021aff
