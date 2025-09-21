# django__django-15498

**Repository**: django/django
**Created**: 2022-03-10T19:47:15Z
**Version**: 4.1

## Problem Statement

Fix handling empty string for If-Modified-Since header
Description
	
Empty string used to be ignored for If-Modified-Since header, but now raises exception since d6aff369ad3.
Fix handling empty string for If-Modified-Since header
Description
	
Empty string used to be ignored for If-Modified-Since header, but now raises exception since d6aff369ad3.


## Patch

```diff

diff --git a/django/views/static.py b/django/views/static.py
--- a/django/views/static.py
+++ b/django/views/static.py
@@ -129,12 +129,14 @@ def was_modified_since(header=None, mtime=0, size=0):
         if header is None:
             raise ValueError
         matches = re.match(r"^([^;]+)(; length=([0-9]+))?$", header, re.IGNORECASE)
+        if matches is None:
+            raise ValueError
         header_mtime = parse_http_date(matches[1])
         header_len = matches[3]
         if header_len and int(header_len) != size:
             raise ValueError
         if int(mtime) > header_mtime:
             raise ValueError
-    except (AttributeError, ValueError, OverflowError):
+    except (ValueError, OverflowError):
         return True
     return False


```

## Test Patch

```diff
diff --git a/tests/view_tests/tests/test_static.py b/tests/view_tests/tests/test_static.py
--- a/tests/view_tests/tests/test_static.py
+++ b/tests/view_tests/tests/test_static.py
@@ -191,3 +191,6 @@ def test_was_modified_since_fp(self):
         mtime = 1343416141.107817
         header = http_date(mtime)
         self.assertFalse(was_modified_since(header, mtime))
+
+    def test_was_modified_since_empty_string(self):
+        self.assertTrue(was_modified_since(header="", mtime=1))

```

## Test Information

**Tests that should FAIL→PASS**: ["test_was_modified_since_empty_string (view_tests.tests.test_static.StaticUtilsTests)"]

**Tests that should PASS→PASS**: ["A floating point mtime does not disturb was_modified_since (#18675).", "test_404 (view_tests.tests.test_static.StaticHelperTest)", "The static view should stream files in chunks to avoid large memory usage", "test_copes_with_empty_path_component (view_tests.tests.test_static.StaticHelperTest)", "No URLs are served if DEBUG=False.", "test_empty_prefix (view_tests.tests.test_static.StaticHelperTest)", "test_index (view_tests.tests.test_static.StaticHelperTest)", "test_index_custom_template (view_tests.tests.test_static.StaticHelperTest)", "test_index_subdir (view_tests.tests.test_static.StaticHelperTest)", "Handle bogus If-Modified-Since values gracefully", "Handle even more bogus If-Modified-Since values gracefully", "test_is_modified_since (view_tests.tests.test_static.StaticHelperTest)", "test_not_modified_since (view_tests.tests.test_static.StaticHelperTest)", "test_prefix (view_tests.tests.test_static.StaticHelperTest)", "The static view can serve static media", "No URLs are served if prefix contains a netloc part.", "test_unknown_mime_type (view_tests.tests.test_static.StaticHelperTest)", "test_404 (view_tests.tests.test_static.StaticTests)", "test_copes_with_empty_path_component (view_tests.tests.test_static.StaticTests)", "test_index (view_tests.tests.test_static.StaticTests)", "test_index_custom_template (view_tests.tests.test_static.StaticTests)", "test_index_subdir (view_tests.tests.test_static.StaticTests)", "test_is_modified_since (view_tests.tests.test_static.StaticTests)", "test_not_modified_since (view_tests.tests.test_static.StaticTests)", "test_unknown_mime_type (view_tests.tests.test_static.StaticTests)"]

**Base Commit**: d90e34c61b27fba2527834806639eebbcfab9631
**Environment Setup Commit**: 647480166bfe7532e8c471fef0146e3a17e6c0c9
