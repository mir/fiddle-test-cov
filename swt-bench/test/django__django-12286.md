# django__django-12286

**Repository**: django/django
**Created**: 2020-01-07T13:56:28Z
**Version**: 3.1

## Problem Statement

translation.E004 shouldn't be raised on sublanguages when a base language is available.
Description
	
According to Django documentation:
If a base language is available but the sublanguage specified is not, Django uses the base language. For example, if a user specifies de-at (Austrian German) but Django only has de available, Django uses de.
However, when using Django 3.0.2, if my settings.py has
LANGUAGE_CODE = "de-at"
I get this error message:
SystemCheckError: System check identified some issues:
ERRORS:
?: (translation.E004) You have provided a value for the LANGUAGE_CODE setting that is not in the LANGUAGES setting.
If using
LANGUAGE_CODE = "es-ar"
Django works fine (es-ar is one of the translations provided out of the box).


## Hints

Thanks for this report. Regression in 4400d8296d268f5a8523cd02ddc33b12219b2535.

## Patch

```diff

diff --git a/django/core/checks/translation.py b/django/core/checks/translation.py
--- a/django/core/checks/translation.py
+++ b/django/core/checks/translation.py
@@ -1,4 +1,5 @@
 from django.conf import settings
+from django.utils.translation import get_supported_language_variant
 from django.utils.translation.trans_real import language_code_re
 
 from . import Error, Tags, register
@@ -55,7 +56,9 @@ def check_setting_languages_bidi(app_configs, **kwargs):
 @register(Tags.translation)
 def check_language_settings_consistent(app_configs, **kwargs):
     """Error if language settings are not consistent with each other."""
-    available_tags = {i for i, _ in settings.LANGUAGES} | {'en-us'}
-    if settings.LANGUAGE_CODE not in available_tags:
+    try:
+        get_supported_language_variant(settings.LANGUAGE_CODE)
+    except LookupError:
         return [E004]
-    return []
+    else:
+        return []


```

## Test Patch

```diff
diff --git a/tests/check_framework/test_translation.py b/tests/check_framework/test_translation.py
--- a/tests/check_framework/test_translation.py
+++ b/tests/check_framework/test_translation.py
@@ -3,7 +3,7 @@
     check_language_settings_consistent, check_setting_language_code,
     check_setting_languages, check_setting_languages_bidi,
 )
-from django.test import SimpleTestCase
+from django.test import SimpleTestCase, override_settings
 
 
 class TranslationCheckTests(SimpleTestCase):
@@ -75,12 +75,36 @@ def test_invalid_languages_bidi(self):
                     Error(msg % tag, id='translation.E003'),
                 ])
 
+    @override_settings(USE_I18N=True, LANGUAGES=[('en', 'English')])
     def test_inconsistent_language_settings(self):
         msg = (
             'You have provided a value for the LANGUAGE_CODE setting that is '
             'not in the LANGUAGES setting.'
         )
-        with self.settings(LANGUAGE_CODE='fr', LANGUAGES=[('en', 'English')]):
-            self.assertEqual(check_language_settings_consistent(None), [
-                Error(msg, id='translation.E004'),
-            ])
+        for tag in ['fr', 'fr-CA', 'fr-357']:
+            with self.subTest(tag), self.settings(LANGUAGE_CODE=tag):
+                self.assertEqual(check_language_settings_consistent(None), [
+                    Error(msg, id='translation.E004'),
+                ])
+
+    @override_settings(
+        USE_I18N=True,
+        LANGUAGES=[
+            ('de', 'German'),
+            ('es', 'Spanish'),
+            ('fr', 'French'),
+            ('ca', 'Catalan'),
+        ],
+    )
+    def test_valid_variant_consistent_language_settings(self):
+        tests = [
+            # language + region.
+            'fr-CA',
+            'es-419',
+            'de-at',
+            # language + region + variant.
+            'ca-ES-valencia',
+        ]
+        for tag in tests:
+            with self.subTest(tag), self.settings(LANGUAGE_CODE=tag):
+                self.assertEqual(check_language_settings_consistent(None), [])

```

## Test Information

**Tests that should FAIL→PASS**: ["test_valid_variant_consistent_language_settings (check_framework.test_translation.TranslationCheckTests)"]

**Tests that should PASS→PASS**: ["test_inconsistent_language_settings (check_framework.test_translation.TranslationCheckTests)", "test_invalid_language_code (check_framework.test_translation.TranslationCheckTests)", "test_invalid_languages (check_framework.test_translation.TranslationCheckTests)", "test_invalid_languages_bidi (check_framework.test_translation.TranslationCheckTests)", "test_valid_language_code (check_framework.test_translation.TranslationCheckTests)", "test_valid_languages (check_framework.test_translation.TranslationCheckTests)", "test_valid_languages_bidi (check_framework.test_translation.TranslationCheckTests)"]

**Base Commit**: 979f61abd322507aafced9627702362e541ec34e
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
