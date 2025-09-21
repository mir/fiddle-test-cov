# django__django-16046

**Repository**: django/django
**Created**: 2022-09-10T13:27:38Z
**Version**: 4.2

## Problem Statement

Fix numberformat.py "string index out of range" when null
Description
	
When:
if str_number[0] == "-"
encounters a number field that's null when formatting for the admin list_display this causes an 
IndexError: string index out of range
I can attach the proposed fix here, or open a pull request on GitHub if you like?


## Hints

proposed fix patch
Please provide a pull request, including a test.

## Patch

```diff

diff --git a/django/utils/numberformat.py b/django/utils/numberformat.py
--- a/django/utils/numberformat.py
+++ b/django/utils/numberformat.py
@@ -25,6 +25,8 @@ def format(
         module in locale.localeconv() LC_NUMERIC grouping (e.g. (3, 2, 0)).
     * thousand_sep: Thousand separator symbol (for example ",")
     """
+    if number is None or number == "":
+        return mark_safe(number)
     use_grouping = (
         use_l10n or (use_l10n is None and settings.USE_L10N)
     ) and settings.USE_THOUSAND_SEPARATOR


```

## Test Patch

```diff
diff --git a/tests/utils_tests/test_numberformat.py b/tests/utils_tests/test_numberformat.py
--- a/tests/utils_tests/test_numberformat.py
+++ b/tests/utils_tests/test_numberformat.py
@@ -172,3 +172,7 @@ def __format__(self, specifier, **kwargs):
 
         price = EuroDecimal("1.23")
         self.assertEqual(nformat(price, ","), "€ 1,23")
+
+    def test_empty(self):
+        self.assertEqual(nformat("", "."), "")
+        self.assertEqual(nformat(None, "."), "None")

```

## Test Information

**Tests that should FAIL→PASS**: ["test_empty (utils_tests.test_numberformat.TestNumberFormat)"]

**Tests that should PASS→PASS**: ["test_decimal_numbers (utils_tests.test_numberformat.TestNumberFormat)", "test_decimal_subclass (utils_tests.test_numberformat.TestNumberFormat)", "test_float_numbers (utils_tests.test_numberformat.TestNumberFormat)", "test_format_number (utils_tests.test_numberformat.TestNumberFormat)", "test_format_string (utils_tests.test_numberformat.TestNumberFormat)", "test_large_number (utils_tests.test_numberformat.TestNumberFormat)"]

**Base Commit**: ec13e801b820614ff374cb0046092caab8d67249
**Environment Setup Commit**: 0fbdb9784da915fce5dcc1fe82bac9b4785749e5
