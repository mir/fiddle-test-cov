# django__django-16873

**Repository**: django/django
**Created**: 2023-05-19T09:38:35Z
**Version**: 5.0

## Problem Statement

Template filter `join` should not escape the joining string if `autoescape` is `off`
Description
	
Consider the following template code snippet:
{% autoescape off %}
{{ some_list|join:some_var }}
{% endautoescape %}
in this case, the items inside some_list will not be escaped (matching the expected behavior) but some_var will forcibly be escaped. From the docs for autoescape or join I don't think this is expected behavior.
The following testcase illustrates what I think is a bug in the join filter (run inside the template_tests/filter_tests folder):
from django.template.defaultfilters import escape
from django.test import SimpleTestCase
from ..utils import setup
class RegressionTests(SimpleTestCase):
	@setup({"join01": '{{ some_list|join:some_var }}'})
	def test_join01(self):
		some_list = ["<p>Hello World!</p>", "beta & me", "<script>Hi!</script>"]
		some_var = "<br/>"
		output = self.engine.render_to_string("join01", {"some_list": some_list, "some_var": some_var})
		self.assertEqual(output, escape(some_var.join(some_list)))
	@setup({"join02": '{% autoescape off %}{{ some_list|join:some_var }}{% endautoescape %}'})
	def test_join02(self):
		some_list = ["<p>Hello World!</p>", "beta & me", "<script>Hi!</script>"]
		some_var = "<br/>"
		output = self.engine.render_to_string("join02", {"some_list": some_list, "some_var": some_var})
		self.assertEqual(output, some_var.join(some_list))
Result of this run in current main is:
.F
======================================================================
FAIL: test_join02 (template_tests.filter_tests.test_regression.RegressionTests.test_join02)
----------------------------------------------------------------------
Traceback (most recent call last):
 File "/home/nessita/fellowship/django/django/test/utils.py", line 443, in inner
	return func(*args, **kwargs)
		 ^^^^^^^^^^^^^^^^^^^^^
 File "/home/nessita/fellowship/django/tests/template_tests/utils.py", line 58, in inner
	func(self)
 File "/home/nessita/fellowship/django/tests/template_tests/filter_tests/test_regression.py", line 21, in test_join02
	self.assertEqual(output, some_var.join(some_list))
AssertionError: '<p>Hello World!</p>&lt;br/&gt;beta & me&lt;br/&gt;<script>Hi!</script>' != '<p>Hello World!</p><br/>beta & me<br/><script>Hi!</script>'
----------------------------------------------------------------------
Ran 2 tests in 0.007s


## Hints

Off-topic: As far as I'm aware it's easier to follow the expected output in assertions instead of a series of function calls, e.g. self.assertEqual(output, "<p>Hello World!</p><br/>beta & me<br/><script>Hi!</script>")

## Patch

```diff

diff --git a/django/template/defaultfilters.py b/django/template/defaultfilters.py
--- a/django/template/defaultfilters.py
+++ b/django/template/defaultfilters.py
@@ -586,8 +586,9 @@ def join(value, arg, autoescape=True):
     """Join a list with a string, like Python's ``str.join(list)``."""
     try:
         if autoescape:
-            value = [conditional_escape(v) for v in value]
-        data = conditional_escape(arg).join(value)
+            data = conditional_escape(arg).join([conditional_escape(v) for v in value])
+        else:
+            data = arg.join(value)
     except TypeError:  # Fail silently if arg isn't iterable.
         return value
     return mark_safe(data)


```

## Test Patch

```diff
diff --git a/tests/template_tests/filter_tests/test_join.py b/tests/template_tests/filter_tests/test_join.py
--- a/tests/template_tests/filter_tests/test_join.py
+++ b/tests/template_tests/filter_tests/test_join.py
@@ -55,6 +55,22 @@ def test_join08(self):
         )
         self.assertEqual(output, "alpha & beta &amp; me")
 
+    @setup(
+        {
+            "join_autoescape_off": (
+                "{% autoescape off %}"
+                "{{ var_list|join:var_joiner }}"
+                "{% endautoescape %}"
+            ),
+        }
+    )
+    def test_join_autoescape_off(self):
+        var_list = ["<p>Hello World!</p>", "beta & me", "<script>Hi!</script>"]
+        context = {"var_list": var_list, "var_joiner": "<br/>"}
+        output = self.engine.render_to_string("join_autoescape_off", context)
+        expected_result = "<p>Hello World!</p><br/>beta & me<br/><script>Hi!</script>"
+        self.assertEqual(output, expected_result)
+
 
 class FunctionTests(SimpleTestCase):
     def test_list(self):
@@ -69,7 +85,7 @@ def test_autoescape(self):
     def test_autoescape_off(self):
         self.assertEqual(
             join(["<a>", "<img>", "</a>"], "<br>", autoescape=False),
-            "<a>&lt;br&gt;<img>&lt;br&gt;</a>",
+            "<a><br><img><br></a>",
         )
 
     def test_noniterable_arg(self):

```

## Test Information

**Tests that should FAIL→PASS**: ["test_autoescape_off (template_tests.filter_tests.test_join.FunctionTests.test_autoescape_off)", "test_join_autoescape_off (template_tests.filter_tests.test_join.JoinTests.test_join_autoescape_off)"]

**Tests that should PASS→PASS**: ["test_autoescape (template_tests.filter_tests.test_join.FunctionTests.test_autoescape)", "test_list (template_tests.filter_tests.test_join.FunctionTests.test_list)", "test_noniterable_arg (template_tests.filter_tests.test_join.FunctionTests.test_noniterable_arg)", "test_noniterable_arg_autoescape_off (template_tests.filter_tests.test_join.FunctionTests.test_noniterable_arg_autoescape_off)", "test_join01 (template_tests.filter_tests.test_join.JoinTests.test_join01)", "test_join02 (template_tests.filter_tests.test_join.JoinTests.test_join02)", "test_join03 (template_tests.filter_tests.test_join.JoinTests.test_join03)", "test_join04 (template_tests.filter_tests.test_join.JoinTests.test_join04)", "test_join05 (template_tests.filter_tests.test_join.JoinTests.test_join05)", "test_join06 (template_tests.filter_tests.test_join.JoinTests.test_join06)", "test_join07 (template_tests.filter_tests.test_join.JoinTests.test_join07)", "test_join08 (template_tests.filter_tests.test_join.JoinTests.test_join08)"]

**Base Commit**: fce90950bef348803fa7cc3e6bc65f4bce429b82
**Environment Setup Commit**: 4a72da71001f154ea60906a2f74898d32b7322a7
