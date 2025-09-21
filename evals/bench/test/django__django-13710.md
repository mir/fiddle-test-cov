# django__django-13710

**Repository**: django/django
**Created**: 2020-11-23T04:39:05Z
**Version**: 4.0

## Problem Statement

Use Admin Inline verbose_name as default for Inline verbose_name_plural
Description
	
Django allows specification of a verbose_name and a verbose_name_plural for Inline classes in admin views. However, verbose_name_plural for an Inline is not currently based on a specified verbose_name. Instead, it continues to be based on the model name, or an a verbose_name specified in the model's Meta class. This was confusing to me initially (I didn't understand why I had to specify both name forms for an Inline if I wanted to overrule the default name), and seems inconsistent with the approach for a model's Meta class (which does automatically base the plural form on a specified verbose_name). I propose that verbose_name_plural for an Inline class should by default be based on the verbose_name for an Inline if that is specified.
I have written a patch to implement this, including tests. Would be happy to submit that.


## Hints

Please push your patch as a ​Django pull request.

## Patch

```diff

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -2037,10 +2037,13 @@ def __init__(self, parent_model, admin_site):
         self.opts = self.model._meta
         self.has_registered_model = admin_site.is_registered(self.model)
         super().__init__()
+        if self.verbose_name_plural is None:
+            if self.verbose_name is None:
+                self.verbose_name_plural = self.model._meta.verbose_name_plural
+            else:
+                self.verbose_name_plural = format_lazy('{}s', self.verbose_name)
         if self.verbose_name is None:
             self.verbose_name = self.model._meta.verbose_name
-        if self.verbose_name_plural is None:
-            self.verbose_name_plural = self.model._meta.verbose_name_plural
 
     @property
     def media(self):


```

## Test Patch

```diff
diff --git a/tests/admin_inlines/tests.py b/tests/admin_inlines/tests.py
--- a/tests/admin_inlines/tests.py
+++ b/tests/admin_inlines/tests.py
@@ -967,6 +967,55 @@ def test_extra_inlines_are_not_shown(self):
 class TestVerboseNameInlineForms(TestDataMixin, TestCase):
     factory = RequestFactory()
 
+    def test_verbose_name_inline(self):
+        class NonVerboseProfileInline(TabularInline):
+            model = Profile
+            verbose_name = 'Non-verbose childs'
+
+        class VerboseNameProfileInline(TabularInline):
+            model = VerboseNameProfile
+            verbose_name = 'Childs with verbose name'
+
+        class VerboseNamePluralProfileInline(TabularInline):
+            model = VerboseNamePluralProfile
+            verbose_name = 'Childs with verbose name plural'
+
+        class BothVerboseNameProfileInline(TabularInline):
+            model = BothVerboseNameProfile
+            verbose_name = 'Childs with both verbose names'
+
+        modeladmin = ModelAdmin(ProfileCollection, admin_site)
+        modeladmin.inlines = [
+            NonVerboseProfileInline,
+            VerboseNameProfileInline,
+            VerboseNamePluralProfileInline,
+            BothVerboseNameProfileInline,
+        ]
+        obj = ProfileCollection.objects.create()
+        url = reverse('admin:admin_inlines_profilecollection_change', args=(obj.pk,))
+        request = self.factory.get(url)
+        request.user = self.superuser
+        response = modeladmin.changeform_view(request)
+        self.assertNotContains(response, 'Add another Profile')
+        # Non-verbose model.
+        self.assertContains(response, '<h2>Non-verbose childss</h2>')
+        self.assertContains(response, 'Add another Non-verbose child')
+        self.assertNotContains(response, '<h2>Profiles</h2>')
+        # Model with verbose name.
+        self.assertContains(response, '<h2>Childs with verbose names</h2>')
+        self.assertContains(response, 'Add another Childs with verbose name')
+        self.assertNotContains(response, '<h2>Model with verbose name onlys</h2>')
+        self.assertNotContains(response, 'Add another Model with verbose name only')
+        # Model with verbose name plural.
+        self.assertContains(response, '<h2>Childs with verbose name plurals</h2>')
+        self.assertContains(response, 'Add another Childs with verbose name plural')
+        self.assertNotContains(response, '<h2>Model with verbose name plural only</h2>')
+        # Model with both verbose names.
+        self.assertContains(response, '<h2>Childs with both verbose namess</h2>')
+        self.assertContains(response, 'Add another Childs with both verbose names')
+        self.assertNotContains(response, '<h2>Model with both - plural name</h2>')
+        self.assertNotContains(response, 'Add another Model with both - name')
+
     def test_verbose_name_plural_inline(self):
         class NonVerboseProfileInline(TabularInline):
             model = Profile

```

## Test Information

**Tests that should FAIL→PASS**: ["test_verbose_name_inline (admin_inlines.tests.TestVerboseNameInlineForms)"]

**Tests that should PASS→PASS**: ["Regression for #9362", "test_deleting_inline_with_protected_delete_does_not_validate (admin_inlines.tests.TestInlineProtectedOnDelete)", "test_all_inline_media (admin_inlines.tests.TestInlineMedia)", "test_inline_media_only_base (admin_inlines.tests.TestInlineMedia)", "test_inline_media_only_inline (admin_inlines.tests.TestInlineMedia)", "test_both_verbose_names_inline (admin_inlines.tests.TestVerboseNameInlineForms)", "test_verbose_name_plural_inline (admin_inlines.tests.TestVerboseNameInlineForms)", "test_add_url_not_allowed (admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions)", "test_extra_inlines_are_not_shown (admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions)", "test_get_to_change_url_is_allowed (admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions)", "test_inline_delete_buttons_are_not_shown (admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions)", "test_inlines_are_rendered_as_read_only (admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions)", "test_main_model_is_rendered_as_read_only (admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions)", "test_post_to_change_url_not_allowed (admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions)", "test_submit_line_shows_only_close_button (admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions)", "test_inline_add_fk_add_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_add_fk_noperm (admin_inlines.tests.TestInlinePermissions)", "test_inline_add_m2m_add_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_add_m2m_noperm (admin_inlines.tests.TestInlinePermissions)", "test_inline_add_m2m_view_only_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_fk_add_change_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_fk_add_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_fk_all_perms (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_fk_change_del_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_fk_change_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_fk_noperm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_m2m_add_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_m2m_change_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_m2m_noperm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_m2m_view_only_perm (admin_inlines.tests.TestInlinePermissions)", "Admin inline should invoke local callable when its name is listed in readonly_fields", "can_delete should be passed to inlineformset factory.", "An object can be created with inlines when it inherits another class.", "test_custom_form_tabular_inline_extra_field_label (admin_inlines.tests.TestInline)", "A model form with a form field specified (TitleForm.title1) should have", "SomeChildModelForm.__init__() overrides the label of a form field.", "test_custom_get_extra_form (admin_inlines.tests.TestInline)", "test_custom_min_num (admin_inlines.tests.TestInline)", "The \"View on Site\" link is correct for models with a custom primary key", "The inlines' model field help texts are displayed when using both the", "test_inline_editable_pk (admin_inlines.tests.TestInline)", "#18263 -- Make sure hidden fields don't get a column in tabular inlines", "test_inline_nonauto_noneditable_inherited_pk (admin_inlines.tests.TestInline)", "test_inline_nonauto_noneditable_pk (admin_inlines.tests.TestInline)", "test_inline_primary (admin_inlines.tests.TestInline)", "test_inlines_plural_heading_foreign_key (admin_inlines.tests.TestInline)", "Inlines `show_change_link` for registered models when enabled.", "Inlines `show_change_link` disabled for unregistered models.", "test_inlines_singular_heading_one_to_one (admin_inlines.tests.TestInline)", "The \"View on Site\" link is correct for locales that use thousand", "Autogenerated many-to-many inlines are displayed correctly (#13407)", "min_num and extra determine number of forms.", "Admin inline `readonly_field` shouldn't invoke parent ModelAdmin callable", "test_non_editable_custom_form_tabular_inline_extra_field_label (admin_inlines.tests.TestInline)", "Multiple inlines with related_name='+' have correct form prefixes.", "Inlines without change permission shows field inputs on add form.", "Bug #13174.", "test_stacked_inline_edit_form_contains_has_original_class (admin_inlines.tests.TestInline)", "Field names are included in the context to output a field-specific", "Inlines `show_change_link` disabled by default.", "Tabular inlines use ModelForm.Meta.help_texts and labels for read-only", "non_field_errors are displayed correctly, including the correct value"]

**Base Commit**: 1bd6a7a0acc11e249fca11c017505ad39f15ebf6
**Environment Setup Commit**: 475cffd1d64c690cdad16ede4d5e81985738ceb4
