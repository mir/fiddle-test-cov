# django__django-14787

**Repository**: django/django
**Created**: 2021-08-23T12:59:59Z
**Version**: 4.1

## Problem Statement

method_decorator() should preserve wrapper assignments
Description
	
the function that is passed to the decorator is a partial object and does not have any of the attributes expected from a function i.e. __name__, __module__ etc...
consider the following case
def logger(func):
	@wraps(func)
	def inner(*args, **kwargs):
		try:
			result = func(*args, **kwargs)
		except Exception as e:
			result = str(e)
		finally:
			logger.debug(f"{func.__name__} called with args: {args} and kwargs: {kwargs} resulting: {result}")
	return inner
class Test:
	@method_decorator(logger)
	def hello_world(self):
		return "hello"
Test().test_method()
This results in the following exception
AttributeError: 'functools.partial' object has no attribute '__name__'


## Patch

```diff

diff --git a/django/utils/decorators.py b/django/utils/decorators.py
--- a/django/utils/decorators.py
+++ b/django/utils/decorators.py
@@ -37,7 +37,7 @@ def _wrapper(self, *args, **kwargs):
         # 'self' argument, but it's a closure over self so it can call
         # 'func'. Also, wrap method.__get__() in a function because new
         # attributes can't be set on bound method objects, only on functions.
-        bound_method = partial(method.__get__(self, type(self)))
+        bound_method = wraps(method)(partial(method.__get__(self, type(self))))
         for dec in decorators:
             bound_method = dec(bound_method)
         return bound_method(*args, **kwargs)


```

## Test Patch

```diff
diff --git a/tests/decorators/tests.py b/tests/decorators/tests.py
--- a/tests/decorators/tests.py
+++ b/tests/decorators/tests.py
@@ -425,6 +425,29 @@ class Test:
                 def __module__(cls):
                     return "tests"
 
+    def test_wrapper_assignments(self):
+        """@method_decorator preserves wrapper assignments."""
+        func_name = None
+        func_module = None
+
+        def decorator(func):
+            @wraps(func)
+            def inner(*args, **kwargs):
+                nonlocal func_name, func_module
+                func_name = getattr(func, '__name__', None)
+                func_module = getattr(func, '__module__', None)
+                return func(*args, **kwargs)
+            return inner
+
+        class Test:
+            @method_decorator(decorator)
+            def method(self):
+                return 'tests'
+
+        Test().method()
+        self.assertEqual(func_name, 'method')
+        self.assertIsNotNone(func_module)
+
 
 class XFrameOptionsDecoratorsTests(TestCase):
     """

```

## Test Information

**Tests that should FAIL→PASS**: ["@method_decorator preserves wrapper assignments."]

**Tests that should PASS→PASS**: ["test_cache_control_decorator_http_request (decorators.tests.CacheControlDecoratorTest)", "Ensures @xframe_options_deny properly sets the X-Frame-Options header.", "Ensures @xframe_options_exempt properly instructs the", "Ensures @xframe_options_sameorigin properly sets the X-Frame-Options", "Built-in decorators set certain attributes of the wrapped function.", "test_cache_page (decorators.tests.DecoratorsTest)", "Test for the require_safe decorator.", "The user_passes_test decorator can be applied multiple times (#9474).", "test_never_cache_decorator (decorators.tests.NeverCacheDecoratorTest)", "test_never_cache_decorator_http_request (decorators.tests.NeverCacheDecoratorTest)", "test_argumented (decorators.tests.MethodDecoratorTests)", "test_bad_iterable (decorators.tests.MethodDecoratorTests)", "@method_decorator can be used to decorate a class and its methods.", "test_descriptors (decorators.tests.MethodDecoratorTests)", "@method_decorator on a nonexistent method raises an error.", "@method_decorator on a non-callable attribute raises an error.", "A decorator that sets a new attribute on the method.", "test_preserve_attributes (decorators.tests.MethodDecoratorTests)", "test_preserve_signature (decorators.tests.MethodDecoratorTests)", "@method_decorator can accept a tuple of decorators."]

**Base Commit**: 004b4620f6f4ad87261e149898940f2dcd5757ef
**Environment Setup Commit**: 647480166bfe7532e8c471fef0146e3a17e6c0c9
