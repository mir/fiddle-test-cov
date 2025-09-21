# django__django-15202

**Repository**: django/django
**Created**: 2021-12-15T15:04:13Z
**Version**: 4.1

## Problem Statement

URLField throws ValueError instead of ValidationError on clean
Description
	
forms.URLField( ).clean('////]@N.AN')
results in:
	ValueError: Invalid IPv6 URL
	Traceback (most recent call last):
	 File "basic_fuzzer.py", line 22, in TestOneInput
	 File "fuzzers.py", line 350, in test_forms_URLField
	 File "django/forms/fields.py", line 151, in clean
	 File "django/forms/fields.py", line 136, in run_validators
	 File "django/core/validators.py", line 130, in __call__
	 File "urllib/parse.py", line 440, in urlsplit


## Patch

```diff

diff --git a/django/core/validators.py b/django/core/validators.py
--- a/django/core/validators.py
+++ b/django/core/validators.py
@@ -108,15 +108,16 @@ def __call__(self, value):
             raise ValidationError(self.message, code=self.code, params={'value': value})
 
         # Then check full URL
+        try:
+            splitted_url = urlsplit(value)
+        except ValueError:
+            raise ValidationError(self.message, code=self.code, params={'value': value})
         try:
             super().__call__(value)
         except ValidationError as e:
             # Trivial case failed. Try for possible IDN domain
             if value:
-                try:
-                    scheme, netloc, path, query, fragment = urlsplit(value)
-                except ValueError:  # for example, "Invalid IPv6 URL"
-                    raise ValidationError(self.message, code=self.code, params={'value': value})
+                scheme, netloc, path, query, fragment = splitted_url
                 try:
                     netloc = punycode(netloc)  # IDN -> ACE
                 except UnicodeError:  # invalid domain part
@@ -127,7 +128,7 @@ def __call__(self, value):
                 raise
         else:
             # Now verify IPv6 in the netloc part
-            host_match = re.search(r'^\[(.+)\](?::\d{1,5})?$', urlsplit(value).netloc)
+            host_match = re.search(r'^\[(.+)\](?::\d{1,5})?$', splitted_url.netloc)
             if host_match:
                 potential_ip = host_match[1]
                 try:
@@ -139,7 +140,7 @@ def __call__(self, value):
         # section 3.1. It's defined to be 255 bytes or less, but this includes
         # one byte for the length of the name and one byte for the trailing dot
         # that's used to indicate absolute names in DNS.
-        if len(urlsplit(value).hostname) > 253:
+        if splitted_url.hostname is None or len(splitted_url.hostname) > 253:
             raise ValidationError(self.message, code=self.code, params={'value': value})
 
 


```

## Test Patch

```diff
diff --git a/tests/forms_tests/field_tests/test_urlfield.py b/tests/forms_tests/field_tests/test_urlfield.py
--- a/tests/forms_tests/field_tests/test_urlfield.py
+++ b/tests/forms_tests/field_tests/test_urlfield.py
@@ -100,6 +100,10 @@ def test_urlfield_clean_invalid(self):
             # even on domains that don't fail the domain label length check in
             # the regex.
             'http://%s' % ("X" * 200,),
+            # urlsplit() raises ValueError.
+            '////]@N.AN',
+            # Empty hostname.
+            '#@A.bO',
         ]
         msg = "'Enter a valid URL.'"
         for value in tests:

```

## Test Information

**Tests that should FAIL→PASS**: ["test_urlfield_clean_invalid (forms_tests.field_tests.test_urlfield.URLFieldTest)", "test_urlfield_clean_not_required (forms_tests.field_tests.test_urlfield.URLFieldTest)"]

**Tests that should PASS→PASS**: ["test_urlfield_clean (forms_tests.field_tests.test_urlfield.URLFieldTest)", "test_urlfield_clean_required (forms_tests.field_tests.test_urlfield.URLFieldTest)", "test_urlfield_strip_on_none_value (forms_tests.field_tests.test_urlfield.URLFieldTest)", "test_urlfield_unable_to_set_strip_kwarg (forms_tests.field_tests.test_urlfield.URLFieldTest)", "test_urlfield_widget (forms_tests.field_tests.test_urlfield.URLFieldTest)", "test_urlfield_widget_max_min_length (forms_tests.field_tests.test_urlfield.URLFieldTest)"]

**Base Commit**: 4fd3044ca0135da903a70dfb66992293f529ecf1
**Environment Setup Commit**: 647480166bfe7532e8c471fef0146e3a17e6c0c9
