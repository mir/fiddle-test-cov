# django__django-11742

**Repository**: django/django
**Created**: 2019-09-04T08:30:14Z
**Version**: 3.0

## Problem Statement

Add check to ensure max_length fits longest choice.
Description
	
There is currently no check to ensure that Field.max_length is large enough to fit the longest value in Field.choices.
This would be very helpful as often this mistake is not noticed until an attempt is made to save a record with those values that are too long.


## Patch

```diff

diff --git a/django/db/models/fields/__init__.py b/django/db/models/fields/__init__.py
--- a/django/db/models/fields/__init__.py
+++ b/django/db/models/fields/__init__.py
@@ -257,6 +257,7 @@ def is_value(value, accept_promise=True):
                 )
             ]
 
+        choice_max_length = 0
         # Expect [group_name, [value, display]]
         for choices_group in self.choices:
             try:
@@ -270,16 +271,32 @@ def is_value(value, accept_promise=True):
                     for value, human_name in group_choices
                 ):
                     break
+                if self.max_length is not None and group_choices:
+                    choice_max_length = max(
+                        choice_max_length,
+                        *(len(value) for value, _ in group_choices if isinstance(value, str)),
+                    )
             except (TypeError, ValueError):
                 # No groups, choices in the form [value, display]
                 value, human_name = group_name, group_choices
                 if not is_value(value) or not is_value(human_name):
                     break
+                if self.max_length is not None and isinstance(value, str):
+                    choice_max_length = max(choice_max_length, len(value))
 
             # Special case: choices=['ab']
             if isinstance(choices_group, str):
                 break
         else:
+            if self.max_length is not None and choice_max_length > self.max_length:
+                return [
+                    checks.Error(
+                        "'max_length' is too small to fit the longest value "
+                        "in 'choices' (%d characters)." % choice_max_length,
+                        obj=self,
+                        id='fields.E009',
+                    ),
+                ]
             return []
 
         return [


```

## Test Patch

```diff
diff --git a/tests/invalid_models_tests/test_ordinary_fields.py b/tests/invalid_models_tests/test_ordinary_fields.py
--- a/tests/invalid_models_tests/test_ordinary_fields.py
+++ b/tests/invalid_models_tests/test_ordinary_fields.py
@@ -304,6 +304,32 @@ class Model(models.Model):
 
         self.assertEqual(Model._meta.get_field('field').check(), [])
 
+    def test_choices_in_max_length(self):
+        class Model(models.Model):
+            field = models.CharField(
+                max_length=2, choices=[
+                    ('ABC', 'Value Too Long!'), ('OK', 'Good')
+                ],
+            )
+            group = models.CharField(
+                max_length=2, choices=[
+                    ('Nested', [('OK', 'Good'), ('Longer', 'Longer')]),
+                    ('Grouped', [('Bad', 'Bad')]),
+                ],
+            )
+
+        for name, choice_max_length in (('field', 3), ('group', 6)):
+            with self.subTest(name):
+                field = Model._meta.get_field(name)
+                self.assertEqual(field.check(), [
+                    Error(
+                        "'max_length' is too small to fit the longest value "
+                        "in 'choices' (%d characters)." % choice_max_length,
+                        obj=field,
+                        id='fields.E009',
+                    ),
+                ])
+
     def test_bad_db_index_value(self):
         class Model(models.Model):
             field = models.CharField(max_length=10, db_index='bad')

```

## Test Information

**Tests that should FAIL→PASS**: ["test_choices_in_max_length (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_choices_named_group (invalid_models_tests.test_ordinary_fields.CharFieldTests)"]

**Tests that should PASS→PASS**: ["test_non_nullable_blank (invalid_models_tests.test_ordinary_fields.GenericIPAddressFieldTests)", "test_forbidden_files_and_folders (invalid_models_tests.test_ordinary_fields.FilePathFieldTests)", "test_max_length_warning (invalid_models_tests.test_ordinary_fields.IntegerFieldTests)", "test_primary_key (invalid_models_tests.test_ordinary_fields.FileFieldTests)", "test_upload_to_callable_not_checked (invalid_models_tests.test_ordinary_fields.FileFieldTests)", "test_upload_to_starts_with_slash (invalid_models_tests.test_ordinary_fields.FileFieldTests)", "test_valid_case (invalid_models_tests.test_ordinary_fields.FileFieldTests)", "test_valid_default_case (invalid_models_tests.test_ordinary_fields.FileFieldTests)", "test_str_default_value (invalid_models_tests.test_ordinary_fields.BinaryFieldTests)", "test_valid_default_value (invalid_models_tests.test_ordinary_fields.BinaryFieldTests)", "test_max_length_warning (invalid_models_tests.test_ordinary_fields.AutoFieldTests)", "test_primary_key (invalid_models_tests.test_ordinary_fields.AutoFieldTests)", "test_valid_case (invalid_models_tests.test_ordinary_fields.AutoFieldTests)", "test_fix_default_value (invalid_models_tests.test_ordinary_fields.DateTimeFieldTests)", "test_fix_default_value_tz (invalid_models_tests.test_ordinary_fields.DateTimeFieldTests)", "test_auto_now_and_auto_now_add_raise_error (invalid_models_tests.test_ordinary_fields.DateFieldTests)", "test_fix_default_value (invalid_models_tests.test_ordinary_fields.DateFieldTests)", "test_fix_default_value_tz (invalid_models_tests.test_ordinary_fields.DateFieldTests)", "test_fix_default_value (invalid_models_tests.test_ordinary_fields.TimeFieldTests)", "test_fix_default_value_tz (invalid_models_tests.test_ordinary_fields.TimeFieldTests)", "test_bad_values_of_max_digits_and_decimal_places (invalid_models_tests.test_ordinary_fields.DecimalFieldTests)", "test_decimal_places_greater_than_max_digits (invalid_models_tests.test_ordinary_fields.DecimalFieldTests)", "test_negative_max_digits_and_decimal_places (invalid_models_tests.test_ordinary_fields.DecimalFieldTests)", "test_required_attributes (invalid_models_tests.test_ordinary_fields.DecimalFieldTests)", "test_valid_field (invalid_models_tests.test_ordinary_fields.DecimalFieldTests)", "test_bad_db_index_value (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_bad_max_length_value (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_bad_validators (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_choices_containing_lazy (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_choices_containing_non_pairs (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_choices_named_group_bad_structure (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_choices_named_group_lazy (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_choices_named_group_non_pairs (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_iterable_of_iterable_choices (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_lazy_choices (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_missing_max_length (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_negative_max_length (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_non_iterable_choices (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "Two letters isn't a valid choice pair.", "test_str_max_length_type (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_str_max_length_value (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_valid_field (invalid_models_tests.test_ordinary_fields.CharFieldTests)", "test_pillow_installed (invalid_models_tests.test_ordinary_fields.ImageFieldTests)"]

**Base Commit**: fee75d2aed4e58ada6567c464cfd22e89dc65f4a
**Environment Setup Commit**: 419a78300f7cd27611196e1e464d50fd0385ff27
