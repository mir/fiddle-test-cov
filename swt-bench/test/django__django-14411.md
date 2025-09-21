# django__django-14411

**Repository**: django/django
**Created**: 2021-05-19T04:05:47Z
**Version**: 4.0

## Problem Statement

Label for ReadOnlyPasswordHashWidget points to non-labelable element.
Description
	 
		(last modified by David Sanders)
	 
In the admin, the label element for the ReadOnlyPasswordHashWidget widget has a 'for' attribute which points to a non-labelable element, since the widget just renders text, not an input. There's no labelable element for the widget, so the label shouldn't have a 'for' attribute.


## Patch

```diff

diff --git a/django/contrib/auth/forms.py b/django/contrib/auth/forms.py
--- a/django/contrib/auth/forms.py
+++ b/django/contrib/auth/forms.py
@@ -50,6 +50,9 @@ def get_context(self, name, value, attrs):
         context['summary'] = summary
         return context
 
+    def id_for_label(self, id_):
+        return None
+
 
 class ReadOnlyPasswordHashField(forms.Field):
     widget = ReadOnlyPasswordHashWidget


```

## Test Patch

```diff
diff --git a/tests/auth_tests/test_forms.py b/tests/auth_tests/test_forms.py
--- a/tests/auth_tests/test_forms.py
+++ b/tests/auth_tests/test_forms.py
@@ -13,6 +13,7 @@
 from django.core import mail
 from django.core.exceptions import ValidationError
 from django.core.mail import EmailMultiAlternatives
+from django.forms import forms
 from django.forms.fields import CharField, Field, IntegerField
 from django.test import SimpleTestCase, TestCase, override_settings
 from django.utils import translation
@@ -1025,6 +1026,18 @@ def test_readonly_field_has_changed(self):
         self.assertIs(field.disabled, True)
         self.assertFalse(field.has_changed('aaa', 'bbb'))
 
+    def test_label(self):
+        """
+        ReadOnlyPasswordHashWidget doesn't contain a for attribute in the
+        <label> because it doesn't have any labelable elements.
+        """
+        class TestForm(forms.Form):
+            hash_field = ReadOnlyPasswordHashField()
+
+        bound_field = TestForm()['hash_field']
+        self.assertEqual(bound_field.field.widget.id_for_label('id'), None)
+        self.assertEqual(bound_field.label_tag(), '<label>Hash field:</label>')
+
 
 class AdminPasswordChangeFormTest(TestDataMixin, TestCase):
 

```

## Test Information

**Tests that should FAIL→PASS**: ["ReadOnlyPasswordHashWidget doesn't contain a for attribute in the"]

**Tests that should PASS→PASS**: ["test_html_autocomplete_attributes (auth_tests.test_forms.AdminPasswordChangeFormTest)", "test_missing_passwords (auth_tests.test_forms.AdminPasswordChangeFormTest)", "test_non_matching_passwords (auth_tests.test_forms.AdminPasswordChangeFormTest)", "test_one_password (auth_tests.test_forms.AdminPasswordChangeFormTest)", "test_password_whitespace_not_stripped (auth_tests.test_forms.AdminPasswordChangeFormTest)", "test_success (auth_tests.test_forms.AdminPasswordChangeFormTest)", "test_field_order (auth_tests.test_forms.PasswordChangeFormTest)", "test_html_autocomplete_attributes (auth_tests.test_forms.PasswordChangeFormTest)", "test_incorrect_password (auth_tests.test_forms.PasswordChangeFormTest)", "test_password_verification (auth_tests.test_forms.PasswordChangeFormTest)", "test_password_whitespace_not_stripped (auth_tests.test_forms.PasswordChangeFormTest)", "test_success (auth_tests.test_forms.PasswordChangeFormTest)", "test_both_passwords (auth_tests.test_forms.UserCreationFormTest)", "test_custom_form (auth_tests.test_forms.UserCreationFormTest)", "test_custom_form_hidden_username_field (auth_tests.test_forms.UserCreationFormTest)", "test_custom_form_with_different_username_field (auth_tests.test_forms.UserCreationFormTest)", "To prevent almost identical usernames, visually identical but differing", "test_html_autocomplete_attributes (auth_tests.test_forms.UserCreationFormTest)", "test_invalid_data (auth_tests.test_forms.UserCreationFormTest)", "test_normalize_username (auth_tests.test_forms.UserCreationFormTest)", "test_password_help_text (auth_tests.test_forms.UserCreationFormTest)", "test_password_verification (auth_tests.test_forms.UserCreationFormTest)", "test_password_whitespace_not_stripped (auth_tests.test_forms.UserCreationFormTest)", "test_success (auth_tests.test_forms.UserCreationFormTest)", "test_unicode_username (auth_tests.test_forms.UserCreationFormTest)", "test_user_already_exists (auth_tests.test_forms.UserCreationFormTest)", "UserCreationForm password validation uses all of the form's data.", "test_username_field_autocapitalize_none (auth_tests.test_forms.UserCreationFormTest)", "test_validates_password (auth_tests.test_forms.UserCreationFormTest)", "test_bug_19349_render_with_none_value (auth_tests.test_forms.ReadOnlyPasswordHashTest)", "test_readonly_field_has_changed (auth_tests.test_forms.ReadOnlyPasswordHashTest)", "test_render (auth_tests.test_forms.ReadOnlyPasswordHashTest)", "test_help_text_translation (auth_tests.test_forms.SetPasswordFormTest)", "test_html_autocomplete_attributes (auth_tests.test_forms.SetPasswordFormTest)", "test_password_verification (auth_tests.test_forms.SetPasswordFormTest)", "test_password_whitespace_not_stripped (auth_tests.test_forms.SetPasswordFormTest)", "test_success (auth_tests.test_forms.SetPasswordFormTest)", "test_validates_password (auth_tests.test_forms.SetPasswordFormTest)", "test_custom_login_allowed_policy (auth_tests.test_forms.AuthenticationFormTest)", "test_get_invalid_login_error (auth_tests.test_forms.AuthenticationFormTest)", "test_html_autocomplete_attributes (auth_tests.test_forms.AuthenticationFormTest)", "test_inactive_user (auth_tests.test_forms.AuthenticationFormTest)", "test_inactive_user_i18n (auth_tests.test_forms.AuthenticationFormTest)", "An invalid login doesn't leak the inactive status of a user.", "test_integer_username (auth_tests.test_forms.AuthenticationFormTest)", "test_invalid_username (auth_tests.test_forms.AuthenticationFormTest)", "test_login_failed (auth_tests.test_forms.AuthenticationFormTest)", "test_password_whitespace_not_stripped (auth_tests.test_forms.AuthenticationFormTest)", "test_success (auth_tests.test_forms.AuthenticationFormTest)", "test_unicode_username (auth_tests.test_forms.AuthenticationFormTest)", "test_username_field_autocapitalize_none (auth_tests.test_forms.AuthenticationFormTest)", "test_username_field_label (auth_tests.test_forms.AuthenticationFormTest)", "test_username_field_label_empty_string (auth_tests.test_forms.AuthenticationFormTest)", "test_username_field_label_not_set (auth_tests.test_forms.AuthenticationFormTest)", "test_username_field_max_length_defaults_to_254 (auth_tests.test_forms.AuthenticationFormTest)", "test_username_field_max_length_matches_user_model (auth_tests.test_forms.AuthenticationFormTest)", "test_cleaned_data (auth_tests.test_forms.PasswordResetFormTest)", "test_custom_email_constructor (auth_tests.test_forms.PasswordResetFormTest)", "test_custom_email_field (auth_tests.test_forms.PasswordResetFormTest)", "test_custom_email_subject (auth_tests.test_forms.PasswordResetFormTest)", "test_html_autocomplete_attributes (auth_tests.test_forms.PasswordResetFormTest)", "Inactive user cannot receive password reset email.", "test_invalid_email (auth_tests.test_forms.PasswordResetFormTest)", "Test nonexistent email address. This should not fail because it would", "Preserve the case of the user name (before the @ in the email address)", "Test the PasswordResetForm.save() method with html_email_template_name", "Test the PasswordResetForm.save() method with no html_email_template_name", "test_unusable_password (auth_tests.test_forms.PasswordResetFormTest)", "test_user_email_domain_unicode_collision (auth_tests.test_forms.PasswordResetFormTest)", "test_user_email_domain_unicode_collision_nonexistent (auth_tests.test_forms.PasswordResetFormTest)", "test_user_email_unicode_collision (auth_tests.test_forms.PasswordResetFormTest)", "test_user_email_unicode_collision_nonexistent (auth_tests.test_forms.PasswordResetFormTest)", "test_bug_14242 (auth_tests.test_forms.UserChangeFormTest)", "test_bug_17944_empty_password (auth_tests.test_forms.UserChangeFormTest)", "test_bug_17944_unknown_password_algorithm (auth_tests.test_forms.UserChangeFormTest)", "test_bug_17944_unmanageable_password (auth_tests.test_forms.UserChangeFormTest)", "The change form does not return the password value", "test_bug_19349_bound_password_field (auth_tests.test_forms.UserChangeFormTest)", "test_custom_form (auth_tests.test_forms.UserChangeFormTest)", "test_password_excluded (auth_tests.test_forms.UserChangeFormTest)", "test_unusable_password (auth_tests.test_forms.UserChangeFormTest)", "test_username_field_autocapitalize_none (auth_tests.test_forms.UserChangeFormTest)", "test_username_validity (auth_tests.test_forms.UserChangeFormTest)"]

**Base Commit**: fa4e963ee7e6876581b5432363603571839ba00c
**Environment Setup Commit**: 475cffd1d64c690cdad16ede4d5e81985738ceb4
