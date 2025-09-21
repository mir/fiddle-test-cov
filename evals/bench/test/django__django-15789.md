# django__django-15789

**Repository**: django/django
**Created**: 2022-06-23T08:59:04Z
**Version**: 4.2

## Problem Statement

Add an encoder parameter to django.utils.html.json_script().
Description
	
I have a use case where I want to customize the JSON encoding of some values to output to the template layer. It looks like django.utils.html.json_script is a good utility for that, however the JSON encoder is hardcoded to DjangoJSONEncoder. I think it would be nice to be able to pass a custom encoder class.
By the way, django.utils.html.json_script is not documented (only its template filter counterpart is), would it be a good thing to add to the docs?


## Hints

Sounds good, and yes, we should document django.utils.html.json_script().
​PR I'll also add docs for json_script() soon
​PR

## Patch

```diff

diff --git a/django/utils/html.py b/django/utils/html.py
--- a/django/utils/html.py
+++ b/django/utils/html.py
@@ -59,7 +59,7 @@ def escapejs(value):
 }
 
 
-def json_script(value, element_id=None):
+def json_script(value, element_id=None, encoder=None):
     """
     Escape all the HTML/XML special characters with their unicode escapes, so
     value is safe to be output anywhere except for inside a tag attribute. Wrap
@@ -67,7 +67,9 @@ def json_script(value, element_id=None):
     """
     from django.core.serializers.json import DjangoJSONEncoder
 
-    json_str = json.dumps(value, cls=DjangoJSONEncoder).translate(_json_script_escapes)
+    json_str = json.dumps(value, cls=encoder or DjangoJSONEncoder).translate(
+        _json_script_escapes
+    )
     if element_id:
         template = '<script id="{}" type="application/json">{}</script>'
         args = (element_id, mark_safe(json_str))


```

## Test Patch

```diff
diff --git a/tests/utils_tests/test_html.py b/tests/utils_tests/test_html.py
--- a/tests/utils_tests/test_html.py
+++ b/tests/utils_tests/test_html.py
@@ -1,6 +1,7 @@
 import os
 from datetime import datetime
 
+from django.core.serializers.json import DjangoJSONEncoder
 from django.test import SimpleTestCase
 from django.utils.functional import lazystr
 from django.utils.html import (
@@ -211,6 +212,16 @@ def test_json_script(self):
             with self.subTest(arg=arg):
                 self.assertEqual(json_script(arg, "test_id"), expected)
 
+    def test_json_script_custom_encoder(self):
+        class CustomDjangoJSONEncoder(DjangoJSONEncoder):
+            def encode(self, o):
+                return '{"hello": "world"}'
+
+        self.assertHTMLEqual(
+            json_script({}, encoder=CustomDjangoJSONEncoder),
+            '<script type="application/json">{"hello": "world"}</script>',
+        )
+
     def test_json_script_without_id(self):
         self.assertHTMLEqual(
             json_script({"key": "value"}),

```

## Test Information

**Tests that should FAIL→PASS**: ["test_json_script_custom_encoder (utils_tests.test_html.TestUtilsHtml)"]

**Tests that should PASS→PASS**: ["test_conditional_escape (utils_tests.test_html.TestUtilsHtml)", "test_escape (utils_tests.test_html.TestUtilsHtml)", "test_escapejs (utils_tests.test_html.TestUtilsHtml)", "test_format_html (utils_tests.test_html.TestUtilsHtml)", "test_html_safe (utils_tests.test_html.TestUtilsHtml)", "test_html_safe_defines_html_error (utils_tests.test_html.TestUtilsHtml)", "test_html_safe_doesnt_define_str (utils_tests.test_html.TestUtilsHtml)", "test_html_safe_subclass (utils_tests.test_html.TestUtilsHtml)", "test_json_script (utils_tests.test_html.TestUtilsHtml)", "test_json_script_without_id (utils_tests.test_html.TestUtilsHtml)", "test_linebreaks (utils_tests.test_html.TestUtilsHtml)", "test_smart_urlquote (utils_tests.test_html.TestUtilsHtml)", "test_strip_spaces_between_tags (utils_tests.test_html.TestUtilsHtml)", "test_strip_tags (utils_tests.test_html.TestUtilsHtml)", "test_strip_tags_files (utils_tests.test_html.TestUtilsHtml)", "test_urlize (utils_tests.test_html.TestUtilsHtml)", "test_urlize_unchanged_inputs (utils_tests.test_html.TestUtilsHtml)"]

**Base Commit**: d4d5427571b4bf3a21c902276c2a00215c2a37cc
**Environment Setup Commit**: 0fbdb9784da915fce5dcc1fe82bac9b4785749e5
