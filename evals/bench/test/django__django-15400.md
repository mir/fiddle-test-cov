# django__django-15400

**Repository**: django/django
**Created**: 2022-02-05T19:34:55Z
**Version**: 4.1

## Problem Statement

SimpleLazyObject doesn't implement __radd__
Description
	
Technically, there's a whole bunch of magic methods it doesn't implement, compared to a complete proxy implementation, like that of wrapt.ObjectProxy, but __radd__ being missing is the one that's biting me at the moment.
As far as I can tell, the implementation can't just be
__radd__ = new_method_proxy(operator.radd)
because that doesn't exist, which is rubbish.
__radd__ = new_method_proxy(operator.attrgetter("__radd__"))
also won't work because types may not have that attr, and attrgetter doesn't supress the exception (correctly)
The minimal implementation I've found that works for me is:
	def __radd__(self, other):
		if self._wrapped is empty:
			self._setup()
		return other + self._wrapped


## Hints

Could you please give some sample code with your use case?
In a boiled-down nutshell: def lazy_consumer(): # something more complex, obviously. return [1, 3, 5] consumer = SimpleLazyObject(lazy_consumer) # inside third party code ... def some_func(param): third_party_code = [...] # then, through parameter passing, my value is provided to be used. # param is at this point, `consumer` third_party_code_plus_mine = third_party_code + param which ultimately yields: TypeError: unsupported operand type(s) for +: 'list' and 'SimpleLazyObject'
Seems okay, although I'm not an expert on the SimpleLazyObject class.
Replying to kezabelle: def lazy_consumer(): # something more complex, obviously. return [1, 3, 5] consumer = SimpleLazyObject(lazy_consumer) If you know what is the resulting type or possible resulting types of your expression, I think you better use django.utils.functional.lazy which will provide all the necessary methods.
Replying to kezabelle: As far as I can tell, the implementation can't just be __radd__ = new_method_proxy(operator.radd) because that doesn't exist, which is rubbish. __radd__ = new_method_proxy(operator.attrgetter("__radd__")) also won't work because types may not have that attr, and attrgetter doesn't supress the exception (correctly) Wouldn't the following code work? __add__ = new_method_proxy(operator.add) __radd__ = new_method_proxy(lambda a, b: operator.add(b, a)) I have tested this and it seems to work as excepted.

## Patch

```diff

diff --git a/django/utils/functional.py b/django/utils/functional.py
--- a/django/utils/functional.py
+++ b/django/utils/functional.py
@@ -432,6 +432,12 @@ def __deepcopy__(self, memo):
             return result
         return copy.deepcopy(self._wrapped, memo)
 
+    __add__ = new_method_proxy(operator.add)
+
+    @new_method_proxy
+    def __radd__(self, other):
+        return other + self
+
 
 def partition(predicate, values):
     """


```

## Test Patch

```diff
diff --git a/tests/utils_tests/test_lazyobject.py b/tests/utils_tests/test_lazyobject.py
--- a/tests/utils_tests/test_lazyobject.py
+++ b/tests/utils_tests/test_lazyobject.py
@@ -317,6 +317,17 @@ def test_repr(self):
         self.assertIsInstance(obj._wrapped, int)
         self.assertEqual(repr(obj), "<SimpleLazyObject: 42>")
 
+    def test_add(self):
+        obj1 = self.lazy_wrap(1)
+        self.assertEqual(obj1 + 1, 2)
+        obj2 = self.lazy_wrap(2)
+        self.assertEqual(obj2 + obj1, 3)
+        self.assertEqual(obj1 + obj2, 3)
+
+    def test_radd(self):
+        obj1 = self.lazy_wrap(1)
+        self.assertEqual(1 + obj1, 2)
+
     def test_trace(self):
         # See ticket #19456
         old_trace_func = sys.gettrace()

```

## Test Information

**Tests that should FAIL→PASS**: ["test_add (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_radd (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)"]

**Tests that should PASS→PASS**: ["test_bool (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_bytes (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_class (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_cmp (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_contains (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_copy_class (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_copy_class_no_evaluation (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_copy_list (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_copy_list_no_evaluation (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_deepcopy_class (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_deepcopy_class_no_evaluation (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_deepcopy_list (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_deepcopy_list_no_evaluation (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_delattr (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_delitem (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_dir (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_getattr (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_getitem (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_gt (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_hash (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_iter (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_len (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_lt (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_pickle (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_setattr (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_setattr2 (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_setitem (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_text (utils_tests.test_lazyobject.LazyObjectTestCase)", "test_bool (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_bytes (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_class (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_cmp (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_contains (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_copy_class (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_copy_class_no_evaluation (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_copy_list (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_copy_list_no_evaluation (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_deepcopy_class (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_deepcopy_class_no_evaluation (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_deepcopy_list (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_deepcopy_list_no_evaluation (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_delattr (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_delitem (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_dict (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_dir (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_getattr (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_getitem (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_gt (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_hash (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_iter (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_len (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_list_set (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_lt (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_none (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_pickle (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_repr (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_setattr (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_setattr2 (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_setitem (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_text (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "test_trace (utils_tests.test_lazyobject.SimpleLazyObjectTestCase)", "Test in a fairly synthetic setting."]

**Base Commit**: 4c76ffc2d6c77c850b4bef8d9acc197d11c47937
**Environment Setup Commit**: 647480166bfe7532e8c471fef0146e3a17e6c0c9
