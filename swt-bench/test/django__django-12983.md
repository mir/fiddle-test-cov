# django__django-12983

**Repository**: django/django
**Created**: 2020-05-26T22:02:40Z
**Version**: 3.2

## Problem Statement

Make django.utils.text.slugify() strip dashes and underscores
Description
	 
		(last modified by Elinaldo do Nascimento Monteiro)
	 
Bug generation slug
Example:
from django.utils import text
text.slugify("___This is a test ---")
output: ___this-is-a-test-
Improvement after correction
from django.utils import text
text.slugify("___This is a test ---")
output: this-is-a-test
​PR


## Hints

The current version of the patch converts all underscores to dashes which (as discussed on the PR) isn't an obviously desired change. A discussion is needed to see if there's consensus about that change.

## Patch

```diff

diff --git a/django/utils/text.py b/django/utils/text.py
--- a/django/utils/text.py
+++ b/django/utils/text.py
@@ -393,17 +393,18 @@ def unescape_string_literal(s):
 @keep_lazy_text
 def slugify(value, allow_unicode=False):
     """
-    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
-    Remove characters that aren't alphanumerics, underscores, or hyphens.
-    Convert to lowercase. Also strip leading and trailing whitespace.
+    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
+    dashes to single dashes. Remove characters that aren't alphanumerics,
+    underscores, or hyphens. Convert to lowercase. Also strip leading and
+    trailing whitespace, dashes, and underscores.
     """
     value = str(value)
     if allow_unicode:
         value = unicodedata.normalize('NFKC', value)
     else:
         value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
-    value = re.sub(r'[^\w\s-]', '', value.lower()).strip()
-    return re.sub(r'[-\s]+', '-', value)
+    value = re.sub(r'[^\w\s-]', '', value.lower())
+    return re.sub(r'[-\s]+', '-', value).strip('-_')
 
 
 def camel_case_to_spaces(value):


```

## Test Patch

```diff
diff --git a/tests/utils_tests/test_text.py b/tests/utils_tests/test_text.py
--- a/tests/utils_tests/test_text.py
+++ b/tests/utils_tests/test_text.py
@@ -192,6 +192,13 @@ def test_slugify(self):
             # given - expected - Unicode?
             ('Hello, World!', 'hello-world', False),
             ('spam & eggs', 'spam-eggs', False),
+            (' multiple---dash and  space ', 'multiple-dash-and-space', False),
+            ('\t whitespace-in-value \n', 'whitespace-in-value', False),
+            ('underscore_in-value', 'underscore_in-value', False),
+            ('__strip__underscore-value___', 'strip__underscore-value', False),
+            ('--strip-dash-value---', 'strip-dash-value', False),
+            ('__strip-mixed-value---', 'strip-mixed-value', False),
+            ('_ -strip-mixed-value _-', 'strip-mixed-value', False),
             ('spam & ıçüş', 'spam-ıçüş', True),
             ('foo ıç bar', 'foo-ıç-bar', True),
             ('    foo ıç bar', 'foo-ıç-bar', True),

```

## Test Information

**Tests that should FAIL→PASS**: ["test_slugify (utils_tests.test_text.TestUtilsText)"]

**Tests that should PASS→PASS**: ["test_compress_sequence (utils_tests.test_text.TestUtilsText)", "test_format_lazy (utils_tests.test_text.TestUtilsText)", "test_get_text_list (utils_tests.test_text.TestUtilsText)", "test_get_valid_filename (utils_tests.test_text.TestUtilsText)", "test_normalize_newlines (utils_tests.test_text.TestUtilsText)", "test_phone2numeric (utils_tests.test_text.TestUtilsText)", "test_smart_split (utils_tests.test_text.TestUtilsText)", "test_truncate_chars (utils_tests.test_text.TestUtilsText)", "test_truncate_chars_html (utils_tests.test_text.TestUtilsText)", "test_truncate_html_words (utils_tests.test_text.TestUtilsText)", "test_truncate_words (utils_tests.test_text.TestUtilsText)", "test_unescape_entities (utils_tests.test_text.TestUtilsText)", "test_unescape_entities_deprecated (utils_tests.test_text.TestUtilsText)", "test_unescape_string_literal (utils_tests.test_text.TestUtilsText)", "test_wrap (utils_tests.test_text.TestUtilsText)"]

**Base Commit**: 3bc4240d979812bd11365ede04c028ea13fdc8c6
**Environment Setup Commit**: 65dfb06a1ab56c238cc80f5e1c31f61210c4577d
