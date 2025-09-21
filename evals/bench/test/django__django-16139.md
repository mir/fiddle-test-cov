# django__django-16139

**Repository**: django/django
**Created**: 2022-09-30T08:51:16Z
**Version**: 4.2

## Problem Statement

Accessing UserAdmin via to_field leads to link to PasswordResetForm being broken (404)
Description
	 
		(last modified by Simon Kern)
	 
Accessing the UserAdmin via another model's Admin that has a reference to User (with to_field set, e.g., to_field="uuid") leads to the UserAdmin being accessed via an url that looks similar to this one:
.../user/22222222-3333-4444-5555-666677778888/change/?_to_field=uuid
However the underlying form looks like this: 
Code highlighting:
class UserChangeForm(forms.ModelForm):
	password = ReadOnlyPasswordHashField(
		label=_("Password"),
		help_text=_(
			"Raw passwords are not stored, so there is no way to see this "
			"user’s password, but you can change the password using "
			'<a href="{}">this form</a>.'
		),
	)
	...
	...
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		password = self.fields.get("password")
		if password:
			password.help_text = password.help_text.format("../password/")
	...
	...
This results in the link to the PasswordResetForm being wrong and thus ending up in a 404. If we drop the assumption that UserAdmin is always accessed via its pk, then we're good to go. It's as simple as replacing password.help_text = password.help_text.format("../password/") with password.help_text = password.help_text.format(f"../../{self.instance.pk}/password/")
I've opened a pull request on GitHub for this Ticket, please see:
​PR


## Patch

```diff

diff --git a/django/contrib/auth/forms.py b/django/contrib/auth/forms.py
--- a/django/contrib/auth/forms.py
+++ b/django/contrib/auth/forms.py
@@ -163,7 +163,9 @@ def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs)
         password = self.fields.get("password")
         if password:
-            password.help_text = password.help_text.format("../password/")
+            password.help_text = password.help_text.format(
+                f"../../{self.instance.pk}/password/"
+            )
         user_permissions = self.fields.get("user_permissions")
         if user_permissions:
             user_permissions.queryset = user_permissions.queryset.select_related(


```

## Test Patch

```diff
diff --git a/tests/auth_tests/test_forms.py b/tests/auth_tests/test_forms.py
--- a/tests/auth_tests/test_forms.py
+++ b/tests/auth_tests/test_forms.py
@@ -1,5 +1,6 @@
 import datetime
 import re
+import urllib.parse
 from unittest import mock
 
 from django.contrib.auth.forms import (
@@ -22,6 +23,7 @@
 from django.forms import forms
 from django.forms.fields import CharField, Field, IntegerField
 from django.test import SimpleTestCase, TestCase, override_settings
+from django.urls import reverse
 from django.utils import translation
 from django.utils.text import capfirst
 from django.utils.translation import gettext as _
@@ -892,6 +894,26 @@ def test_bug_19349_bound_password_field(self):
         # value to render correctly
         self.assertEqual(form.initial["password"], form["password"].value())
 
+    @override_settings(ROOT_URLCONF="auth_tests.urls_admin")
+    def test_link_to_password_reset_in_helptext_via_to_field(self):
+        user = User.objects.get(username="testclient")
+        form = UserChangeForm(data={}, instance=user)
+        password_help_text = form.fields["password"].help_text
+        matches = re.search('<a href="(.*?)">', password_help_text)
+
+        # URL to UserChangeForm in admin via to_field (instead of pk).
+        admin_user_change_url = reverse(
+            f"admin:{user._meta.app_label}_{user._meta.model_name}_change",
+            args=(user.username,),
+        )
+        joined_url = urllib.parse.urljoin(admin_user_change_url, matches.group(1))
+
+        pw_change_url = reverse(
+            f"admin:{user._meta.app_label}_{user._meta.model_name}_password_change",
+            args=(user.pk,),
+        )
+        self.assertEqual(joined_url, pw_change_url)
+
     def test_custom_form(self):
         class CustomUserChangeForm(UserChangeForm):
             class Meta(UserChangeForm.Meta):

```

## Test Information

**Tests that should FAIL→PASS**: ["test_link_to_password_reset_in_helptext_via_to_field (auth_tests.test_forms.UserChangeFormTest)"]

**Tests that should PASS→PASS**: ["test_field_order (auth_tests.test_forms.PasswordChangeFormTest)", "test_html_autocomplete_attributes (auth_tests.test_forms.PasswordChangeFormTest)", "test_incorrect_password (auth_tests.test_forms.PasswordChangeFormTest)", "test_password_verification (auth_tests.test_forms.PasswordChangeFormTest)", "test_password_whitespace_not_stripped (auth_tests.test_forms.PasswordChangeFormTest)", "test_success (auth_tests.test_forms.PasswordChangeFormTest)", "test_html_autocomplete_attributes (auth_tests.test_forms.AdminPasswordChangeFormTest)", "test_missing_passwords (auth_tests.test_forms.AdminPasswordChangeFormTest)", "test_non_matching_passwords (auth_tests.test_forms.AdminPasswordChangeFormTest)", "test_one_password (auth_tests.test_forms.AdminPasswordChangeFormTest)", "test_password_whitespace_not_stripped (auth_tests.test_forms.AdminPasswordChangeFormTest)", "test_success (auth_tests.test_forms.AdminPasswordChangeFormTest)", "test_both_passwords (auth_tests.test_forms.UserCreationFormTest)", "test_custom_form (auth_tests.test_forms.UserCreationFormTest)", "test_custom_form_hidden_username_field (auth_tests.test_forms.UserCreationFormTest)", "test_custom_form_with_different_username_field (auth_tests.test_forms.UserCreationFormTest)", "To prevent almost identical usernames, visually identical but differing", "test_html_autocomplete_attributes (auth_tests.test_forms.UserCreationFormTest)", "test_invalid_data (auth_tests.test_forms.UserCreationFormTest)", "test_normalize_username (auth_tests.test_forms.UserCreationFormTest)", "test_password_help_text (auth_tests.test_forms.UserCreationFormTest)", "test_password_verification (auth_tests.test_forms.UserCreationFormTest)", "test_password_whitespace_not_stripped (auth_tests.test_forms.UserCreationFormTest)", "test_success (auth_tests.test_forms.UserCreationFormTest)", "test_unicode_username (auth_tests.test_forms.UserCreationFormTest)", "test_user_already_exists (auth_tests.test_forms.UserCreationFormTest)", "UserCreationForm password validation uses all of the form's data.", "test_username_field_autocapitalize_none (auth_tests.test_forms.UserCreationFormTest)", "test_validates_password (auth_tests.test_forms.UserCreationFormTest)", "test_bug_19349_render_with_none_value (auth_tests.test_forms.ReadOnlyPasswordHashTest)", "ReadOnlyPasswordHashWidget doesn't contain a for attribute in the", "test_readonly_field_has_changed (auth_tests.test_forms.ReadOnlyPasswordHashTest)", "test_render (auth_tests.test_forms.ReadOnlyPasswordHashTest)", "test_help_text_translation (auth_tests.test_forms.SetPasswordFormTest)", "test_html_autocomplete_attributes (auth_tests.test_forms.SetPasswordFormTest)", "test_no_password (auth_tests.test_forms.SetPasswordFormTest)", "test_password_verification (auth_tests.test_forms.SetPasswordFormTest)", "test_password_whitespace_not_stripped (auth_tests.test_forms.SetPasswordFormTest)", "test_success (auth_tests.test_forms.SetPasswordFormTest)", "test_validates_password (auth_tests.test_forms.SetPasswordFormTest)", "test_custom_login_allowed_policy (auth_tests.test_forms.AuthenticationFormTest)", "test_get_invalid_login_error (auth_tests.test_forms.AuthenticationFormTest)", "test_html_autocomplete_attributes (auth_tests.test_forms.AuthenticationFormTest)", "test_inactive_user (auth_tests.test_forms.AuthenticationFormTest)", "test_inactive_user_i18n (auth_tests.test_forms.AuthenticationFormTest)", "An invalid login doesn't leak the inactive status of a user.", "test_integer_username (auth_tests.test_forms.AuthenticationFormTest)", "test_invalid_username (auth_tests.test_forms.AuthenticationFormTest)", "test_login_failed (auth_tests.test_forms.AuthenticationFormTest)", "test_no_password (auth_tests.test_forms.AuthenticationFormTest)", "test_password_whitespace_not_stripped (auth_tests.test_forms.AuthenticationFormTest)", "test_success (auth_tests.test_forms.AuthenticationFormTest)", "test_unicode_username (auth_tests.test_forms.AuthenticationFormTest)", "test_username_field_autocapitalize_none (auth_tests.test_forms.AuthenticationFormTest)", "test_username_field_label (auth_tests.test_forms.AuthenticationFormTest)", "test_username_field_label_empty_string (auth_tests.test_forms.AuthenticationFormTest)", "test_username_field_label_not_set (auth_tests.test_forms.AuthenticationFormTest)", "test_username_field_max_length_defaults_to_254 (auth_tests.test_forms.AuthenticationFormTest)", "test_username_field_max_length_matches_user_model (auth_tests.test_forms.AuthenticationFormTest)", "test_cleaned_data (auth_tests.test_forms.PasswordResetFormTest)", "test_custom_email_constructor (auth_tests.test_forms.PasswordResetFormTest)", "test_custom_email_field (auth_tests.test_forms.PasswordResetFormTest)", "test_custom_email_subject (auth_tests.test_forms.PasswordResetFormTest)", "test_html_autocomplete_attributes (auth_tests.test_forms.PasswordResetFormTest)", "Inactive user cannot receive password reset email.", "test_invalid_email (auth_tests.test_forms.PasswordResetFormTest)", "Test nonexistent email address. This should not fail because it would", "Preserve the case of the user name (before the @ in the email address)", "Test the PasswordResetForm.save() method with html_email_template_name", "Test the PasswordResetForm.save() method with no html_email_template_name", "test_unusable_password (auth_tests.test_forms.PasswordResetFormTest)", "test_user_email_domain_unicode_collision (auth_tests.test_forms.PasswordResetFormTest)", "test_user_email_domain_unicode_collision_nonexistent (auth_tests.test_forms.PasswordResetFormTest)", "test_user_email_unicode_collision (auth_tests.test_forms.PasswordResetFormTest)", "test_user_email_unicode_collision_nonexistent (auth_tests.test_forms.PasswordResetFormTest)", "test_bug_14242 (auth_tests.test_forms.UserChangeFormTest)", "test_bug_17944_empty_password (auth_tests.test_forms.UserChangeFormTest)", "test_bug_17944_unknown_password_algorithm (auth_tests.test_forms.UserChangeFormTest)", "test_bug_17944_unmanageable_password (auth_tests.test_forms.UserChangeFormTest)", "The change form does not return the password value", "test_bug_19349_bound_password_field (auth_tests.test_forms.UserChangeFormTest)", "test_custom_form (auth_tests.test_forms.UserChangeFormTest)", "test_password_excluded (auth_tests.test_forms.UserChangeFormTest)", "test_unusable_password (auth_tests.test_forms.UserChangeFormTest)", "test_username_field_autocapitalize_none (auth_tests.test_forms.UserChangeFormTest)", "test_username_validity (auth_tests.test_forms.UserChangeFormTest)"]

**Base Commit**: d559cb02da30f74debbb1fc3a46de0df134d2d80
**Environment Setup Commit**: 0fbdb9784da915fce5dcc1fe82bac9b4785749e5
