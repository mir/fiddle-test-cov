# django__django-15061

**Repository**: django/django
**Created**: 2021-11-04T17:15:53Z
**Version**: 4.1

## Problem Statement

Remove "for = ..." from MultiWidget's <label>.
Description
	
The instance from Raw MultiWidget class generate id_for_label like f'{id_}0'
It has not sense.
For example ChoiceWidget has self.add_id_index and I can decide it myself, how I will see label_id - with or without index.
I think, it is better to remove completely id_for_label method from MultiWidget Class.


## Hints

I agree that we should remove for from MultiWidget's <label> but not because "It has not sense" but to improve accessibility when using a screen reader, see also #32338. It should be enough to return an empty string: def id_for_label(self, id_): return ''
​PR

## Patch

```diff

diff --git a/django/forms/widgets.py b/django/forms/widgets.py
--- a/django/forms/widgets.py
+++ b/django/forms/widgets.py
@@ -849,9 +849,7 @@ def get_context(self, name, value, attrs):
         return context
 
     def id_for_label(self, id_):
-        if id_:
-            id_ += '_0'
-        return id_
+        return ''
 
     def value_from_datadict(self, data, files, name):
         return [


```

## Test Patch

```diff
diff --git a/tests/forms_tests/field_tests/test_multivaluefield.py b/tests/forms_tests/field_tests/test_multivaluefield.py
--- a/tests/forms_tests/field_tests/test_multivaluefield.py
+++ b/tests/forms_tests/field_tests/test_multivaluefield.py
@@ -141,7 +141,7 @@ def test_form_as_table(self):
         self.assertHTMLEqual(
             form.as_table(),
             """
-            <tr><th><label for="id_field1_0">Field1:</label></th>
+            <tr><th><label>Field1:</label></th>
             <td><input type="text" name="field1_0" id="id_field1_0" required>
             <select multiple name="field1_1" id="id_field1_1" required>
             <option value="J">John</option>
@@ -164,7 +164,7 @@ def test_form_as_table_data(self):
         self.assertHTMLEqual(
             form.as_table(),
             """
-            <tr><th><label for="id_field1_0">Field1:</label></th>
+            <tr><th><label>Field1:</label></th>
             <td><input type="text" name="field1_0" value="some text" id="id_field1_0" required>
             <select multiple name="field1_1" id="id_field1_1" required>
             <option value="J" selected>John</option>
diff --git a/tests/forms_tests/field_tests/test_splitdatetimefield.py b/tests/forms_tests/field_tests/test_splitdatetimefield.py
--- a/tests/forms_tests/field_tests/test_splitdatetimefield.py
+++ b/tests/forms_tests/field_tests/test_splitdatetimefield.py
@@ -1,7 +1,7 @@
 import datetime
 
 from django.core.exceptions import ValidationError
-from django.forms import SplitDateTimeField
+from django.forms import Form, SplitDateTimeField
 from django.forms.widgets import SplitDateTimeWidget
 from django.test import SimpleTestCase
 
@@ -60,3 +60,16 @@ def test_splitdatetimefield_changed(self):
         self.assertTrue(f.has_changed(datetime.datetime(2008, 5, 6, 12, 40, 00), ['2008-05-06', '12:40:00']))
         self.assertFalse(f.has_changed(datetime.datetime(2008, 5, 6, 12, 40, 00), ['06/05/2008', '12:40']))
         self.assertTrue(f.has_changed(datetime.datetime(2008, 5, 6, 12, 40, 00), ['06/05/2008', '12:41']))
+
+    def test_form_as_table(self):
+        class TestForm(Form):
+            datetime = SplitDateTimeField()
+
+        f = TestForm()
+        self.assertHTMLEqual(
+            f.as_table(),
+            '<tr><th><label>Datetime:</label></th><td>'
+            '<input type="text" name="datetime_0" required id="id_datetime_0">'
+            '<input type="text" name="datetime_1" required id="id_datetime_1">'
+            '</td></tr>',
+        )
diff --git a/tests/postgres_tests/test_ranges.py b/tests/postgres_tests/test_ranges.py
--- a/tests/postgres_tests/test_ranges.py
+++ b/tests/postgres_tests/test_ranges.py
@@ -665,7 +665,7 @@ class SplitForm(forms.Form):
         self.assertHTMLEqual(str(form), '''
             <tr>
                 <th>
-                <label for="id_field_0">Field:</label>
+                <label>Field:</label>
                 </th>
                 <td>
                     <input id="id_field_0_0" name="field_0_0" type="text">
@@ -700,7 +700,7 @@ class DateTimeRangeForm(forms.Form):
             form.as_table(),
             """
             <tr><th>
-            <label for="id_datetime_field_0">Datetime field:</label>
+            <label>Datetime field:</label>
             </th><td>
             <input type="text" name="datetime_field_0" id="id_datetime_field_0">
             <input type="text" name="datetime_field_1" id="id_datetime_field_1">
@@ -717,7 +717,7 @@ class DateTimeRangeForm(forms.Form):
             form.as_table(),
             """
             <tr><th>
-            <label for="id_datetime_field_0">Datetime field:</label>
+            <label>Datetime field:</label>
             </th><td>
             <input type="text" name="datetime_field_0"
             value="2010-01-01 11:13:00" id="id_datetime_field_0">
@@ -754,7 +754,7 @@ class RangeForm(forms.Form):
 
         self.assertHTMLEqual(str(RangeForm()), '''
         <tr>
-            <th><label for="id_ints_0">Ints:</label></th>
+            <th><label>Ints:</label></th>
             <td>
                 <input id="id_ints_0" name="ints_0" type="number">
                 <input id="id_ints_1" name="ints_1" type="number">

```

## Test Information

**Tests that should FAIL→PASS**: ["test_form_as_table (forms_tests.field_tests.test_multivaluefield.MultiValueFieldTest)", "test_form_as_table_data (forms_tests.field_tests.test_multivaluefield.MultiValueFieldTest)", "test_form_as_table (forms_tests.field_tests.test_splitdatetimefield.SplitDateTimeFieldTest)"]

**Tests that should PASS→PASS**: ["test_bad_choice (forms_tests.field_tests.test_multivaluefield.MultiValueFieldTest)", "test_clean (forms_tests.field_tests.test_multivaluefield.MultiValueFieldTest)", "test_clean_disabled_multivalue (forms_tests.field_tests.test_multivaluefield.MultiValueFieldTest)", "test_disabled_has_changed (forms_tests.field_tests.test_multivaluefield.MultiValueFieldTest)", "test_form_cleaned_data (forms_tests.field_tests.test_multivaluefield.MultiValueFieldTest)", "Test when the first widget's data has changed.", "Test when the last widget's data has changed. This ensures that it is", "test_has_changed_no_initial (forms_tests.field_tests.test_multivaluefield.MultiValueFieldTest)", "test_has_changed_same (forms_tests.field_tests.test_multivaluefield.MultiValueFieldTest)", "If insufficient data is provided, None is substituted.", "test_render_required_attributes (forms_tests.field_tests.test_multivaluefield.MultiValueFieldTest)", "test_splitdatetimefield_1 (forms_tests.field_tests.test_splitdatetimefield.SplitDateTimeFieldTest)", "test_splitdatetimefield_2 (forms_tests.field_tests.test_splitdatetimefield.SplitDateTimeFieldTest)", "test_splitdatetimefield_changed (forms_tests.field_tests.test_splitdatetimefield.SplitDateTimeFieldTest)"]

**Base Commit**: 2c01ebb4be5d53cbf6450f356c10e436025d6d07
**Environment Setup Commit**: 647480166bfe7532e8c471fef0146e3a17e6c0c9
