# django__django-13925

**Repository**: django/django
**Created**: 2021-01-21T08:08:55Z
**Version**: 4.0

## Problem Statement

models.W042 is raised on inherited manually specified primary key.
Description
	
I have models which inherit from other models, and they should inherit the primary key. This works fine with Django 3.1. However, if I install Django 3.2 alpha, when I run make_migrations I get the following error messages:
System check identified some issues:
WARNINGS:
accounts.ReservedUsername: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the SpeedyCoreAccountsConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
accounts.User: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the SpeedyCoreAccountsConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
blocks.Block: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
contact_by_form.Feedback: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the SpeedyCoreContactByFormConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
core_messages.ReadMark: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the SpeedyCoreMessagesConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
friendship.Block: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
friendship.Follow: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
friendship.Friend: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
friendship.FriendshipRequest: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
likes.UserLike: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
uploads.Image: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
These models should not use auto-created primary keys! I already defined the primary key in the ancestor of the model. For example class Entity which class User inherits from. It looks to me like a bug in Django 3.2 alpha.


## Hints

Hello Uri, thanks for testing out the alpha and the report. These models should not use auto-created primary keys! I already defined the primary key in the ancestor of the model. For example class Entity which class User inherits from. It looks to me like a bug in Django 3.2 alpha. Could you provide a minimal project with a set of models to reproduce the issue. I tried the following but couldn't reproduce from django.db import models class Entity(models.Model): id = models.AutoField(primary_key=True) class User(Entity): pass Also neither the User or Entity models are mentioned in your check failures above.
Replying to Simon Charette: Hello Uri, thanks for testing out the alpha and the report. These models should not use auto-created primary keys! I already defined the primary key in the ancestor of the model. For example class Entity which class User inherits from. It looks to me like a bug in Django 3.2 alpha. Could you provide a minimal project with a set of models to reproduce the issue. I tried the following but couldn't reproduce from django.db import models class Entity(models.Model): id = models.AutoField(primary_key=True) class User(Entity): pass Also neither the User or Entity models are mentioned in your check failures above. Hi Simon, Notice that accounts.User above is class User in the accounts app. I'm not sure if I can provide a minimal project as you requested, but you can see my code on GitHub. For example the models of the accounts app are here: ​https://github.com/speedy-net/speedy-net/blob/master/speedy/core/accounts/models.py (Search for "class Entity" and "class User". The id = SmallUDIDField() field in class Entity is the primary key. It also works for getting a User model by User.objects.get(pk=...). Also same is for class ReservedUsername above, which is a much more simpler model than class User. The definition of SmallUDIDField above (the primary key field) is on ​https://github.com/speedy-net/speedy-net/blob/master/speedy/core/base/fields.py .
Thanks for the report. Reproduced at bbd18943c6c00fb1386ecaaf6771a54f780ebf62. Bug in b5e12d490af3debca8c55ab3c1698189fdedbbdb.
Regression test.
Shouldn't the Child class inherits from Parent in the regression test? class Child(Parent): pass

## Patch

```diff

diff --git a/django/db/models/base.py b/django/db/models/base.py
--- a/django/db/models/base.py
+++ b/django/db/models/base.py
@@ -1299,6 +1299,11 @@ def check(cls, **kwargs):
     def _check_default_pk(cls):
         if (
             cls._meta.pk.auto_created and
+            # Inherited PKs are checked in parents models.
+            not (
+                isinstance(cls._meta.pk, OneToOneField) and
+                cls._meta.pk.remote_field.parent_link
+            ) and
             not settings.is_overridden('DEFAULT_AUTO_FIELD') and
             not cls._meta.app_config._is_default_auto_field_overridden
         ):


```

## Test Patch

```diff
diff --git a/tests/check_framework/test_model_checks.py b/tests/check_framework/test_model_checks.py
--- a/tests/check_framework/test_model_checks.py
+++ b/tests/check_framework/test_model_checks.py
@@ -376,23 +376,62 @@ def mocked_is_overridden(self, setting):
 @isolate_apps('check_framework.apps.CheckDefaultPKConfig', attr_name='apps')
 @override_system_checks([checks.model_checks.check_all_models])
 class ModelDefaultAutoFieldTests(SimpleTestCase):
+    msg = (
+        "Auto-created primary key used when not defining a primary key type, "
+        "by default 'django.db.models.AutoField'."
+    )
+    hint = (
+        "Configure the DEFAULT_AUTO_FIELD setting or the "
+        "CheckDefaultPKConfig.default_auto_field attribute to point to a "
+        "subclass of AutoField, e.g. 'django.db.models.BigAutoField'."
+    )
+
     def test_auto_created_pk(self):
         class Model(models.Model):
             pass
 
         self.assertEqual(checks.run_checks(app_configs=self.apps.get_app_configs()), [
-            Warning(
-                "Auto-created primary key used when not defining a primary "
-                "key type, by default 'django.db.models.AutoField'.",
-                hint=(
-                    "Configure the DEFAULT_AUTO_FIELD setting or the "
-                    "CheckDefaultPKConfig.default_auto_field attribute to "
-                    "point to a subclass of AutoField, e.g. "
-                    "'django.db.models.BigAutoField'."
-                ),
-                obj=Model,
-                id='models.W042',
-            ),
+            Warning(self.msg, hint=self.hint, obj=Model, id='models.W042'),
+        ])
+
+    def test_explicit_inherited_pk(self):
+        class Parent(models.Model):
+            id = models.AutoField(primary_key=True)
+
+        class Child(Parent):
+            pass
+
+        self.assertEqual(checks.run_checks(app_configs=self.apps.get_app_configs()), [])
+
+    def test_explicit_inherited_parent_link(self):
+        class Parent(models.Model):
+            id = models.AutoField(primary_key=True)
+
+        class Child(Parent):
+            parent_ptr = models.OneToOneField(Parent, models.CASCADE, parent_link=True)
+
+        self.assertEqual(checks.run_checks(app_configs=self.apps.get_app_configs()), [])
+
+    def test_auto_created_inherited_pk(self):
+        class Parent(models.Model):
+            pass
+
+        class Child(Parent):
+            pass
+
+        self.assertEqual(checks.run_checks(app_configs=self.apps.get_app_configs()), [
+            Warning(self.msg, hint=self.hint, obj=Parent, id='models.W042'),
+        ])
+
+    def test_auto_created_inherited_parent_link(self):
+        class Parent(models.Model):
+            pass
+
+        class Child(Parent):
+            parent_ptr = models.OneToOneField(Parent, models.CASCADE, parent_link=True)
+
+        self.assertEqual(checks.run_checks(app_configs=self.apps.get_app_configs()), [
+            Warning(self.msg, hint=self.hint, obj=Parent, id='models.W042'),
         ])
 
     @override_settings(DEFAULT_AUTO_FIELD='django.db.models.BigAutoField')

```

## Test Information

**Tests that should FAIL→PASS**: ["test_auto_created_inherited_pk (check_framework.test_model_checks.ModelDefaultAutoFieldTests)", "test_explicit_inherited_pk (check_framework.test_model_checks.ModelDefaultAutoFieldTests)"]

**Tests that should PASS→PASS**: ["test_app_default_auto_field (check_framework.test_model_checks.ModelDefaultAutoFieldTests)", "test_auto_created_inherited_parent_link (check_framework.test_model_checks.ModelDefaultAutoFieldTests)", "test_auto_created_pk (check_framework.test_model_checks.ModelDefaultAutoFieldTests)", "test_default_auto_field_setting (check_framework.test_model_checks.ModelDefaultAutoFieldTests)", "test_explicit_inherited_parent_link (check_framework.test_model_checks.ModelDefaultAutoFieldTests)", "test_explicit_pk (check_framework.test_model_checks.ModelDefaultAutoFieldTests)", "test_collision_abstract_model (check_framework.test_model_checks.IndexNameTests)", "test_collision_across_apps (check_framework.test_model_checks.IndexNameTests)", "test_collision_in_different_models (check_framework.test_model_checks.IndexNameTests)", "test_collision_in_same_model (check_framework.test_model_checks.IndexNameTests)", "test_no_collision_abstract_model_interpolation (check_framework.test_model_checks.IndexNameTests)", "test_no_collision_across_apps_interpolation (check_framework.test_model_checks.IndexNameTests)", "test_collision_abstract_model (check_framework.test_model_checks.ConstraintNameTests)", "test_collision_across_apps (check_framework.test_model_checks.ConstraintNameTests)", "test_collision_in_different_models (check_framework.test_model_checks.ConstraintNameTests)", "test_collision_in_same_model (check_framework.test_model_checks.ConstraintNameTests)", "test_no_collision_abstract_model_interpolation (check_framework.test_model_checks.ConstraintNameTests)", "test_no_collision_across_apps_interpolation (check_framework.test_model_checks.ConstraintNameTests)", "test_collision_across_apps (check_framework.test_model_checks.DuplicateDBTableTests)", "test_collision_across_apps_database_routers_installed (check_framework.test_model_checks.DuplicateDBTableTests)", "test_collision_in_same_app (check_framework.test_model_checks.DuplicateDBTableTests)", "test_collision_in_same_app_database_routers_installed (check_framework.test_model_checks.DuplicateDBTableTests)", "test_no_collision_for_proxy_models (check_framework.test_model_checks.DuplicateDBTableTests)", "test_no_collision_for_unmanaged_models (check_framework.test_model_checks.DuplicateDBTableTests)"]

**Base Commit**: 0c42cdf0d2422f4c080e93594d5d15381d6e955e
**Environment Setup Commit**: 475cffd1d64c690cdad16ede4d5e81985738ceb4
