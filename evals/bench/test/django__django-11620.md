# django__django-11620

**Repository**: django/django
**Created**: 2019-08-02T13:56:08Z
**Version**: 3.0

## Problem Statement

When DEBUG is True, raising Http404 in a path converter's to_python method does not result in a technical response
Description
	
This is the response I get (plain text): 
A server error occurred. Please contact the administrator.
I understand a ValueError should be raised which tells the URL resolver "this path does not match, try next one" but Http404 is what came to my mind intuitively and the error message was not very helpful.
One could also make a point that raising a Http404 should be valid way to tell the resolver "this is indeed the right path but the current parameter value does not match anything so stop what you are doing and let the handler return the 404 page (including a helpful error message when DEBUG is True instead of the default 'Django tried these URL patterns')".
This would prove useful for example to implement a path converter that uses get_object_or_404.


## Hints

It seems that other exceptions correctly result in a technical 500 response.
The technical_404_response view performs a new URL resolving (cf ​https://github.com/django/django/blob/a8e492bc81fca829f5d270e2d57703c02e58701e/django/views/debug.py#L482) which will obviously raise a new Http404 which won't be caught as only Resolver404 is checked. That means the WSGI handler fails and the WSGI server returns the previously described default error message (indeed the error message is the default one from wsgiref.handlers.BaseHandler ​https://docs.python.org/3.6/library/wsgiref.html#wsgiref.handlers.BaseHandler.error_body). The solution seems to be to catch Http404 instead of Resolver404 in technical_404_response. This will result in a technical 404 page with the Http404's message displayed and will match the behaviour of when DEBUG is False.
Created ​PR , but I am not sure how to write the tests. I've looking about the response before and after catch Http404 instead of Resolver404, and there is no difference. Should I also change the technical_404.html for response?
I've added test to the patch, but not sure if it is correct.
I have made the requested changes; please review again

## Patch

```diff

diff --git a/django/views/debug.py b/django/views/debug.py
--- a/django/views/debug.py
+++ b/django/views/debug.py
@@ -5,10 +5,10 @@
 from pathlib import Path
 
 from django.conf import settings
-from django.http import HttpResponse, HttpResponseNotFound
+from django.http import Http404, HttpResponse, HttpResponseNotFound
 from django.template import Context, Engine, TemplateDoesNotExist
 from django.template.defaultfilters import pprint
-from django.urls import Resolver404, resolve
+from django.urls import resolve
 from django.utils import timezone
 from django.utils.datastructures import MultiValueDict
 from django.utils.encoding import force_str
@@ -483,7 +483,7 @@ def technical_404_response(request, exception):
     caller = ''
     try:
         resolver_match = resolve(request.path)
-    except Resolver404:
+    except Http404:
         pass
     else:
         obj = resolver_match.func


```

## Test Patch

```diff
diff --git a/tests/view_tests/tests/test_debug.py b/tests/view_tests/tests/test_debug.py
--- a/tests/view_tests/tests/test_debug.py
+++ b/tests/view_tests/tests/test_debug.py
@@ -12,11 +12,13 @@
 from django.core import mail
 from django.core.files.uploadedfile import SimpleUploadedFile
 from django.db import DatabaseError, connection
+from django.http import Http404
 from django.shortcuts import render
 from django.template import TemplateDoesNotExist
 from django.test import RequestFactory, SimpleTestCase, override_settings
 from django.test.utils import LoggingCaptureMixin
 from django.urls import path, reverse
+from django.urls.converters import IntConverter
 from django.utils.functional import SimpleLazyObject
 from django.utils.safestring import mark_safe
 from django.views.debug import (
@@ -237,6 +239,11 @@ def test_template_encoding(self):
             technical_404_response(mock.MagicMock(), mock.Mock())
             m.assert_called_once_with(encoding='utf-8')
 
+    def test_technical_404_converter_raise_404(self):
+        with mock.patch.object(IntConverter, 'to_python', side_effect=Http404):
+            response = self.client.get('/path-post/1/')
+            self.assertContains(response, 'Page not found', status_code=404)
+
 
 class DebugViewQueriesAllowedTests(SimpleTestCase):
     # May need a query to initialize MySQL connection

```

## Test Information

**Tests that should FAIL→PASS**: ["test_technical_404_converter_raise_404 (view_tests.tests.test_debug.DebugViewTests)"]

**Tests that should PASS→PASS**: ["test_repr (view_tests.tests.test_debug.CallableSettingWrapperTests)", "test_cleanse_setting_basic (view_tests.tests.test_debug.HelperFunctionTests)", "test_cleanse_setting_ignore_case (view_tests.tests.test_debug.HelperFunctionTests)", "test_cleanse_setting_recurses_in_dictionary (view_tests.tests.test_debug.HelperFunctionTests)", "test_handle_db_exception (view_tests.tests.test_debug.DebugViewQueriesAllowedTests)", "test_400 (view_tests.tests.test_debug.NonDjangoTemplatesDebugViewTests)", "test_403 (view_tests.tests.test_debug.NonDjangoTemplatesDebugViewTests)", "test_404 (view_tests.tests.test_debug.NonDjangoTemplatesDebugViewTests)", "test_template_not_found_error (view_tests.tests.test_debug.NonDjangoTemplatesDebugViewTests)", "An exception report can be generated even for a disallowed host.", "test_message_only (view_tests.tests.test_debug.PlainTextReportTests)", "An exception report can be generated for just a request", "An exception report can be generated without request", "A simple exception report can be generated", "A message can be provided in addition to a request", "test_request_with_items_key (view_tests.tests.test_debug.PlainTextReportTests)", "test_template_exception (view_tests.tests.test_debug.PlainTextReportTests)", "test_ajax_response_encoding (view_tests.tests.test_debug.AjaxResponseExceptionReporterFilter)", "test_custom_exception_reporter_filter (view_tests.tests.test_debug.AjaxResponseExceptionReporterFilter)", "test_non_sensitive_request (view_tests.tests.test_debug.AjaxResponseExceptionReporterFilter)", "test_paranoid_request (view_tests.tests.test_debug.AjaxResponseExceptionReporterFilter)", "test_sensitive_request (view_tests.tests.test_debug.AjaxResponseExceptionReporterFilter)", "test_400 (view_tests.tests.test_debug.DebugViewTests)", "test_403 (view_tests.tests.test_debug.DebugViewTests)", "test_403_template (view_tests.tests.test_debug.DebugViewTests)", "test_404 (view_tests.tests.test_debug.DebugViewTests)", "test_404_empty_path_not_in_urls (view_tests.tests.test_debug.DebugViewTests)", "test_404_not_in_urls (view_tests.tests.test_debug.DebugViewTests)", "test_classbased_technical_404 (view_tests.tests.test_debug.DebugViewTests)", "test_default_urlconf_template (view_tests.tests.test_debug.DebugViewTests)", "test_files (view_tests.tests.test_debug.DebugViewTests)", "test_no_template_source_loaders (view_tests.tests.test_debug.DebugViewTests)", "test_non_l10ned_numeric_ids (view_tests.tests.test_debug.DebugViewTests)", "test_regression_21530 (view_tests.tests.test_debug.DebugViewTests)", "test_technical_404 (view_tests.tests.test_debug.DebugViewTests)", "test_template_encoding (view_tests.tests.test_debug.DebugViewTests)", "test_template_exceptions (view_tests.tests.test_debug.DebugViewTests)", "Tests for not existing file", "test_encoding_error (view_tests.tests.test_debug.ExceptionReporterTests)", "The ExceptionReporter supports Unix, Windows and Macintosh EOL markers", "test_exception_fetching_user (view_tests.tests.test_debug.ExceptionReporterTests)", "test_ignore_traceback_evaluation_exceptions (view_tests.tests.test_debug.ExceptionReporterTests)", "Safe strings in local variables are escaped.", "test_message_only (view_tests.tests.test_debug.ExceptionReporterTests)", "Non-UTF-8 exceptions/values should not make the output generation choke.", "test_reporting_frames_for_cyclic_reference (view_tests.tests.test_debug.ExceptionReporterTests)", "test_reporting_frames_without_source (view_tests.tests.test_debug.ExceptionReporterTests)", "test_reporting_of_nested_exceptions (view_tests.tests.test_debug.ExceptionReporterTests)", "test_request_with_items_key (view_tests.tests.test_debug.ExceptionReporterTests)", "test_template_encoding (view_tests.tests.test_debug.ExceptionReporterTests)", "Large values should not create a large HTML.", "test_unfrozen_importlib (view_tests.tests.test_debug.ExceptionReporterTests)", "Unprintable values should not make the output generation choke.", "test_callable_settings (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_callable_settings_forbidding_to_set_attributes (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_custom_exception_reporter_filter (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_dict_setting_with_non_str_key (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_multivalue_dict_key_error (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_non_sensitive_request (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_paranoid_request (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_sensitive_function_arguments (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_sensitive_function_keyword_arguments (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_sensitive_method (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_sensitive_request (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_sensitive_settings (view_tests.tests.test_debug.ExceptionReporterFilterTests)", "test_settings_with_sensitive_keys (view_tests.tests.test_debug.ExceptionReporterFilterTests)"]

**Base Commit**: 514efa3129792ec2abb2444f3e7aeb3f21a38386
**Environment Setup Commit**: 419a78300f7cd27611196e1e464d50fd0385ff27
