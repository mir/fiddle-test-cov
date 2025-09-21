# django__django-16255

**Repository**: django/django
**Created**: 2022-11-04T13:49:40Z
**Version**: 4.2

## Problem Statement

Sitemaps without items raise ValueError on callable lastmod.
Description
	
When sitemap contains not items, but supports returning lastmod for an item, it fails with a ValueError:
Traceback (most recent call last):
 File "/usr/local/lib/python3.10/site-packages/django/core/handlers/exception.py", line 55, in inner
	response = get_response(request)
 File "/usr/local/lib/python3.10/site-packages/django/core/handlers/base.py", line 197, in _get_response
	response = wrapped_callback(request, *callback_args, **callback_kwargs)
 File "/usr/local/lib/python3.10/site-packages/django/utils/decorators.py", line 133, in _wrapped_view
	response = view_func(request, *args, **kwargs)
 File "/usr/local/lib/python3.10/site-packages/django/contrib/sitemaps/views.py", line 34, in inner
	response = func(request, *args, **kwargs)
 File "/usr/local/lib/python3.10/site-packages/django/contrib/sitemaps/views.py", line 76, in index
	site_lastmod = site.get_latest_lastmod()
 File "/usr/local/lib/python3.10/site-packages/django/contrib/sitemaps/__init__.py", line 170, in get_latest_lastmod
	return max([self.lastmod(item) for item in self.items()])
Exception Type: ValueError at /sitemap.xml
Exception Value: max() arg is an empty sequence
Something like this might be a solution:
	 def get_latest_lastmod(self):
		 if not hasattr(self, "lastmod"):
			 return None
		 if callable(self.lastmod):
			 try:
				 return max([self.lastmod(item) for item in self.items()])
-			except TypeError:
+			except (TypeError, ValueError):
				 return None
		 else:
			 return self.lastmod


## Hints

Thanks for the report.
The default argument of max() can be used.

## Patch

```diff

diff --git a/django/contrib/sitemaps/__init__.py b/django/contrib/sitemaps/__init__.py
--- a/django/contrib/sitemaps/__init__.py
+++ b/django/contrib/sitemaps/__init__.py
@@ -167,7 +167,7 @@ def get_latest_lastmod(self):
             return None
         if callable(self.lastmod):
             try:
-                return max([self.lastmod(item) for item in self.items()])
+                return max([self.lastmod(item) for item in self.items()], default=None)
             except TypeError:
                 return None
         else:


```

## Test Patch

```diff
diff --git a/tests/sitemaps_tests/test_http.py b/tests/sitemaps_tests/test_http.py
--- a/tests/sitemaps_tests/test_http.py
+++ b/tests/sitemaps_tests/test_http.py
@@ -507,6 +507,16 @@ def test_callable_sitemod_full(self):
         self.assertXMLEqual(index_response.content.decode(), expected_content_index)
         self.assertXMLEqual(sitemap_response.content.decode(), expected_content_sitemap)
 
+    def test_callable_sitemod_no_items(self):
+        index_response = self.client.get("/callable-lastmod-no-items/index.xml")
+        self.assertNotIn("Last-Modified", index_response)
+        expected_content_index = """<?xml version="1.0" encoding="UTF-8"?>
+        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
+        <sitemap><loc>http://example.com/simple/sitemap-callable-lastmod.xml</loc></sitemap>
+        </sitemapindex>
+        """
+        self.assertXMLEqual(index_response.content.decode(), expected_content_index)
+
 
 # RemovedInDjango50Warning
 class DeprecatedTests(SitemapTestsBase):
diff --git a/tests/sitemaps_tests/urls/http.py b/tests/sitemaps_tests/urls/http.py
--- a/tests/sitemaps_tests/urls/http.py
+++ b/tests/sitemaps_tests/urls/http.py
@@ -114,6 +114,16 @@ def lastmod(self, obj):
         return obj.lastmod
 
 
+class CallableLastmodNoItemsSitemap(Sitemap):
+    location = "/location/"
+
+    def items(self):
+        return []
+
+    def lastmod(self, obj):
+        return obj.lastmod
+
+
 class GetLatestLastmodNoneSiteMap(Sitemap):
     changefreq = "never"
     priority = 0.5
@@ -233,6 +243,10 @@ def testmodelview(request, id):
     "callable-lastmod": CallableLastmodFullSitemap,
 }
 
+callable_lastmod_no_items_sitemap = {
+    "callable-lastmod": CallableLastmodNoItemsSitemap,
+}
+
 urlpatterns = [
     path("simple/index.xml", views.index, {"sitemaps": simple_sitemaps}),
     path("simple-paged/index.xml", views.index, {"sitemaps": simple_sitemaps_paged}),
@@ -417,6 +431,11 @@ def testmodelview(request, id):
         views.sitemap,
         {"sitemaps": callable_lastmod_full_sitemap},
     ),
+    path(
+        "callable-lastmod-no-items/index.xml",
+        views.index,
+        {"sitemaps": callable_lastmod_no_items_sitemap},
+    ),
     path(
         "generic-lastmod/index.xml",
         views.index,

```

## Test Information

**Tests that should FAIL→PASS**: ["test_callable_sitemod_no_items (sitemaps_tests.test_http.HTTPSitemapTests)"]

**Tests that should PASS→PASS**: ["A simple sitemap index can be rendered with a custom template", "test_simple_sitemap_custom_index_warning (sitemaps_tests.test_http.DeprecatedTests)", "A i18n sitemap with alternate/hreflang links can be rendered.", "A i18n sitemap index with limited languages can be rendered.", "A i18n sitemap index with x-default can be rendered.", "A cached sitemap index can be rendered (#2713).", "All items in the sitemap have `lastmod`. The `Last-Modified` header", "Not all items have `lastmod`. Therefore the `Last-Modified` header", "test_empty_page (sitemaps_tests.test_http.HTTPSitemapTests)", "test_empty_sitemap (sitemaps_tests.test_http.HTTPSitemapTests)", "The priority value should not be localized.", "test_no_section (sitemaps_tests.test_http.HTTPSitemapTests)", "test_page_not_int (sitemaps_tests.test_http.HTTPSitemapTests)", "A sitemap may have multiple pages.", "test_requestsite_sitemap (sitemaps_tests.test_http.HTTPSitemapTests)", "A simple sitemap can be rendered with a custom template", "A simple i18n sitemap index can be rendered, without logging variable", "A simple sitemap can be rendered", "A simple sitemap index can be rendered", "A simple sitemap section can be rendered", "sitemapindex.lastmod is included when Sitemap.lastmod is", "sitemapindex.lastmod is omitted when Sitemap.lastmod is", "Check we get ImproperlyConfigured if we don't pass a site object to", "Check we get ImproperlyConfigured when we don't pass a site object to", "Check to make sure that the raw item is included with each", "Last-Modified header is set correctly", "The Last-Modified header should be support dates (without time).", "Last-Modified header is missing when sitemap has no lastmod", "Last-Modified header is omitted when lastmod not on all items", "The Last-Modified header should be converted from timezone aware dates", "lastmod datestamp shows timezones if Sitemap.get_latest_lastmod", "A sitemap may not be callable.", "test_sitemap_without_entries (sitemaps_tests.test_http.HTTPSitemapTests)", "The Last-Modified header is set to the most recent sitemap lastmod.", "The Last-Modified header is omitted when lastmod isn't found in all", "test_x_robots_sitemap (sitemaps_tests.test_http.HTTPSitemapTests)"]

**Base Commit**: 444b6da7cc229a58a2c476a52e45233001dc7073
**Environment Setup Commit**: 0fbdb9784da915fce5dcc1fe82bac9b4785749e5
