# django__django-11099

**Repository**: django/django
**Created**: 2019-03-20T03:46:18Z
**Version**: 3.0

## Problem Statement

UsernameValidator allows trailing newline in usernames
Description
	
ASCIIUsernameValidator and UnicodeUsernameValidator use the regex 
r'^[\w.@+-]+$'
The intent is to only allow alphanumeric characters as well as ., @, +, and -. However, a little known quirk of Python regexes is that $ will also match a trailing newline. Therefore, the user name validators will accept usernames which end with a newline. You can avoid this behavior by instead using \A and \Z to terminate regexes. For example, the validator regex could be changed to
r'\A[\w.@+-]+\Z'
in order to reject usernames that end with a newline.
I am not sure how to officially post a patch, but the required change is trivial - using the regex above in the two validators in contrib.auth.validators.


## Patch

```diff

diff --git a/django/contrib/auth/validators.py b/django/contrib/auth/validators.py
--- a/django/contrib/auth/validators.py
+++ b/django/contrib/auth/validators.py
@@ -7,7 +7,7 @@
 
 @deconstructible
 class ASCIIUsernameValidator(validators.RegexValidator):
-    regex = r'^[\w.@+-]+$'
+    regex = r'^[\w.@+-]+\Z'
     message = _(
         'Enter a valid username. This value may contain only English letters, '
         'numbers, and @/./+/-/_ characters.'
@@ -17,7 +17,7 @@ class ASCIIUsernameValidator(validators.RegexValidator):
 
 @deconstructible
 class UnicodeUsernameValidator(validators.RegexValidator):
-    regex = r'^[\w.@+-]+$'
+    regex = r'^[\w.@+-]+\Z'
     message = _(
         'Enter a valid username. This value may contain only letters, '
         'numbers, and @/./+/-/_ characters.'


```

## Test Patch

```diff
diff --git a/tests/auth_tests/test_validators.py b/tests/auth_tests/test_validators.py
--- a/tests/auth_tests/test_validators.py
+++ b/tests/auth_tests/test_validators.py
@@ -237,7 +237,7 @@ def test_unicode_validator(self):
         invalid_usernames = [
             "o'connell", "عبد ال",
             "zerowidth\u200Bspace", "nonbreaking\u00A0space",
-            "en\u2013dash",
+            "en\u2013dash", 'trailingnewline\u000A',
         ]
         v = validators.UnicodeUsernameValidator()
         for valid in valid_usernames:
@@ -250,7 +250,7 @@ def test_unicode_validator(self):
 
     def test_ascii_validator(self):
         valid_usernames = ['glenn', 'GLEnN', 'jean-marc']
-        invalid_usernames = ["o'connell", 'Éric', 'jean marc', "أحمد"]
+        invalid_usernames = ["o'connell", 'Éric', 'jean marc', "أحمد", 'trailingnewline\n']
         v = validators.ASCIIUsernameValidator()
         for valid in valid_usernames:
             with self.subTest(valid=valid):

```

## Test Information

**Tests that should FAIL→PASS**: ["test_ascii_validator (auth_tests.test_validators.UsernameValidatorsTests)", "test_unicode_validator (auth_tests.test_validators.UsernameValidatorsTests)", "test_help_text (auth_tests.test_validators.UserAttributeSimilarityValidatorTest)"]

**Tests that should PASS→PASS**: ["test_help_text (auth_tests.test_validators.MinimumLengthValidatorTest)", "test_validate (auth_tests.test_validators.MinimumLengthValidatorTest)", "test_help_text (auth_tests.test_validators.NumericPasswordValidatorTest)", "test_validate (auth_tests.test_validators.NumericPasswordValidatorTest)", "test_validate (auth_tests.test_validators.UserAttributeSimilarityValidatorTest)", "test_validate_property (auth_tests.test_validators.UserAttributeSimilarityValidatorTest)", "test_empty_password_validator_help_text_html (auth_tests.test_validators.PasswordValidationTest)", "test_get_default_password_validators (auth_tests.test_validators.PasswordValidationTest)", "test_get_password_validators_custom (auth_tests.test_validators.PasswordValidationTest)", "test_password_changed (auth_tests.test_validators.PasswordValidationTest)", "test_password_changed_with_custom_validator (auth_tests.test_validators.PasswordValidationTest)", "test_password_validators_help_text_html (auth_tests.test_validators.PasswordValidationTest)", "test_password_validators_help_text_html_escaping (auth_tests.test_validators.PasswordValidationTest)", "test_password_validators_help_texts (auth_tests.test_validators.PasswordValidationTest)", "test_validate_password (auth_tests.test_validators.PasswordValidationTest)", "test_help_text (auth_tests.test_validators.CommonPasswordValidatorTest)", "test_validate (auth_tests.test_validators.CommonPasswordValidatorTest)", "test_validate_custom_list (auth_tests.test_validators.CommonPasswordValidatorTest)", "test_validate_django_supplied_file (auth_tests.test_validators.CommonPasswordValidatorTest)"]

**Base Commit**: d26b2424437dabeeca94d7900b37d2df4410da0c
**Environment Setup Commit**: 419a78300f7cd27611196e1e464d50fd0385ff27
