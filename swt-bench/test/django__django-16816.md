# django__django-16816

**Repository**: django/django
**Created**: 2023-04-30T15:37:43Z
**Version**: 5.0

## Problem Statement

Error E108 does not cover some cases
Description
	 
		(last modified by Baha Sdtbekov)
	 
I have two models, Question and Choice. And if I write list_display = ["choice"] in QuestionAdmin, I get no errors.
But when I visit /admin/polls/question/, the following trace is returned:
Internal Server Error: /admin/polls/question/
Traceback (most recent call last):
 File "/some/path/django/contrib/admin/utils.py", line 334, in label_for_field
	field = _get_non_gfk_field(model._meta, name)
 File "/some/path/django/contrib/admin/utils.py", line 310, in _get_non_gfk_field
	raise FieldDoesNotExist()
django.core.exceptions.FieldDoesNotExist
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
 File "/some/path/django/core/handlers/exception.py", line 55, in inner
	response = get_response(request)
 File "/some/path/django/core/handlers/base.py", line 220, in _get_response
	response = response.render()
 File "/some/path/django/template/response.py", line 111, in render
	self.content = self.rendered_content
 File "/some/path/django/template/response.py", line 89, in rendered_content
	return template.render(context, self._request)
 File "/some/path/django/template/backends/django.py", line 61, in render
	return self.template.render(context)
 File "/some/path/django/template/base.py", line 175, in render
	return self._render(context)
 File "/some/path/django/template/base.py", line 167, in _render
	return self.nodelist.render(context)
 File "/some/path/django/template/base.py", line 1005, in render
	return SafeString("".join([node.render_annotated(context) for node in self]))
 File "/some/path/django/template/base.py", line 1005, in <listcomp>
	return SafeString("".join([node.render_annotated(context) for node in self]))
 File "/some/path/django/template/base.py", line 966, in render_annotated
	return self.render(context)
 File "/some/path/django/template/loader_tags.py", line 157, in render
	return compiled_parent._render(context)
 File "/some/path/django/template/base.py", line 167, in _render
	return self.nodelist.render(context)
 File "/some/path/django/template/base.py", line 1005, in render
	return SafeString("".join([node.render_annotated(context) for node in self]))
 File "/some/path/django/template/base.py", line 1005, in <listcomp>
	return SafeString("".join([node.render_annotated(context) for node in self]))
 File "/some/path/django/template/base.py", line 966, in render_annotated
	return self.render(context)
 File "/some/path/django/template/loader_tags.py", line 157, in render
	return compiled_parent._render(context)
 File "/some/path/django/template/base.py", line 167, in _render
	return self.nodelist.render(context)
 File "/some/path/django/template/base.py", line 1005, in render
	return SafeString("".join([node.render_annotated(context) for node in self]))
 File "/some/path/django/template/base.py", line 1005, in <listcomp>
	return SafeString("".join([node.render_annotated(context) for node in self]))
 File "/some/path/django/template/base.py", line 966, in render_annotated
	return self.render(context)
 File "/some/path/django/template/loader_tags.py", line 63, in render
	result = block.nodelist.render(context)
 File "/some/path/django/template/base.py", line 1005, in render
	return SafeString("".join([node.render_annotated(context) for node in self]))
 File "/some/path/django/template/base.py", line 1005, in <listcomp>
	return SafeString("".join([node.render_annotated(context) for node in self]))
 File "/some/path/django/template/base.py", line 966, in render_annotated
	return self.render(context)
 File "/some/path/django/template/loader_tags.py", line 63, in render
	result = block.nodelist.render(context)
 File "/some/path/django/template/base.py", line 1005, in render
	return SafeString("".join([node.render_annotated(context) for node in self]))
 File "/some/path/django/template/base.py", line 1005, in <listcomp>
	return SafeString("".join([node.render_annotated(context) for node in self]))
 File "/some/path/django/template/base.py", line 966, in render_annotated
	return self.render(context)
 File "/some/path/django/contrib/admin/templatetags/base.py", line 45, in render
	return super().render(context)
 File "/some/path/django/template/library.py", line 258, in render
	_dict = self.func(*resolved_args, **resolved_kwargs)
 File "/some/path/django/contrib/admin/templatetags/admin_list.py", line 326, in result_list
	headers = list(result_headers(cl))
 File "/some/path/django/contrib/admin/templatetags/admin_list.py", line 90, in result_headers
	text, attr = label_for_field(
 File "/some/path/django/contrib/admin/utils.py", line 362, in label_for_field
	raise AttributeError(message)
AttributeError: Unable to lookup 'choice' on Question or QuestionAdmin
[24/Apr/2023 15:43:32] "GET /admin/polls/question/ HTTP/1.1" 500 349913
I suggest that error E108 be updated to cover this case as well
For reproduce see ​github


## Hints

I think I will make a bug fix later if required
Thanks bakdolot 👍 There's a slight difference between a model instance's attributes and the model class' meta's fields. Meta stores the reverse relationship as choice, where as this would be setup & named according to whatever the related_name is declared as.
fyi potential quick fix, this will cause it to start raising E108 errors. this is just a demo of where to look. One possibility we could abandon using get_field() and refer to _meta.fields instead? 🤔… though that would mean the E109 check below this would no longer work. django/contrib/admin/checks.py a b from django.core.exceptions import FieldDoesNotExist 99from django.db import models 1010from django.db.models.constants import LOOKUP_SEP 1111from django.db.models.expressions import Combinable 12from django.db.models.fields.reverse_related import ManyToOneRel 1213from django.forms.models import BaseModelForm, BaseModelFormSet, _get_foreign_key 1314from django.template import engines 1415from django.template.backends.django import DjangoTemplates … … class ModelAdminChecks(BaseModelAdminChecks): 897898 return [] 898899 try: 899900 field = obj.model._meta.get_field(item) 901 if isinstance(field, ManyToOneRel): 902 raise FieldDoesNotExist 900903 except FieldDoesNotExist: 901904 try: 902905 field = getattr(obj.model, item)
This is related to the recent work merged for ticket:34481.
@nessita yup I recognised bakdolot's username from that patch :D
Oh no they recognized me :D I apologize very much. I noticed this bug only after merge when I decided to check again By the way, I also noticed two bugs related to this
I checked most of the fields and found these fields that are not working correctly class QuestionAdmin(admin.ModelAdmin): list_display = ["choice", "choice_set", "somem2m", "SomeM2M_question+", "somem2m_set", "__module__", "__doc__", "objects"] Also for reproduce see ​github
Replying to Baha Sdtbekov: I checked most of the fields and found these fields that are not working correctly class QuestionAdmin(admin.ModelAdmin): list_display = ["choice", "choice_set", "somem2m", "SomeM2M_question+", "somem2m_set", "__module__", "__doc__", "objects"] Also for reproduce see ​github System checks are helpers that in this case should highlight potentially reasonable but unsupported options. IMO they don't have to catch all obviously wrong values that you can find in __dir__.
Yup agreed with felixx if they're putting __doc__ in there then they probably need to go back and do a Python tutorial :) As for choice_set & somem2m – I thought that's what you fixed up in the other patch with E109.

## Patch

```diff

diff --git a/django/contrib/admin/checks.py b/django/contrib/admin/checks.py
--- a/django/contrib/admin/checks.py
+++ b/django/contrib/admin/checks.py
@@ -916,9 +916,10 @@ def _check_list_display_item(self, obj, item, label):
                         id="admin.E108",
                     )
                 ]
-        if isinstance(field, models.ManyToManyField) or (
-            getattr(field, "rel", None) and field.rel.field.many_to_one
-        ):
+        if (
+            getattr(field, "is_relation", False)
+            and (field.many_to_many or field.one_to_many)
+        ) or (getattr(field, "rel", None) and field.rel.field.many_to_one):
             return [
                 checks.Error(
                     f"The value of '{label}' must not be a many-to-many field or a "


```

## Test Patch

```diff
diff --git a/tests/modeladmin/test_checks.py b/tests/modeladmin/test_checks.py
--- a/tests/modeladmin/test_checks.py
+++ b/tests/modeladmin/test_checks.py
@@ -554,6 +554,30 @@ class TestModelAdmin(ModelAdmin):
             "admin.E109",
         )
 
+    def test_invalid_related_field(self):
+        class TestModelAdmin(ModelAdmin):
+            list_display = ["song"]
+
+        self.assertIsInvalid(
+            TestModelAdmin,
+            Band,
+            "The value of 'list_display[0]' must not be a many-to-many field or a "
+            "reverse foreign key.",
+            "admin.E109",
+        )
+
+    def test_invalid_m2m_related_name(self):
+        class TestModelAdmin(ModelAdmin):
+            list_display = ["featured"]
+
+        self.assertIsInvalid(
+            TestModelAdmin,
+            Band,
+            "The value of 'list_display[0]' must not be a many-to-many field or a "
+            "reverse foreign key.",
+            "admin.E109",
+        )
+
     def test_valid_case(self):
         @admin.display
         def a_callable(obj):

```

## Test Information

**Tests that should FAIL→PASS**: ["test_invalid_m2m_related_name (modeladmin.test_checks.ListDisplayTests.test_invalid_m2m_related_name)", "test_invalid_related_field (modeladmin.test_checks.ListDisplayTests.test_invalid_related_field)"]

**Tests that should PASS→PASS**: ["test_inline_without_formset_class (modeladmin.test_checks.FormsetCheckTests.test_inline_without_formset_class)", "test_invalid_type (modeladmin.test_checks.FormsetCheckTests.test_invalid_type)", "test_valid_case (modeladmin.test_checks.FormsetCheckTests.test_valid_case)", "test_invalid_type (modeladmin.test_checks.ListSelectRelatedCheckTests.test_invalid_type)", "test_valid_case (modeladmin.test_checks.ListSelectRelatedCheckTests.test_valid_case)", "test_not_boolean (modeladmin.test_checks.SaveAsCheckTests.test_not_boolean)", "test_valid_case (modeladmin.test_checks.SaveAsCheckTests.test_valid_case)", "test_not_integer (modeladmin.test_checks.MinNumCheckTests.test_not_integer)", "test_valid_case (modeladmin.test_checks.MinNumCheckTests.test_valid_case)", "test_not_integer (modeladmin.test_checks.ExtraCheckTests.test_not_integer)", "test_valid_case (modeladmin.test_checks.ExtraCheckTests.test_valid_case)", "test_not_integer (modeladmin.test_checks.ListMaxShowAllCheckTests.test_not_integer)", "test_valid_case (modeladmin.test_checks.ListMaxShowAllCheckTests.test_valid_case)", "test_invalid_expression (modeladmin.test_checks.OrderingCheckTests.test_invalid_expression)", "test_not_iterable (modeladmin.test_checks.OrderingCheckTests.test_not_iterable)", "test_random_marker_not_alone (modeladmin.test_checks.OrderingCheckTests.test_random_marker_not_alone)", "test_valid_case (modeladmin.test_checks.OrderingCheckTests.test_valid_case)", "test_valid_complex_case (modeladmin.test_checks.OrderingCheckTests.test_valid_complex_case)", "test_valid_expression (modeladmin.test_checks.OrderingCheckTests.test_valid_expression)", "test_valid_random_marker_case (modeladmin.test_checks.OrderingCheckTests.test_valid_random_marker_case)", "test_invalid_field_type (modeladmin.test_checks.ListDisplayTests.test_invalid_field_type)", "test_invalid_reverse_related_field (modeladmin.test_checks.ListDisplayTests.test_invalid_reverse_related_field)", "test_missing_field (modeladmin.test_checks.ListDisplayTests.test_missing_field)", "test_not_iterable (modeladmin.test_checks.ListDisplayTests.test_not_iterable)", "test_valid_case (modeladmin.test_checks.ListDisplayTests.test_valid_case)", "test_valid_field_accessible_via_instance (modeladmin.test_checks.ListDisplayTests.test_valid_field_accessible_via_instance)", "test_invalid_field_type (modeladmin.test_checks.FilterVerticalCheckTests.test_invalid_field_type)", "test_missing_field (modeladmin.test_checks.FilterVerticalCheckTests.test_missing_field)", "test_not_iterable (modeladmin.test_checks.FilterVerticalCheckTests.test_not_iterable)", "test_valid_case (modeladmin.test_checks.FilterVerticalCheckTests.test_valid_case)", "test_actions_not_unique (modeladmin.test_checks.ActionsCheckTests.test_actions_not_unique)", "test_actions_unique (modeladmin.test_checks.ActionsCheckTests.test_actions_unique)", "test_custom_permissions_require_matching_has_method (modeladmin.test_checks.ActionsCheckTests.test_custom_permissions_require_matching_has_method)", "test_duplicate_fields_in_fields (modeladmin.test_checks.FieldsCheckTests.test_duplicate_fields_in_fields)", "test_inline (modeladmin.test_checks.FieldsCheckTests.test_inline)", "test_fieldsets_with_custom_form_validation (modeladmin.test_checks.FormCheckTests.test_fieldsets_with_custom_form_validation)", "test_invalid_type (modeladmin.test_checks.FormCheckTests.test_invalid_type)", "test_valid_case (modeladmin.test_checks.FormCheckTests.test_valid_case)", "test_invalid_field_type (modeladmin.test_checks.FilterHorizontalCheckTests.test_invalid_field_type)", "test_missing_field (modeladmin.test_checks.FilterHorizontalCheckTests.test_missing_field)", "test_not_iterable (modeladmin.test_checks.FilterHorizontalCheckTests.test_not_iterable)", "test_valid_case (modeladmin.test_checks.FilterHorizontalCheckTests.test_valid_case)", "test_None_is_valid_case (modeladmin.test_checks.ListDisplayLinksCheckTests.test_None_is_valid_case)", "list_display_links is checked for list/tuple/None even if", "list_display_links check is skipped if get_list_display() is overridden.", "test_missing_field (modeladmin.test_checks.ListDisplayLinksCheckTests.test_missing_field)", "test_missing_in_list_display (modeladmin.test_checks.ListDisplayLinksCheckTests.test_missing_in_list_display)", "test_not_iterable (modeladmin.test_checks.ListDisplayLinksCheckTests.test_not_iterable)", "test_valid_case (modeladmin.test_checks.ListDisplayLinksCheckTests.test_valid_case)", "test_not_iterable (modeladmin.test_checks.SearchFieldsCheckTests.test_not_iterable)", "test_not_integer (modeladmin.test_checks.ListPerPageCheckTests.test_not_integer)", "test_valid_case (modeladmin.test_checks.ListPerPageCheckTests.test_valid_case)", "test_invalid_field_type (modeladmin.test_checks.DateHierarchyCheckTests.test_invalid_field_type)", "test_missing_field (modeladmin.test_checks.DateHierarchyCheckTests.test_missing_field)", "test_related_invalid_field_type (modeladmin.test_checks.DateHierarchyCheckTests.test_related_invalid_field_type)", "test_related_valid_case (modeladmin.test_checks.DateHierarchyCheckTests.test_related_valid_case)", "test_valid_case (modeladmin.test_checks.DateHierarchyCheckTests.test_valid_case)", "test_both_list_editable_and_list_display_links (modeladmin.test_checks.ListDisplayEditableTests.test_both_list_editable_and_list_display_links)", "The first item in list_display can be in list_editable as long as", "The first item in list_display cannot be in list_editable if", "The first item in list_display can be the same as the first in", "The first item in list_display cannot be the same as the first item", "list_display and list_editable can contain the same values", "test_not_boolean (modeladmin.test_checks.SaveOnTopCheckTests.test_not_boolean)", "test_valid_case (modeladmin.test_checks.SaveOnTopCheckTests.test_valid_case)", "test_autocomplete_e036 (modeladmin.test_checks.AutocompleteFieldsTests.test_autocomplete_e036)", "test_autocomplete_e037 (modeladmin.test_checks.AutocompleteFieldsTests.test_autocomplete_e037)", "test_autocomplete_e039 (modeladmin.test_checks.AutocompleteFieldsTests.test_autocomplete_e039)", "test_autocomplete_e040 (modeladmin.test_checks.AutocompleteFieldsTests.test_autocomplete_e040)", "test_autocomplete_e38 (modeladmin.test_checks.AutocompleteFieldsTests.test_autocomplete_e38)", "test_autocomplete_is_onetoone (modeladmin.test_checks.AutocompleteFieldsTests.test_autocomplete_is_onetoone)", "test_autocomplete_is_valid (modeladmin.test_checks.AutocompleteFieldsTests.test_autocomplete_is_valid)", "test_not_integer (modeladmin.test_checks.MaxNumCheckTests.test_not_integer)", "test_valid_case (modeladmin.test_checks.MaxNumCheckTests.test_valid_case)", "test_duplicate_fields (modeladmin.test_checks.FieldsetsCheckTests.test_duplicate_fields)", "test_duplicate_fields_in_fieldsets (modeladmin.test_checks.FieldsetsCheckTests.test_duplicate_fields_in_fieldsets)", "test_fieldsets_with_custom_form_validation (modeladmin.test_checks.FieldsetsCheckTests.test_fieldsets_with_custom_form_validation)", "test_item_not_a_pair (modeladmin.test_checks.FieldsetsCheckTests.test_item_not_a_pair)", "test_missing_fields_key (modeladmin.test_checks.FieldsetsCheckTests.test_missing_fields_key)", "test_non_iterable_item (modeladmin.test_checks.FieldsetsCheckTests.test_non_iterable_item)", "test_not_iterable (modeladmin.test_checks.FieldsetsCheckTests.test_not_iterable)", "test_second_element_of_item_not_a_dict (modeladmin.test_checks.FieldsetsCheckTests.test_second_element_of_item_not_a_dict)", "test_specified_both_fields_and_fieldsets (modeladmin.test_checks.FieldsetsCheckTests.test_specified_both_fields_and_fieldsets)", "test_valid_case (modeladmin.test_checks.FieldsetsCheckTests.test_valid_case)", "test_field_attname (modeladmin.test_checks.RawIdCheckTests.test_field_attname)", "test_invalid_field_type (modeladmin.test_checks.RawIdCheckTests.test_invalid_field_type)", "test_missing_field (modeladmin.test_checks.RawIdCheckTests.test_missing_field)", "test_not_iterable (modeladmin.test_checks.RawIdCheckTests.test_not_iterable)", "test_valid_case (modeladmin.test_checks.RawIdCheckTests.test_valid_case)", "test_invalid_field_type (modeladmin.test_checks.RadioFieldsCheckTests.test_invalid_field_type)", "test_invalid_value (modeladmin.test_checks.RadioFieldsCheckTests.test_invalid_value)", "test_missing_field (modeladmin.test_checks.RadioFieldsCheckTests.test_missing_field)", "test_not_dictionary (modeladmin.test_checks.RadioFieldsCheckTests.test_not_dictionary)", "test_valid_case (modeladmin.test_checks.RadioFieldsCheckTests.test_valid_case)", "test_missing_field (modeladmin.test_checks.FkNameCheckTests.test_missing_field)", "test_proxy_model_parent (modeladmin.test_checks.FkNameCheckTests.test_proxy_model_parent)", "test_valid_case (modeladmin.test_checks.FkNameCheckTests.test_valid_case)", "test_invalid_field_type (modeladmin.test_checks.PrepopulatedFieldsCheckTests.test_invalid_field_type)", "test_missing_field (modeladmin.test_checks.PrepopulatedFieldsCheckTests.test_missing_field)", "test_missing_field_again (modeladmin.test_checks.PrepopulatedFieldsCheckTests.test_missing_field_again)", "test_not_dictionary (modeladmin.test_checks.PrepopulatedFieldsCheckTests.test_not_dictionary)", "test_not_list_or_tuple (modeladmin.test_checks.PrepopulatedFieldsCheckTests.test_not_list_or_tuple)", "test_one_to_one_field (modeladmin.test_checks.PrepopulatedFieldsCheckTests.test_one_to_one_field)", "test_valid_case (modeladmin.test_checks.PrepopulatedFieldsCheckTests.test_valid_case)", "test_invalid_callable (modeladmin.test_checks.InlinesCheckTests.test_invalid_callable)", "test_invalid_model (modeladmin.test_checks.InlinesCheckTests.test_invalid_model)", "test_invalid_model_type (modeladmin.test_checks.InlinesCheckTests.test_invalid_model_type)", "test_missing_model_field (modeladmin.test_checks.InlinesCheckTests.test_missing_model_field)", "test_not_correct_inline_field (modeladmin.test_checks.InlinesCheckTests.test_not_correct_inline_field)", "test_not_iterable (modeladmin.test_checks.InlinesCheckTests.test_not_iterable)", "test_not_model_admin (modeladmin.test_checks.InlinesCheckTests.test_not_model_admin)", "test_valid_case (modeladmin.test_checks.InlinesCheckTests.test_valid_case)", "test_callable (modeladmin.test_checks.ListFilterTests.test_callable)", "test_list_filter_is_func (modeladmin.test_checks.ListFilterTests.test_list_filter_is_func)", "test_list_filter_validation (modeladmin.test_checks.ListFilterTests.test_list_filter_validation)", "test_missing_field (modeladmin.test_checks.ListFilterTests.test_missing_field)", "test_not_associated_with_field_name (modeladmin.test_checks.ListFilterTests.test_not_associated_with_field_name)", "test_not_callable (modeladmin.test_checks.ListFilterTests.test_not_callable)", "test_not_filter (modeladmin.test_checks.ListFilterTests.test_not_filter)", "test_not_filter_again (modeladmin.test_checks.ListFilterTests.test_not_filter_again)", "test_not_filter_again_again (modeladmin.test_checks.ListFilterTests.test_not_filter_again_again)", "test_not_list_filter_class (modeladmin.test_checks.ListFilterTests.test_not_list_filter_class)", "test_valid_case (modeladmin.test_checks.ListFilterTests.test_valid_case)"]

**Base Commit**: 191f6a9a4586b5e5f79f4f42f190e7ad4bbacc84
**Environment Setup Commit**: 4a72da71001f154ea60906a2f74898d32b7322a7
