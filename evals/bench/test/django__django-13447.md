# django__django-13447

**Repository**: django/django
**Created**: 2020-09-22T08:49:25Z
**Version**: 4.0

## Problem Statement

Added model class to app_list context
Description
	 
		(last modified by Raffaele Salmaso)
	 
I need to manipulate the app_list in my custom admin view, and the easiest way to get the result is to have access to the model class (currently the dictionary is a serialized model).
In addition I would make the _build_app_dict method public, as it is used by the two views index and app_index.


## Patch

```diff

diff --git a/django/contrib/admin/sites.py b/django/contrib/admin/sites.py
--- a/django/contrib/admin/sites.py
+++ b/django/contrib/admin/sites.py
@@ -461,6 +461,7 @@ def _build_app_dict(self, request, label=None):
 
             info = (app_label, model._meta.model_name)
             model_dict = {
+                'model': model,
                 'name': capfirst(model._meta.verbose_name_plural),
                 'object_name': model._meta.object_name,
                 'perms': perms,


```

## Test Patch

```diff
diff --git a/tests/admin_views/test_adminsite.py b/tests/admin_views/test_adminsite.py
--- a/tests/admin_views/test_adminsite.py
+++ b/tests/admin_views/test_adminsite.py
@@ -55,7 +55,9 @@ def test_available_apps(self):
         admin_views = apps[0]
         self.assertEqual(admin_views['app_label'], 'admin_views')
         self.assertEqual(len(admin_views['models']), 1)
-        self.assertEqual(admin_views['models'][0]['object_name'], 'Article')
+        article = admin_views['models'][0]
+        self.assertEqual(article['object_name'], 'Article')
+        self.assertEqual(article['model'], Article)
 
         # auth.User
         auth = apps[1]
@@ -63,6 +65,7 @@ def test_available_apps(self):
         self.assertEqual(len(auth['models']), 1)
         user = auth['models'][0]
         self.assertEqual(user['object_name'], 'User')
+        self.assertEqual(user['model'], User)
 
         self.assertEqual(auth['app_url'], '/test_admin/admin/auth/')
         self.assertIs(auth['has_module_perms'], True)

```

## Test Information

**Tests that should FAIL→PASS**: ["test_available_apps (admin_views.test_adminsite.SiteEachContextTest)"]

**Tests that should PASS→PASS**: ["test_add_action (admin_views.test_adminsite.SiteActionsTests)", "test_disable_action (admin_views.test_adminsite.SiteActionsTests)", "AdminSite.get_action() returns an action even if it's disabled.", "test_each_context (admin_views.test_adminsite.SiteEachContextTest)", "test_each_context_site_url_with_script_name (admin_views.test_adminsite.SiteEachContextTest)"]

**Base Commit**: 0456d3e42795481a186db05719300691fe2a1029
**Environment Setup Commit**: 475cffd1d64c690cdad16ede4d5e81985738ceb4
