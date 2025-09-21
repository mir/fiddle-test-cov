# django__django-14915

**Repository**: django/django
**Created**: 2021-09-29T22:00:15Z
**Version**: 4.1

## Problem Statement

ModelChoiceIteratorValue is not hashable.
Description
	
Recently I migrated from Django 3.0 to Django 3.1. In my code, I add custom data-* attributes to the select widget options. After the upgrade some of those options broke. Error is {TypeError}unhashable type: 'ModelChoiceIteratorValue'.
Example (this one breaks):
	def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
		context = super().create_option(name, value, label, selected, index, subindex, attrs)
		if not value:
			return context
		if value in self.show_fields: # This is a dict {1: ['first_name', 'last_name']}
			context['attrs']['data-fields'] = json.dumps(self.show_fields[value])
However, working with arrays is not an issue:
	def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
		context = super().create_option(name, value, label, selected, index, subindex, attrs)
		if not value:
			return context
		if value in allowed_values: # This is an array [1, 2]
			...


## Hints

Thanks for the ticket. Agreed, we could make ModelChoiceIteratorValue hashable by adding: def __hash__(self): return hash(self.value) For now you can use value.value as ​documented in the "Backwards incompatible changes in 3.1" section. Would you like to prepare a patch?
Replying to Mariusz Felisiak: Thanks for the ticket. Agreed, we could make ModelChoiceIteratorValue hashable by adding: def __hash__(self): return hash(self.value) For now you can use value.value as ​documented in the "Backwards incompatible changes in 3.1" section. Would you like to prepare a patch? Yes, sure.
Patch: ​https://github.com/django/django/pull/14915

## Patch

```diff

diff --git a/django/forms/models.py b/django/forms/models.py
--- a/django/forms/models.py
+++ b/django/forms/models.py
@@ -1166,6 +1166,9 @@ def __init__(self, value, instance):
     def __str__(self):
         return str(self.value)
 
+    def __hash__(self):
+        return hash(self.value)
+
     def __eq__(self, other):
         if isinstance(other, ModelChoiceIteratorValue):
             other = other.value


```

## Test Patch

```diff
diff --git a/tests/model_forms/test_modelchoicefield.py b/tests/model_forms/test_modelchoicefield.py
--- a/tests/model_forms/test_modelchoicefield.py
+++ b/tests/model_forms/test_modelchoicefield.py
@@ -2,7 +2,7 @@
 
 from django import forms
 from django.core.exceptions import ValidationError
-from django.forms.models import ModelChoiceIterator
+from django.forms.models import ModelChoiceIterator, ModelChoiceIteratorValue
 from django.forms.widgets import CheckboxSelectMultiple
 from django.template import Context, Template
 from django.test import TestCase
@@ -341,6 +341,12 @@ class CustomModelMultipleChoiceField(forms.ModelMultipleChoiceField):
 </div>""" % (self.c1.pk, self.c2.pk, self.c3.pk),
         )
 
+    def test_choice_value_hash(self):
+        value_1 = ModelChoiceIteratorValue(self.c1.pk, self.c1)
+        value_2 = ModelChoiceIteratorValue(self.c2.pk, self.c2)
+        self.assertEqual(hash(value_1), hash(ModelChoiceIteratorValue(self.c1.pk, None)))
+        self.assertNotEqual(hash(value_1), hash(value_2))
+
     def test_choices_not_fetched_when_not_rendering(self):
         with self.assertNumQueries(1):
             field = forms.ModelChoiceField(Category.objects.order_by('-name'))

```

## Test Information

**Tests that should FAIL→PASS**: ["test_choice_value_hash (model_forms.test_modelchoicefield.ModelChoiceFieldTests)"]

**Tests that should PASS→PASS**: ["test_basics (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_choice_iterator_passes_model_to_widget (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_choices (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_choices_bool (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_choices_bool_empty_label (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_choices_freshness (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_choices_not_fetched_when_not_rendering (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_choices_radio_blank (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_clean_model_instance (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_clean_to_field_name (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_custom_choice_iterator_passes_model_to_widget (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_deepcopies_widget (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_disabled_modelchoicefield (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_disabled_modelchoicefield_has_changed (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_disabled_modelchoicefield_initial_model_instance (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_disabled_modelmultiplechoicefield_has_changed (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_disabled_multiplemodelchoicefield (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "ModelChoiceField with RadioSelect widget doesn't produce unnecessary", "Widgets that render multiple subwidgets shouldn't make more than one", "Iterator defaults to ModelChoiceIterator and can be overridden with", "test_queryset_manager (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_queryset_none (model_forms.test_modelchoicefield.ModelChoiceFieldTests)", "test_result_cache_not_shared (model_forms.test_modelchoicefield.ModelChoiceFieldTests)"]

**Base Commit**: 903aaa35e5ceaa33bfc9b19b7f6da65ce5a91dd4
**Environment Setup Commit**: 647480166bfe7532e8c471fef0146e3a17e6c0c9
