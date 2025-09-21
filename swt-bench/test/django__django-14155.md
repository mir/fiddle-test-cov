# django__django-14155

**Repository**: django/django
**Created**: 2021-03-19T15:44:25Z
**Version**: 4.0

## Problem Statement

ResolverMatch.__repr__() doesn't handle functools.partial() nicely.
Description
	 
		(last modified by Nick Pope)
	 
When a partial function is passed as the view, the __repr__ shows the func argument as functools.partial which isn't very helpful, especially as it doesn't reveal the underlying function or arguments provided.
Because a partial function also has arguments provided up front, we need to handle those specially so that they are accessible in __repr__.
ISTM that we can simply unwrap functools.partial objects in ResolverMatch.__init__().


## Patch

```diff

diff --git a/django/urls/resolvers.py b/django/urls/resolvers.py
--- a/django/urls/resolvers.py
+++ b/django/urls/resolvers.py
@@ -59,9 +59,16 @@ def __getitem__(self, index):
         return (self.func, self.args, self.kwargs)[index]
 
     def __repr__(self):
-        return "ResolverMatch(func=%s, args=%s, kwargs=%s, url_name=%s, app_names=%s, namespaces=%s, route=%s)" % (
-            self._func_path, self.args, self.kwargs, self.url_name,
-            self.app_names, self.namespaces, self.route,
+        if isinstance(self.func, functools.partial):
+            func = repr(self.func)
+        else:
+            func = self._func_path
+        return (
+            'ResolverMatch(func=%s, args=%r, kwargs=%r, url_name=%r, '
+            'app_names=%r, namespaces=%r, route=%r)' % (
+                func, self.args, self.kwargs, self.url_name,
+                self.app_names, self.namespaces, self.route,
+            )
         )
 
 


```

## Test Patch

```diff
diff --git a/tests/urlpatterns_reverse/tests.py b/tests/urlpatterns_reverse/tests.py
--- a/tests/urlpatterns_reverse/tests.py
+++ b/tests/urlpatterns_reverse/tests.py
@@ -1141,10 +1141,30 @@ def test_repr(self):
         self.assertEqual(
             repr(resolve('/no_kwargs/42/37/')),
             "ResolverMatch(func=urlpatterns_reverse.views.empty_view, "
-            "args=('42', '37'), kwargs={}, url_name=no-kwargs, app_names=[], "
-            "namespaces=[], route=^no_kwargs/([0-9]+)/([0-9]+)/$)",
+            "args=('42', '37'), kwargs={}, url_name='no-kwargs', app_names=[], "
+            "namespaces=[], route='^no_kwargs/([0-9]+)/([0-9]+)/$')",
         )
 
+    @override_settings(ROOT_URLCONF='urlpatterns_reverse.urls')
+    def test_repr_functools_partial(self):
+        tests = [
+            ('partial', 'template.html'),
+            ('partial_nested', 'nested_partial.html'),
+            ('partial_wrapped', 'template.html'),
+        ]
+        for name, template_name in tests:
+            with self.subTest(name=name):
+                func = (
+                    f"functools.partial({views.empty_view!r}, "
+                    f"template_name='{template_name}')"
+                )
+                self.assertEqual(
+                    repr(resolve(f'/{name}/')),
+                    f"ResolverMatch(func={func}, args=(), kwargs={{}}, "
+                    f"url_name='{name}', app_names=[], namespaces=[], "
+                    f"route='{name}/')",
+                )
+
 
 @override_settings(ROOT_URLCONF='urlpatterns_reverse.erroneous_urls')
 class ErroneousViewTests(SimpleTestCase):

```

## Test Information

**Tests that should FAIL→PASS**: ["test_repr (urlpatterns_reverse.tests.ResolverMatchTests)", "test_repr_functools_partial (urlpatterns_reverse.tests.ResolverMatchTests)", "test_resolver_match_on_request (urlpatterns_reverse.tests.ResolverMatchTests)"]

**Tests that should PASS→PASS**: ["test_include_2_tuple (urlpatterns_reverse.tests.IncludeTests)", "test_include_2_tuple_namespace (urlpatterns_reverse.tests.IncludeTests)", "test_include_3_tuple (urlpatterns_reverse.tests.IncludeTests)", "test_include_3_tuple_namespace (urlpatterns_reverse.tests.IncludeTests)", "test_include_4_tuple (urlpatterns_reverse.tests.IncludeTests)", "test_include_app_name (urlpatterns_reverse.tests.IncludeTests)", "test_include_app_name_namespace (urlpatterns_reverse.tests.IncludeTests)", "test_include_namespace (urlpatterns_reverse.tests.IncludeTests)", "test_include_urls (urlpatterns_reverse.tests.IncludeTests)", "URLResolver should raise an exception when no urlpatterns exist.", "test_invalid_regex (urlpatterns_reverse.tests.ErroneousViewTests)", "test_noncallable_view (urlpatterns_reverse.tests.ErroneousViewTests)", "test_attributeerror_not_hidden (urlpatterns_reverse.tests.ViewLoadingTests)", "test_module_does_not_exist (urlpatterns_reverse.tests.ViewLoadingTests)", "test_non_string_value (urlpatterns_reverse.tests.ViewLoadingTests)", "test_not_callable (urlpatterns_reverse.tests.ViewLoadingTests)", "test_parent_module_does_not_exist (urlpatterns_reverse.tests.ViewLoadingTests)", "test_string_without_dot (urlpatterns_reverse.tests.ViewLoadingTests)", "test_view_does_not_exist (urlpatterns_reverse.tests.ViewLoadingTests)", "test_view_loading (urlpatterns_reverse.tests.ViewLoadingTests)", "test_callable_handlers (urlpatterns_reverse.tests.ErrorHandlerResolutionTests)", "test_named_handlers (urlpatterns_reverse.tests.ErrorHandlerResolutionTests)", "test_invalid_resolve (urlpatterns_reverse.tests.LookaheadTests)", "test_invalid_reverse (urlpatterns_reverse.tests.LookaheadTests)", "test_valid_resolve (urlpatterns_reverse.tests.LookaheadTests)", "test_valid_reverse (urlpatterns_reverse.tests.LookaheadTests)", "test_no_illegal_imports (urlpatterns_reverse.tests.ReverseShortcutTests)", "test_redirect_to_object (urlpatterns_reverse.tests.ReverseShortcutTests)", "test_redirect_to_url (urlpatterns_reverse.tests.ReverseShortcutTests)", "test_redirect_to_view_name (urlpatterns_reverse.tests.ReverseShortcutTests)", "test_redirect_view_object (urlpatterns_reverse.tests.ReverseShortcutTests)", "test_reverse_by_path_nested (urlpatterns_reverse.tests.ReverseShortcutTests)", "test_resolver_match_on_request_before_resolution (urlpatterns_reverse.tests.ResolverMatchTests)", "test_urlpattern_resolve (urlpatterns_reverse.tests.ResolverMatchTests)", "test_illegal_args_message (urlpatterns_reverse.tests.URLPatternReverse)", "test_illegal_kwargs_message (urlpatterns_reverse.tests.URLPatternReverse)", "test_mixing_args_and_kwargs (urlpatterns_reverse.tests.URLPatternReverse)", "test_no_args_message (urlpatterns_reverse.tests.URLPatternReverse)", "test_non_urlsafe_prefix_with_args (urlpatterns_reverse.tests.URLPatternReverse)", "test_patterns_reported (urlpatterns_reverse.tests.URLPatternReverse)", "test_prefix_braces (urlpatterns_reverse.tests.URLPatternReverse)", "test_prefix_format_char (urlpatterns_reverse.tests.URLPatternReverse)", "test_prefix_parenthesis (urlpatterns_reverse.tests.URLPatternReverse)", "test_reverse_none (urlpatterns_reverse.tests.URLPatternReverse)", "test_script_name_escaping (urlpatterns_reverse.tests.URLPatternReverse)", "test_urlpattern_reverse (urlpatterns_reverse.tests.URLPatternReverse)", "test_view_not_found_message (urlpatterns_reverse.tests.URLPatternReverse)", "test_build_absolute_uri (urlpatterns_reverse.tests.ReverseLazyTest)", "test_inserting_reverse_lazy_into_string (urlpatterns_reverse.tests.ReverseLazyTest)", "test_redirect_with_lazy_reverse (urlpatterns_reverse.tests.ReverseLazyTest)", "test_user_permission_with_lazy_reverse (urlpatterns_reverse.tests.ReverseLazyTest)", "Names deployed via dynamic URL objects that require namespaces can't", "A default application namespace can be used for lookup.", "A default application namespace is sensitive to the current app.", "An application namespace without a default is sensitive to the current", "Namespaces can be applied to include()'d urlpatterns that set an", "Dynamic URL objects can return a (pattern, app_name) 2-tuple, and", "Namespace defaults to app_name when including a (pattern, app_name)", "current_app shouldn't be used unless it matches the whole path.", "Namespaces can be installed anywhere in the URL pattern tree.", "Namespaces can be embedded.", "Dynamic URL objects can be found using a namespace.", "Namespaces can be applied to include()'d urlpatterns.", "Using include() with namespaces when there is a regex variable in front", "Namespace prefixes can capture variables.", "A nested current_app should be split in individual namespaces (#24904).", "Namespaces can be nested.", "Nonexistent namespaces raise errors.", "Normal lookups work as expected.", "Normal lookups work on names included from other patterns.", "test_special_chars_namespace (urlpatterns_reverse.tests.NamespaceTests)", "The list of URLs that come back from a Resolver404 exception contains", "test_namespaced_view_detail (urlpatterns_reverse.tests.ResolverTests)", "A Resolver404 is raised if resolving doesn't meet the basic", "URLResolver._populate() can be called concurrently, but not more", "Test repr of URLResolver, especially when urlconf_name is a list", "test_resolver_reverse (urlpatterns_reverse.tests.ResolverTests)", "URL pattern name arguments don't need to be unique. The last registered", "Verifies lazy object returned by reverse_lazy is coerced to", "test_view_detail_as_method (urlpatterns_reverse.tests.ResolverTests)", "Test reversing an URL from the *overridden* URLconf from inside", "Test reversing an URL from the *default* URLconf from inside", "test_urlconf (urlpatterns_reverse.tests.RequestURLconfTests)", "The URLconf is reset after each request.", "test_urlconf_overridden (urlpatterns_reverse.tests.RequestURLconfTests)", "Overriding request.urlconf with None will fall back to the default", "test_no_handler_exception (urlpatterns_reverse.tests.NoRootUrlConfTests)", "If the urls.py doesn't specify handlers, the defaults are used", "test_lazy_in_settings (urlpatterns_reverse.tests.ReverseLazySettingsTest)"]

**Base Commit**: 2f13c476abe4ba787b6cb71131818341911f43cc
**Environment Setup Commit**: 475cffd1d64c690cdad16ede4d5e81985738ceb4
