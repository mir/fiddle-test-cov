# django__django-14016

**Repository**: django/django
**Created**: 2021-02-17T16:06:20Z
**Version**: 4.0

## Problem Statement

"TypeError: cannot pickle" when applying | operator to a Q object
Description
	 
		(last modified by Daniel Izquierdo)
	 
Using a reference to a non-pickleable type of object such as dict_keys in a Q object makes the | operator fail:
>>> from django.db.models import Q
>>> Q(x__in={}.keys())
<Q: (AND: ('x__in', dict_keys([])))>
>>> Q() | Q(x__in={}.keys())
Traceback (most recent call last):
...
TypeError: cannot pickle 'dict_keys' object
Even though this particular example could be solved by doing Q() | Q(x__in={}) it still feels like using .keys() should work.
I can work on a patch if there's agreement that this should not crash.


## Hints

Thanks for this report. Regression in bb0b6e526340e638522e093765e534df4e4393d2.

## Patch

```diff

diff --git a/django/db/models/query_utils.py b/django/db/models/query_utils.py
--- a/django/db/models/query_utils.py
+++ b/django/db/models/query_utils.py
@@ -5,7 +5,6 @@
 large and/or so that they can be used by other modules without getting into
 circular import difficulties.
 """
-import copy
 import functools
 import inspect
 from collections import namedtuple
@@ -46,10 +45,12 @@ def _combine(self, other, conn):
 
         # If the other Q() is empty, ignore it and just use `self`.
         if not other:
-            return copy.deepcopy(self)
+            _, args, kwargs = self.deconstruct()
+            return type(self)(*args, **kwargs)
         # Or if this Q is empty, ignore it and just use `other`.
         elif not self:
-            return copy.deepcopy(other)
+            _, args, kwargs = other.deconstruct()
+            return type(other)(*args, **kwargs)
 
         obj = type(self)()
         obj.connector = conn


```

## Test Patch

```diff
diff --git a/tests/queries/test_q.py b/tests/queries/test_q.py
--- a/tests/queries/test_q.py
+++ b/tests/queries/test_q.py
@@ -8,6 +8,10 @@ def test_combine_and_empty(self):
         self.assertEqual(q & Q(), q)
         self.assertEqual(Q() & q, q)
 
+        q = Q(x__in={}.keys())
+        self.assertEqual(q & Q(), q)
+        self.assertEqual(Q() & q, q)
+
     def test_combine_and_both_empty(self):
         self.assertEqual(Q() & Q(), Q())
 
@@ -16,6 +20,10 @@ def test_combine_or_empty(self):
         self.assertEqual(q | Q(), q)
         self.assertEqual(Q() | q, q)
 
+        q = Q(x__in={}.keys())
+        self.assertEqual(q | Q(), q)
+        self.assertEqual(Q() | q, q)
+
     def test_combine_or_both_empty(self):
         self.assertEqual(Q() | Q(), Q())
 

```

## Test Information

**Tests that should FAIL→PASS**: ["test_combine_and_empty (queries.test_q.QTests)", "test_combine_or_empty (queries.test_q.QTests)"]

**Tests that should PASS→PASS**: ["test_combine_and_both_empty (queries.test_q.QTests)", "test_combine_not_q_object (queries.test_q.QTests)", "test_combine_or_both_empty (queries.test_q.QTests)", "test_deconstruct (queries.test_q.QTests)", "test_deconstruct_and (queries.test_q.QTests)", "test_deconstruct_multiple_kwargs (queries.test_q.QTests)", "test_deconstruct_negated (queries.test_q.QTests)", "test_deconstruct_nested (queries.test_q.QTests)", "test_deconstruct_or (queries.test_q.QTests)", "test_reconstruct (queries.test_q.QTests)", "test_reconstruct_and (queries.test_q.QTests)", "test_reconstruct_negated (queries.test_q.QTests)", "test_reconstruct_or (queries.test_q.QTests)"]

**Base Commit**: 1710cdbe79c90665046034fe1700933d038d90ad
**Environment Setup Commit**: 475cffd1d64c690cdad16ede4d5e81985738ceb4
