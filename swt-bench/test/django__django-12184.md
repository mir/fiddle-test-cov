# django__django-12184

**Repository**: django/django
**Created**: 2019-12-05T13:09:48Z
**Version**: 3.1

## Problem Statement

Optional URL params crash some view functions.
Description
	
My use case, running fine with Django until 2.2:
URLConf:
urlpatterns += [
	...
	re_path(r'^module/(?P<format>(html|json|xml))?/?$', views.modules, name='modules'),
]
View:
def modules(request, format='html'):
	...
	return render(...)
With Django 3.0, this is now producing an error:
Traceback (most recent call last):
 File "/l10n/venv/lib/python3.6/site-packages/django/core/handlers/exception.py", line 34, in inner
	response = get_response(request)
 File "/l10n/venv/lib/python3.6/site-packages/django/core/handlers/base.py", line 115, in _get_response
	response = self.process_exception_by_middleware(e, request)
 File "/l10n/venv/lib/python3.6/site-packages/django/core/handlers/base.py", line 113, in _get_response
	response = wrapped_callback(request, *callback_args, **callback_kwargs)
Exception Type: TypeError at /module/
Exception Value: modules() takes from 1 to 2 positional arguments but 3 were given


## Hints

Tracked regression in 76b993a117b61c41584e95149a67d8a1e9f49dd1.
It seems to work if you remove the extra parentheses: re_path(r'^module/(?P<format>html|json|xml)?/?$', views.modules, name='modules'), It seems Django is getting confused by the nested groups.

## Patch

```diff

diff --git a/django/urls/resolvers.py b/django/urls/resolvers.py
--- a/django/urls/resolvers.py
+++ b/django/urls/resolvers.py
@@ -158,8 +158,9 @@ def match(self, path):
             # If there are any named groups, use those as kwargs, ignoring
             # non-named groups. Otherwise, pass all non-named arguments as
             # positional arguments.
-            kwargs = {k: v for k, v in match.groupdict().items() if v is not None}
+            kwargs = match.groupdict()
             args = () if kwargs else match.groups()
+            kwargs = {k: v for k, v in kwargs.items() if v is not None}
             return path[match.end():], args, kwargs
         return None
 


```

## Test Patch

```diff
diff --git a/tests/urlpatterns/path_urls.py b/tests/urlpatterns/path_urls.py
--- a/tests/urlpatterns/path_urls.py
+++ b/tests/urlpatterns/path_urls.py
@@ -12,6 +12,11 @@
     path('included_urls/', include('urlpatterns.included_urls')),
     re_path(r'^regex/(?P<pk>[0-9]+)/$', views.empty_view, name='regex'),
     re_path(r'^regex_optional/(?P<arg1>\d+)/(?:(?P<arg2>\d+)/)?', views.empty_view, name='regex_optional'),
+    re_path(
+        r'^regex_only_optional/(?:(?P<arg1>\d+)/)?',
+        views.empty_view,
+        name='regex_only_optional',
+    ),
     path('', include('urlpatterns.more_urls')),
     path('<lang>/<path:url>/', views.empty_view, name='lang-and-path'),
 ]
diff --git a/tests/urlpatterns/tests.py b/tests/urlpatterns/tests.py
--- a/tests/urlpatterns/tests.py
+++ b/tests/urlpatterns/tests.py
@@ -68,6 +68,16 @@ def test_re_path_with_optional_parameter(self):
                     r'^regex_optional/(?P<arg1>\d+)/(?:(?P<arg2>\d+)/)?',
                 )
 
+    def test_re_path_with_missing_optional_parameter(self):
+        match = resolve('/regex_only_optional/')
+        self.assertEqual(match.url_name, 'regex_only_optional')
+        self.assertEqual(match.kwargs, {})
+        self.assertEqual(match.args, ())
+        self.assertEqual(
+            match.route,
+            r'^regex_only_optional/(?:(?P<arg1>\d+)/)?',
+        )
+
     def test_path_lookup_with_inclusion(self):
         match = resolve('/included_urls/extra/something/')
         self.assertEqual(match.url_name, 'inner-extra')

```

## Test Information

**Tests that should FAIL→PASS**: ["test_re_path_with_missing_optional_parameter (urlpatterns.tests.SimplifiedURLTests)"]

**Tests that should PASS→PASS**: ["test_allows_non_ascii_but_valid_identifiers (urlpatterns.tests.ParameterRestrictionTests)", "test_non_identifier_parameter_name_causes_exception (urlpatterns.tests.ParameterRestrictionTests)", "test_matching_urls (urlpatterns.tests.ConverterTests)", "test_nonmatching_urls (urlpatterns.tests.ConverterTests)", "test_resolve_type_error_propagates (urlpatterns.tests.ConversionExceptionTests)", "test_resolve_value_error_means_no_match (urlpatterns.tests.ConversionExceptionTests)", "test_reverse_value_error_propagates (urlpatterns.tests.ConversionExceptionTests)", "test_converter_resolve (urlpatterns.tests.SimplifiedURLTests)", "test_converter_reverse (urlpatterns.tests.SimplifiedURLTests)", "test_converter_reverse_with_second_layer_instance_namespace (urlpatterns.tests.SimplifiedURLTests)", "test_invalid_converter (urlpatterns.tests.SimplifiedURLTests)", "test_path_inclusion_is_matchable (urlpatterns.tests.SimplifiedURLTests)", "test_path_inclusion_is_reversible (urlpatterns.tests.SimplifiedURLTests)", "test_path_lookup_with_double_inclusion (urlpatterns.tests.SimplifiedURLTests)", "test_path_lookup_with_empty_string_inclusion (urlpatterns.tests.SimplifiedURLTests)", "test_path_lookup_with_inclusion (urlpatterns.tests.SimplifiedURLTests)", "test_path_lookup_with_multiple_parameters (urlpatterns.tests.SimplifiedURLTests)", "test_path_lookup_with_typed_parameters (urlpatterns.tests.SimplifiedURLTests)", "test_path_lookup_without_parameters (urlpatterns.tests.SimplifiedURLTests)", "test_path_reverse_with_parameter (urlpatterns.tests.SimplifiedURLTests)", "test_path_reverse_without_parameter (urlpatterns.tests.SimplifiedURLTests)", "test_re_path (urlpatterns.tests.SimplifiedURLTests)", "test_re_path_with_optional_parameter (urlpatterns.tests.SimplifiedURLTests)", "test_space_in_route (urlpatterns.tests.SimplifiedURLTests)", "test_two_variable_at_start_of_path_pattern (urlpatterns.tests.SimplifiedURLTests)"]

**Base Commit**: 5d674eac871a306405b0fbbaeb17bbeba9c68bf3
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
