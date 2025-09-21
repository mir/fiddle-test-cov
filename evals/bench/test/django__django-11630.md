# django__django-11630

**Repository**: django/django
**Created**: 2019-08-05T11:22:41Z
**Version**: 3.0

## Problem Statement

Django throws error when different apps with different models have the same name table name.
Description
	
Error message:
table_name: (models.E028) db_table 'table_name' is used by multiple models: base.ModelName, app2.ModelName.
We have a Base app that points to a central database and that has its own tables. We then have multiple Apps that talk to their own databases. Some share the same table names.
We have used this setup for a while, but after upgrading to Django 2.2 we're getting an error saying we're not allowed 2 apps, with 2 different models to have the same table names. 
Is this correct behavior? We've had to roll back to Django 2.0 for now.


## Hints

Regression in [5d25804eaf81795c7d457e5a2a9f0b9b0989136c], ticket #20098. My opinion is that as soon as the project has a non-empty DATABASE_ROUTERS setting, the error should be turned into a warning, as it becomes difficult to say for sure that it's an error. And then the project can add the warning in SILENCED_SYSTEM_CHECKS.
I agree with your opinion. Assigning to myself, patch on its way Replying to Claude Paroz: Regression in [5d25804eaf81795c7d457e5a2a9f0b9b0989136c], ticket #20098. My opinion is that as soon as the project has a non-empty DATABASE_ROUTERS setting, the error should be turned into a warning, as it becomes difficult to say for sure that it's an error. And then the project can add the warning in SILENCED_SYSTEM_CHECKS.

## Patch

```diff

diff --git a/django/core/checks/model_checks.py b/django/core/checks/model_checks.py
--- a/django/core/checks/model_checks.py
+++ b/django/core/checks/model_checks.py
@@ -4,7 +4,8 @@
 from itertools import chain
 
 from django.apps import apps
-from django.core.checks import Error, Tags, register
+from django.conf import settings
+from django.core.checks import Error, Tags, Warning, register
 
 
 @register(Tags.models)
@@ -35,14 +36,25 @@ def check_all_models(app_configs=None, **kwargs):
             indexes[model_index.name].append(model._meta.label)
         for model_constraint in model._meta.constraints:
             constraints[model_constraint.name].append(model._meta.label)
+    if settings.DATABASE_ROUTERS:
+        error_class, error_id = Warning, 'models.W035'
+        error_hint = (
+            'You have configured settings.DATABASE_ROUTERS. Verify that %s '
+            'are correctly routed to separate databases.'
+        )
+    else:
+        error_class, error_id = Error, 'models.E028'
+        error_hint = None
     for db_table, model_labels in db_table_models.items():
         if len(model_labels) != 1:
+            model_labels_str = ', '.join(model_labels)
             errors.append(
-                Error(
+                error_class(
                     "db_table '%s' is used by multiple models: %s."
-                    % (db_table, ', '.join(db_table_models[db_table])),
+                    % (db_table, model_labels_str),
                     obj=db_table,
-                    id='models.E028',
+                    hint=(error_hint % model_labels_str) if error_hint else None,
+                    id=error_id,
                 )
             )
     for index_name, model_labels in indexes.items():


```

## Test Patch

```diff
diff --git a/tests/check_framework/test_model_checks.py b/tests/check_framework/test_model_checks.py
--- a/tests/check_framework/test_model_checks.py
+++ b/tests/check_framework/test_model_checks.py
@@ -1,12 +1,16 @@
 from django.core import checks
-from django.core.checks import Error
+from django.core.checks import Error, Warning
 from django.db import models
 from django.test import SimpleTestCase, TestCase, skipUnlessDBFeature
 from django.test.utils import (
-    isolate_apps, modify_settings, override_system_checks,
+    isolate_apps, modify_settings, override_settings, override_system_checks,
 )
 
 
+class EmptyRouter:
+    pass
+
+
 @isolate_apps('check_framework', attr_name='apps')
 @override_system_checks([checks.model_checks.check_all_models])
 class DuplicateDBTableTests(SimpleTestCase):
@@ -28,6 +32,30 @@ class Meta:
             )
         ])
 
+    @override_settings(DATABASE_ROUTERS=['check_framework.test_model_checks.EmptyRouter'])
+    def test_collision_in_same_app_database_routers_installed(self):
+        class Model1(models.Model):
+            class Meta:
+                db_table = 'test_table'
+
+        class Model2(models.Model):
+            class Meta:
+                db_table = 'test_table'
+
+        self.assertEqual(checks.run_checks(app_configs=self.apps.get_app_configs()), [
+            Warning(
+                "db_table 'test_table' is used by multiple models: "
+                "check_framework.Model1, check_framework.Model2.",
+                hint=(
+                    'You have configured settings.DATABASE_ROUTERS. Verify '
+                    'that check_framework.Model1, check_framework.Model2 are '
+                    'correctly routed to separate databases.'
+                ),
+                obj='test_table',
+                id='models.W035',
+            )
+        ])
+
     @modify_settings(INSTALLED_APPS={'append': 'basic'})
     @isolate_apps('basic', 'check_framework', kwarg_name='apps')
     def test_collision_across_apps(self, apps):
@@ -50,6 +78,34 @@ class Meta:
             )
         ])
 
+    @modify_settings(INSTALLED_APPS={'append': 'basic'})
+    @override_settings(DATABASE_ROUTERS=['check_framework.test_model_checks.EmptyRouter'])
+    @isolate_apps('basic', 'check_framework', kwarg_name='apps')
+    def test_collision_across_apps_database_routers_installed(self, apps):
+        class Model1(models.Model):
+            class Meta:
+                app_label = 'basic'
+                db_table = 'test_table'
+
+        class Model2(models.Model):
+            class Meta:
+                app_label = 'check_framework'
+                db_table = 'test_table'
+
+        self.assertEqual(checks.run_checks(app_configs=apps.get_app_configs()), [
+            Warning(
+                "db_table 'test_table' is used by multiple models: "
+                "basic.Model1, check_framework.Model2.",
+                hint=(
+                    'You have configured settings.DATABASE_ROUTERS. Verify '
+                    'that basic.Model1, check_framework.Model2 are correctly '
+                    'routed to separate databases.'
+                ),
+                obj='test_table',
+                id='models.W035',
+            )
+        ])
+
     def test_no_collision_for_unmanaged_models(self):
         class Unmanaged(models.Model):
             class Meta:

```

## Test Information

**Tests that should FAIL→PASS**: ["test_collision_across_apps_database_routers_installed (check_framework.test_model_checks.DuplicateDBTableTests)", "test_collision_in_same_app_database_routers_installed (check_framework.test_model_checks.DuplicateDBTableTests)"]

**Tests that should PASS→PASS**: ["test_collision_abstract_model (check_framework.test_model_checks.IndexNameTests)", "test_collision_across_apps (check_framework.test_model_checks.IndexNameTests)", "test_collision_in_different_models (check_framework.test_model_checks.IndexNameTests)", "test_collision_in_same_model (check_framework.test_model_checks.IndexNameTests)", "test_no_collision_abstract_model_interpolation (check_framework.test_model_checks.IndexNameTests)", "test_no_collision_across_apps_interpolation (check_framework.test_model_checks.IndexNameTests)", "test_collision_abstract_model (check_framework.test_model_checks.ConstraintNameTests)", "test_collision_across_apps (check_framework.test_model_checks.ConstraintNameTests)", "test_collision_in_different_models (check_framework.test_model_checks.ConstraintNameTests)", "test_collision_in_same_model (check_framework.test_model_checks.ConstraintNameTests)", "test_no_collision_abstract_model_interpolation (check_framework.test_model_checks.ConstraintNameTests)", "test_no_collision_across_apps_interpolation (check_framework.test_model_checks.ConstraintNameTests)", "test_collision_across_apps (check_framework.test_model_checks.DuplicateDBTableTests)", "test_collision_in_same_app (check_framework.test_model_checks.DuplicateDBTableTests)", "test_no_collision_for_proxy_models (check_framework.test_model_checks.DuplicateDBTableTests)", "test_no_collision_for_unmanaged_models (check_framework.test_model_checks.DuplicateDBTableTests)"]

**Base Commit**: 65e86948b80262574058a94ccaae3a9b59c3faea
**Environment Setup Commit**: 419a78300f7cd27611196e1e464d50fd0385ff27
