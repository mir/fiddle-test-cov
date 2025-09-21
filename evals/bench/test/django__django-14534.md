# django__django-14534

**Repository**: django/django
**Created**: 2021-06-17T15:37:34Z
**Version**: 4.0

## Problem Statement

BoundWidget.id_for_label ignores id set by ChoiceWidget.options
Description
	
If you look at the implementation of BoundField.subwidgets
class BoundField:
	...
	def subwidgets(self):
		id_ = self.field.widget.attrs.get('id') or self.auto_id
		attrs = {'id': id_} if id_ else {}
		attrs = self.build_widget_attrs(attrs)
		return [
			BoundWidget(self.field.widget, widget, self.form.renderer)
			for widget in self.field.widget.subwidgets(self.html_name, self.value(), attrs=attrs)
		]
one sees that self.field.widget.subwidgets(self.html_name, self.value(), attrs=attrs) returns a dict and assigns it to widget. Now widget['attrs']['id'] contains the "id" we would like to use when rendering the label of our CheckboxSelectMultiple.
However BoundWidget.id_for_label() is implemented as
class BoundWidget:
	...
	def id_for_label(self):
		return 'id_%s_%s' % (self.data['name'], self.data['index'])
ignoring the id available through self.data['attrs']['id']. This re-implementation for rendering the "id" is confusing and presumably not intended. Nobody has probably realized that so far, because rarely the auto_id-argument is overridden when initializing a form. If however we do, one would assume that the method BoundWidget.id_for_label renders that string as specified through the auto_id format-string.
By changing the code from above to
class BoundWidget:
	...
	def id_for_label(self):
		return self.data['attrs']['id']
that function behaves as expected.
Please note that this error only occurs when rendering the subwidgets of a widget of type CheckboxSelectMultiple. This has nothing to do with the method BoundField.id_for_label().


## Hints

Hey Jacob — Sounds right: I didn't look in-depth but, if you can put your example in a test case it will be clear enough in the PR. Thanks.
Thanks Carlton, I will create a pull request asap.
Here is a pull request fixing this bug: ​https://github.com/django/django/pull/14533 (closed without merging)
Here is the new pull request ​https://github.com/django/django/pull/14534 against main
The regression test looks good; fails before fix, passes afterward. I don't think this one ​qualifies for a backport, so I'm changing it to "Ready for checkin." Do the commits need to be squashed?

## Patch

```diff

diff --git a/django/forms/boundfield.py b/django/forms/boundfield.py
--- a/django/forms/boundfield.py
+++ b/django/forms/boundfield.py
@@ -277,7 +277,7 @@ def template_name(self):
 
     @property
     def id_for_label(self):
-        return 'id_%s_%s' % (self.data['name'], self.data['index'])
+        return self.data['attrs'].get('id')
 
     @property
     def choice_label(self):


```

## Test Patch

```diff
diff --git a/tests/forms_tests/tests/test_forms.py b/tests/forms_tests/tests/test_forms.py
--- a/tests/forms_tests/tests/test_forms.py
+++ b/tests/forms_tests/tests/test_forms.py
@@ -720,7 +720,7 @@ class BeatleForm(Form):
         fields = list(BeatleForm(auto_id=False)['name'])
         self.assertEqual(len(fields), 4)
 
-        self.assertEqual(fields[0].id_for_label, 'id_name_0')
+        self.assertEqual(fields[0].id_for_label, None)
         self.assertEqual(fields[0].choice_label, 'John')
         self.assertHTMLEqual(fields[0].tag(), '<option value="john">John</option>')
         self.assertHTMLEqual(str(fields[0]), '<option value="john">John</option>')
@@ -3202,6 +3202,22 @@ class SomeForm(Form):
         self.assertEqual(form['field'].id_for_label, 'myCustomID')
         self.assertEqual(form['field_none'].id_for_label, 'id_field_none')
 
+    def test_boundfield_subwidget_id_for_label(self):
+        """
+        If auto_id is provided when initializing the form, the generated ID in
+        subwidgets must reflect that prefix.
+        """
+        class SomeForm(Form):
+            field = MultipleChoiceField(
+                choices=[('a', 'A'), ('b', 'B')],
+                widget=CheckboxSelectMultiple,
+            )
+
+        form = SomeForm(auto_id='prefix_%s')
+        subwidgets = form['field'].subwidgets
+        self.assertEqual(subwidgets[0].id_for_label, 'prefix_field_0')
+        self.assertEqual(subwidgets[1].id_for_label, 'prefix_field_1')
+
     def test_boundfield_widget_type(self):
         class SomeForm(Form):
             first_name = CharField()

```

## Test Information

**Tests that should FAIL→PASS**: ["If auto_id is provided when initializing the form, the generated ID in", "test_iterable_boundfield_select (forms_tests.tests.test_forms.FormsTestCase)"]

**Tests that should PASS→PASS**: ["test_attribute_class (forms_tests.tests.test_forms.RendererTests)", "test_attribute_instance (forms_tests.tests.test_forms.RendererTests)", "test_attribute_override (forms_tests.tests.test_forms.RendererTests)", "test_default (forms_tests.tests.test_forms.RendererTests)", "test_kwarg_class (forms_tests.tests.test_forms.RendererTests)", "test_kwarg_instance (forms_tests.tests.test_forms.RendererTests)", "test_accessing_clean (forms_tests.tests.test_forms.FormsTestCase)", "test_auto_id (forms_tests.tests.test_forms.FormsTestCase)", "test_auto_id_false (forms_tests.tests.test_forms.FormsTestCase)", "test_auto_id_on_form_and_field (forms_tests.tests.test_forms.FormsTestCase)", "test_auto_id_true (forms_tests.tests.test_forms.FormsTestCase)", "BaseForm.__repr__() should contain some basic information about the", "BaseForm.__repr__() shouldn't trigger the form validation.", "test_basic_processing_in_view (forms_tests.tests.test_forms.FormsTestCase)", "BoundField without any choices (subwidgets) evaluates to True.", "test_boundfield_css_classes (forms_tests.tests.test_forms.FormsTestCase)", "test_boundfield_empty_label (forms_tests.tests.test_forms.FormsTestCase)", "test_boundfield_id_for_label (forms_tests.tests.test_forms.FormsTestCase)", "If an id is provided in `Widget.attrs`, it overrides the generated ID,", "Multiple calls to BoundField().value() in an unbound form should return", "test_boundfield_invalid_index (forms_tests.tests.test_forms.FormsTestCase)", "test_boundfield_label_tag (forms_tests.tests.test_forms.FormsTestCase)", "test_boundfield_label_tag_custom_widget_id_for_label (forms_tests.tests.test_forms.FormsTestCase)", "If a widget has no id, label_tag just returns the text with no", "test_boundfield_slice (forms_tests.tests.test_forms.FormsTestCase)", "test_boundfield_value_disabled_callable_initial (forms_tests.tests.test_forms.FormsTestCase)", "test_boundfield_values (forms_tests.tests.test_forms.FormsTestCase)", "test_boundfield_widget_type (forms_tests.tests.test_forms.FormsTestCase)", "test_callable_initial_data (forms_tests.tests.test_forms.FormsTestCase)", "test_changed_data (forms_tests.tests.test_forms.FormsTestCase)", "test_changing_cleaned_data_in_clean (forms_tests.tests.test_forms.FormsTestCase)", "test_changing_cleaned_data_nothing_returned (forms_tests.tests.test_forms.FormsTestCase)", "test_checkbox_auto_id (forms_tests.tests.test_forms.FormsTestCase)", "test_class_prefix (forms_tests.tests.test_forms.FormsTestCase)", "test_cleaned_data_only_fields (forms_tests.tests.test_forms.FormsTestCase)", "test_custom_boundfield (forms_tests.tests.test_forms.FormsTestCase)", "Form fields can customize what is considered as an empty value", "test_datetime_changed_data_callable_with_microseconds (forms_tests.tests.test_forms.FormsTestCase)", "The cleaned value for a form with a disabled DateTimeField and callable", "Cleaning a form with a disabled DateTimeField and callable initial", "test_dynamic_construction (forms_tests.tests.test_forms.FormsTestCase)", "test_dynamic_initial_data (forms_tests.tests.test_forms.FormsTestCase)", "test_empty_data_files_multi_value_dict (forms_tests.tests.test_forms.FormsTestCase)", "test_empty_dict (forms_tests.tests.test_forms.FormsTestCase)", "test_empty_permitted (forms_tests.tests.test_forms.FormsTestCase)", "test_empty_permitted_and_use_required_attribute (forms_tests.tests.test_forms.FormsTestCase)", "test_empty_querydict_args (forms_tests.tests.test_forms.FormsTestCase)", "test_error_dict (forms_tests.tests.test_forms.FormsTestCase)", "#21962 - adding html escape flag to ErrorDict", "test_error_escaping (forms_tests.tests.test_forms.FormsTestCase)", "test_error_html_required_html_classes (forms_tests.tests.test_forms.FormsTestCase)", "test_error_list (forms_tests.tests.test_forms.FormsTestCase)", "test_error_list_class_has_one_class_specified (forms_tests.tests.test_forms.FormsTestCase)", "test_error_list_class_not_specified (forms_tests.tests.test_forms.FormsTestCase)", "test_error_list_with_hidden_field_errors_has_correct_class (forms_tests.tests.test_forms.FormsTestCase)", "test_error_list_with_non_field_errors_has_correct_class (forms_tests.tests.test_forms.FormsTestCase)", "test_errorlist_override (forms_tests.tests.test_forms.FormsTestCase)", "test_escaping (forms_tests.tests.test_forms.FormsTestCase)", "test_explicit_field_order (forms_tests.tests.test_forms.FormsTestCase)", "test_extracting_hidden_and_visible (forms_tests.tests.test_forms.FormsTestCase)", "test_field_deep_copy_error_messages (forms_tests.tests.test_forms.FormsTestCase)", "#5749 - `field_name` may be used as a key in _html_output().", "BaseForm._html_output() should merge all the hidden input fields and", "test_field_named_data (forms_tests.tests.test_forms.FormsTestCase)", "test_field_order (forms_tests.tests.test_forms.FormsTestCase)", "`css_classes` may be used as a key in _html_output() (class comes", "`css_classes` may be used as a key in _html_output() (empty classes).", "test_filefield_initial_callable (forms_tests.tests.test_forms.FormsTestCase)", "test_filefield_with_fileinput_required (forms_tests.tests.test_forms.FormsTestCase)", "test_form (forms_tests.tests.test_forms.FormsTestCase)", "test_form_html_attributes (forms_tests.tests.test_forms.FormsTestCase)", "test_form_with_disabled_fields (forms_tests.tests.test_forms.FormsTestCase)", "test_form_with_iterable_boundfield (forms_tests.tests.test_forms.FormsTestCase)", "test_form_with_iterable_boundfield_id (forms_tests.tests.test_forms.FormsTestCase)", "test_form_with_noniterable_boundfield (forms_tests.tests.test_forms.FormsTestCase)", "test_forms_with_choices (forms_tests.tests.test_forms.FormsTestCase)", "test_forms_with_file_fields (forms_tests.tests.test_forms.FormsTestCase)", "test_forms_with_multiple_choice (forms_tests.tests.test_forms.FormsTestCase)", "test_forms_with_null_boolean (forms_tests.tests.test_forms.FormsTestCase)", "test_forms_with_prefixes (forms_tests.tests.test_forms.FormsTestCase)", "test_forms_with_radio (forms_tests.tests.test_forms.FormsTestCase)", "test_get_initial_for_field (forms_tests.tests.test_forms.FormsTestCase)", "test_has_error (forms_tests.tests.test_forms.FormsTestCase)", "test_help_text (forms_tests.tests.test_forms.FormsTestCase)", "test_hidden_data (forms_tests.tests.test_forms.FormsTestCase)", "test_hidden_initial_gets_id (forms_tests.tests.test_forms.FormsTestCase)", "test_hidden_widget (forms_tests.tests.test_forms.FormsTestCase)", "test_html_output_with_hidden_input_field_errors (forms_tests.tests.test_forms.FormsTestCase)", "test_html_safe (forms_tests.tests.test_forms.FormsTestCase)", "test_id_on_field (forms_tests.tests.test_forms.FormsTestCase)", "test_initial_data (forms_tests.tests.test_forms.FormsTestCase)", "test_initial_datetime_values (forms_tests.tests.test_forms.FormsTestCase)", "#17922 - required_css_class is added to the label_tag() of required fields.", "test_label_split_datetime_not_displayed (forms_tests.tests.test_forms.FormsTestCase)", "test_label_suffix (forms_tests.tests.test_forms.FormsTestCase)", "BoundField label_suffix (if provided) overrides Form label_suffix", "test_multipart_encoded_form (forms_tests.tests.test_forms.FormsTestCase)", "test_multiple_choice_checkbox (forms_tests.tests.test_forms.FormsTestCase)", "test_multiple_choice_list_data (forms_tests.tests.test_forms.FormsTestCase)", "test_multiple_hidden (forms_tests.tests.test_forms.FormsTestCase)", "#19298 -- MultiValueField needs to override the default as it needs", "test_multivalue_field_validation (forms_tests.tests.test_forms.FormsTestCase)", "#23674 -- invalid initial data should not break form.changed_data()", "test_multivalue_optional_subfields (forms_tests.tests.test_forms.FormsTestCase)", "test_only_hidden_fields (forms_tests.tests.test_forms.FormsTestCase)", "test_optional_data (forms_tests.tests.test_forms.FormsTestCase)", "test_specifying_labels (forms_tests.tests.test_forms.FormsTestCase)", "test_subclassing_forms (forms_tests.tests.test_forms.FormsTestCase)", "test_templates_with_forms (forms_tests.tests.test_forms.FormsTestCase)", "test_unbound_form (forms_tests.tests.test_forms.FormsTestCase)", "test_unicode_values (forms_tests.tests.test_forms.FormsTestCase)", "test_update_error_dict (forms_tests.tests.test_forms.FormsTestCase)", "test_use_required_attribute_false (forms_tests.tests.test_forms.FormsTestCase)", "test_use_required_attribute_true (forms_tests.tests.test_forms.FormsTestCase)", "test_validating_multiple_fields (forms_tests.tests.test_forms.FormsTestCase)", "The list of form field validators can be modified without polluting", "test_various_boolean_values (forms_tests.tests.test_forms.FormsTestCase)", "test_widget_output (forms_tests.tests.test_forms.FormsTestCase)"]

**Base Commit**: 910ecd1b8df7678f45c3d507dde6bcb1faafa243
**Environment Setup Commit**: 475cffd1d64c690cdad16ede4d5e81985738ceb4
