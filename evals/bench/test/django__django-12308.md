# django__django-12308

**Repository**: django/django
**Created**: 2020-01-12T04:21:15Z
**Version**: 3.1

## Problem Statement

JSONField are not properly displayed in admin when they are readonly.
Description
	
JSONField values are displayed as dict when readonly in the admin.
For example, {"foo": "bar"} would be displayed as {'foo': 'bar'}, which is not valid JSON.
I believe the fix would be to add a special case in django.contrib.admin.utils.display_for_field to call the prepare_value of the JSONField (not calling json.dumps directly to take care of the InvalidJSONInput case).


## Hints

​PR
The proposed patch is problematic as the first version coupled contrib.postgres with .admin and the current one is based off the type name which is brittle and doesn't account for inheritance. It might be worth waiting for #12990 to land before proceeding here as the patch will be able to simply rely of django.db.models.JSONField instance checks from that point.

## Patch

```diff

diff --git a/django/contrib/admin/utils.py b/django/contrib/admin/utils.py
--- a/django/contrib/admin/utils.py
+++ b/django/contrib/admin/utils.py
@@ -398,6 +398,11 @@ def display_for_field(value, field, empty_value_display):
         return formats.number_format(value)
     elif isinstance(field, models.FileField) and value:
         return format_html('<a href="{}">{}</a>', value.url, value)
+    elif isinstance(field, models.JSONField) and value:
+        try:
+            return field.get_prep_value(value)
+        except TypeError:
+            return display_for_value(value, empty_value_display)
     else:
         return display_for_value(value, empty_value_display)
 


```

## Test Patch

```diff
diff --git a/tests/admin_utils/tests.py b/tests/admin_utils/tests.py
--- a/tests/admin_utils/tests.py
+++ b/tests/admin_utils/tests.py
@@ -176,6 +176,23 @@ def test_null_display_for_field(self):
         display_value = display_for_field(None, models.FloatField(), self.empty_value)
         self.assertEqual(display_value, self.empty_value)
 
+        display_value = display_for_field(None, models.JSONField(), self.empty_value)
+        self.assertEqual(display_value, self.empty_value)
+
+    def test_json_display_for_field(self):
+        tests = [
+            ({'a': {'b': 'c'}}, '{"a": {"b": "c"}}'),
+            (['a', 'b'], '["a", "b"]'),
+            ('a', '"a"'),
+            ({('a', 'b'): 'c'}, "{('a', 'b'): 'c'}"),  # Invalid JSON.
+        ]
+        for value, display_value in tests:
+            with self.subTest(value=value):
+                self.assertEqual(
+                    display_for_field(value, models.JSONField(), self.empty_value),
+                    display_value,
+                )
+
     def test_number_formats_display_for_field(self):
         display_value = display_for_field(12345.6789, models.FloatField(), self.empty_value)
         self.assertEqual(display_value, '12345.6789')

```

## Test Information

**Tests that should FAIL→PASS**: ["test_json_display_for_field (admin_utils.tests.UtilsTests)", "test_label_for_field (admin_utils.tests.UtilsTests)"]

**Tests that should PASS→PASS**: ["test_cyclic (admin_utils.tests.NestedObjectsTests)", "test_non_added_parent (admin_utils.tests.NestedObjectsTests)", "test_on_delete_do_nothing (admin_utils.tests.NestedObjectsTests)", "test_queries (admin_utils.tests.NestedObjectsTests)", "test_relation_on_abstract (admin_utils.tests.NestedObjectsTests)", "test_siblings (admin_utils.tests.NestedObjectsTests)", "test_unrelated_roots (admin_utils.tests.NestedObjectsTests)", "test_flatten (admin_utils.tests.UtilsTests)", "test_flatten_fieldsets (admin_utils.tests.UtilsTests)", "test_label_for_field_form_argument (admin_utils.tests.UtilsTests)", "test_label_for_property (admin_utils.tests.UtilsTests)", "test_list_display_for_value (admin_utils.tests.UtilsTests)", "test_list_display_for_value_boolean (admin_utils.tests.UtilsTests)", "test_null_display_for_field (admin_utils.tests.UtilsTests)", "test_number_formats_display_for_field (admin_utils.tests.UtilsTests)", "test_number_formats_with_thousand_separator_display_for_field (admin_utils.tests.UtilsTests)", "test_quote (admin_utils.tests.UtilsTests)", "test_related_name (admin_utils.tests.UtilsTests)", "test_safestring_in_field_label (admin_utils.tests.UtilsTests)", "test_values_from_lookup_field (admin_utils.tests.UtilsTests)"]

**Base Commit**: 2e0f04507b17362239ba49830d26fec504d46978
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
