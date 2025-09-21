# django__django-12700

**Repository**: django/django
**Created**: 2020-04-11T01:58:27Z
**Version**: 3.1

## Problem Statement

Settings are cleaned insufficiently.
Description
	
Posting publicly after checking with the rest of the security team.
I just ran into a case where django.views.debug.SafeExceptionReporterFilter.get_safe_settings() would return several un-cleansed values. Looking at cleanse_setting() I realized that we ​only take care of `dict`s but don't take other types of iterables into account but ​return them as-is.
Example:
In my settings.py I have this:
MY_SETTING = {
	"foo": "value",
	"secret": "value",
	"token": "value",
	"something": [
		{"foo": "value"},
		{"secret": "value"},
		{"token": "value"},
	],
	"else": [
		[
			{"foo": "value"},
			{"secret": "value"},
			{"token": "value"},
		],
		[
			{"foo": "value"},
			{"secret": "value"},
			{"token": "value"},
		],
	]
}
On Django 3.0 and below:
>>> import pprint
>>> from django.views.debug import get_safe_settings
>>> pprint.pprint(get_safe_settings()["MY_SETTING"])
{'else': [[{'foo': 'value'}, {'secret': 'value'}, {'token': 'value'}],
		 [{'foo': 'value'}, {'secret': 'value'}, {'token': 'value'}]],
 'foo': 'value',
 'secret': '********************',
 'something': [{'foo': 'value'}, {'secret': 'value'}, {'token': 'value'}],
 'token': '********************'}
On Django 3.1 and up:
>>> from django.views.debug import SafeExceptionReporterFilter
>>> import pprint
>>> pprint.pprint(SafeExceptionReporterFilter().get_safe_settings()["MY_SETTING"])
{'else': [[{'foo': 'value'}, {'secret': 'value'}, {'token': 'value'}],
		 [{'foo': 'value'}, {'secret': 'value'}, {'token': 'value'}]],
 'foo': 'value',
 'secret': '********************',
 'something': [{'foo': 'value'}, {'secret': 'value'}, {'token': 'value'}],
 'token': '********************'}


## Hints

Do I need to change both versions? Or just create a single implementation for current master branch?

## Patch

```diff

diff --git a/django/views/debug.py b/django/views/debug.py
--- a/django/views/debug.py
+++ b/django/views/debug.py
@@ -90,6 +90,10 @@ def cleanse_setting(self, key, value):
                 cleansed = self.cleansed_substitute
             elif isinstance(value, dict):
                 cleansed = {k: self.cleanse_setting(k, v) for k, v in value.items()}
+            elif isinstance(value, list):
+                cleansed = [self.cleanse_setting('', v) for v in value]
+            elif isinstance(value, tuple):
+                cleansed = tuple([self.cleanse_setting('', v) for v in value])
             else:
                 cleansed = value
         except TypeError:


```

## Test Patch

```diff
diff --git a/tests/view_tests/tests/test_debug.py b/tests/view_tests/tests/test_debug.py
--- a/tests/view_tests/tests/test_debug.py
+++ b/tests/view_tests/tests/test_debug.py
@@ -1249,6 +1249,41 @@ def test_cleanse_setting_recurses_in_dictionary(self):
             {'login': 'cooper', 'password': reporter_filter.cleansed_substitute},
         )
 
+    def test_cleanse_setting_recurses_in_list_tuples(self):
+        reporter_filter = SafeExceptionReporterFilter()
+        initial = [
+            {
+                'login': 'cooper',
+                'password': 'secret',
+                'apps': (
+                    {'name': 'app1', 'api_key': 'a06b-c462cffae87a'},
+                    {'name': 'app2', 'api_key': 'a9f4-f152e97ad808'},
+                ),
+                'tokens': ['98b37c57-ec62-4e39', '8690ef7d-8004-4916'],
+            },
+            {'SECRET_KEY': 'c4d77c62-6196-4f17-a06b-c462cffae87a'},
+        ]
+        cleansed = [
+            {
+                'login': 'cooper',
+                'password': reporter_filter.cleansed_substitute,
+                'apps': (
+                    {'name': 'app1', 'api_key': reporter_filter.cleansed_substitute},
+                    {'name': 'app2', 'api_key': reporter_filter.cleansed_substitute},
+                ),
+                'tokens': reporter_filter.cleansed_substitute,
+            },
+            {'SECRET_KEY': reporter_filter.cleansed_substitute},
+        ]
+        self.assertEqual(
+            reporter_filter.cleanse_setting('SETTING_NAME', initial),
+            cleansed,
+        )
+        self.assertEqual(
+            reporter_filter.cleanse_setting('SETTING_NAME', tuple(initial)),
+            tuple(cleansed),
+        )
+
     def test_request_meta_filtering(self):
         request = self.rf.get('/', HTTP_SECRET_HEADER='super_secret')
         reporter_filter = SafeExceptionReporterFilter()

```

## Test Information

**Tests that should FAIL→PASS**: ["test_cleanse_setting_recurses_in_list_tuples (view_tests.tests.test_debug.ExceptionReporterFilterTests)"]

**Tests that should PASS→PASS**: ["test_repr (view_tests.tests.test_debug.CallableSettingWrapperTests)", "test_sensitive_post_parameters_not_called (view_tests.tests.test_debug.DecoratorsTests)", "test_sensitive_variables_not_called (view_tests.tests.test_debug.DecoratorsTests)", "test_cleansed_substitute_override (view_tests.tests.test_debug.CustomExceptionReporterFilterTests)", "test_hidden_settings_override (view_tests.tests.test_debug.CustomExceptionReporterFilterTests)", "test_setting_allows_custom_subclass (view_tests.tests.test_debug.CustomExceptionReporterFilterTests)", "test_handle_db_exception (view_tests.tests.test_debug.DebugViewQueriesAllowedTests)", "test_400 (view_tests.tests.test_debug.NonDjangoTemplatesDebugViewTests)", "test_403 (view_tests.tests.test_debug.NonDjangoTemplatesDebugViewTests)", "test_404 (view_tests.tests.test_debug.NonDjangoTemplatesDebugViewTests)", "test_template_not_found_error (view_tests.tests.test_debug.NonDjangoTemplatesDebugViewTests)", "An exception report can be generated even for a disallowed host.", "test_message_only (view_tests.tests.test_debug.PlainTextReportTests)", "An exception report can be generated for just a request", "An exception report can be generated without request", "A simple exception report can be generated", "A message can be provided in addition to a request", "test_request_with_items_key (view_tests.tests.test_debug.PlainTextReportTests)", "test_template_exception (view_tests.tests.test_debug.PlainTextReportTests)", "test_custom_exception_reporter_filter (view_tests.tests.test_debug.NonHTMLResponseExceptionReporterFilter)", "test_non_html_response_encoding (view_tests.tests.test_debug.NonHTMLResponseExceptionReporterFilter)", "test_non_sensitive_request (view_tests.tests.test_debug.NonHTMLResponseExceptionReporterFilter)", "test_paranoid_request (view_tests.tests.test_debug.NonHTMLResponseExceptionReporterFilter)", "test_sensitive_request (view_tests.tests.test_debug.NonHTMLResponseExceptionReporterFilter)", "test_400 (view_tests.tests.test_debug.DebugViewTests)", "test_403 (view_tests.tests.test_debug.DebugViewTests)", "test_403_template (view_tests.tests.test_debug.DebugViewTests)", "test_404 (view_tests.tests.test_debug.DebugViewTests)", "test_404_empty_path_not_in_urls (view_tests.tests.test_debug.DebugViewTests)", "test_404_not_in_urls (view_tests.tests.test_debug.DebugViewTests)", "test_classbased_technical_404 (view_tests.tests.test_debug.DebugViewTests)", "test_default_urlconf_template (view_tests.tests.test_debug.DebugViewTests)", "test_exception_reporter_from_request (view_tests.tests.test_debug.DebugViewTests)", "test_exception_reporter_from_settings (view_tests.tests.test_debug.DebugViewTests)", "test_files (view_tests.tests.test_debug.DebugViewTests)", "test_no_template_source_loaders (view_tests.tests.test_debug.DebugViewTests)", "test_non_l10ned_numeric_ids (view_tests.tests.test_debug.DebugViewTests)", "test_regression_21530 (view_tests.tests.test_debug.DebugViewTests)", "test_technical_404 (view_tests.tests.test_debug.DebugViewTests)", "test_technical_404_converter_raise_404 (view_tests.tests.test_debug.DebugViewTests)", "test_template_encoding (view_tests.tests.test_debug.DebugViewTests)", "test_template_exceptions (view_tests.tests.test_debug.DebugViewTests)", "Tests for not existing file", "test_encoding_error (view_tests.tests.test_debug.ExceptionReporterTests)", "The ExceptionReporter supports Unix, Windows and Macintosh EOL markers", "test_exception_fetching_user (view_tests.tests.test_debug.ExceptionReporterTests)", "test_ignore_traceback_evaluation_exceptions (view_tests.tests.test_debug.ExceptionReporterTests)", "Safe strings in local variables are escaped.", "test_message_only (view_tests.tests.test_debug.ExceptionReporterTests)", "Non-UTF-8 exceptions/values should not make the output generation choke.", "test_reporting_frames_for_cyclic_reference (view_tests.tests.test_debug.ExceptionReporterTests)", "test_reporting_frames_source_not_match (view_tests.tests.test_debug.ExceptionReporterTests)", "test_reporting_frames_without_source (view_tests.tests.test_debug.ExceptionReporterTests)", "test_reporting_of_nested_exceptions (view_tests.tests.test_debug.ExceptionReporterTests)", "test_request_with_items_key (view_tests.tests.test_debug.ExceptionReporterTests)", "test_template_encoding (view_tests.tests.test_debug.ExceptionReporterTests)", "Large values should not create a large HTML.", "test_unfrozen_importlib (view_tests.tests.test_debug.ExceptionReporterTests)", "Unprintable values should not make the output generation choke.", "test_callable_settings (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_callable_settings_forbidding_to_set_attributes (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_cleanse_setting_basic (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_cleanse_setting_ignore_case (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_cleanse_setting_recurses_in_dictionary (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_custom_exception_reporter_filter (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_dict_setting_with_non_str_key (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_exception_report_uses_meta_filtering (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_multivalue_dict_key_error (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_non_sensitive_request (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_paranoid_request (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_request_meta_filtering (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_sensitive_function_arguments (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_sensitive_function_keyword_arguments (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_sensitive_method (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_sensitive_request (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_sensitive_settings (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_settings_with_sensitive_keys (view_tests.tests.test_debug.ExceptionReporterFilterTests)"]

**Base Commit**: d51c50d836c5cf8db5566da17963f871be554615
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
