# django__django-11283

**Repository**: django/django
**Created**: 2019-04-26T07:02:50Z
**Version**: 3.0

## Problem Statement

Migration auth.0011_update_proxy_permissions fails for models recreated as a proxy.
Description
	 
		(last modified by Mariusz Felisiak)
	 
I am trying to update my project to Django 2.2. When I launch python manage.py migrate, I get this error message when migration auth.0011_update_proxy_permissions is applying (full stacktrace is available ​here):
django.db.utils.IntegrityError: duplicate key value violates unique constraint "idx_18141_auth_permission_content_type_id_01ab375a_uniq" DETAIL: Key (co.ntent_type_id, codename)=(12, add_agency) already exists.
It looks like the migration is trying to re-create already existing entries in the auth_permission table. At first I though it cloud because we recently renamed a model. But after digging and deleting the entries associated with the renamed model from our database in the auth_permission table, the problem still occurs with other proxy models.
I tried to update directly from 2.0.13 and 2.1.8. The issues appeared each time. I also deleted my venv and recreated it without an effect.
I searched for a ticket about this on the bug tracker but found nothing. I also posted this on ​django-users and was asked to report this here.


## Hints

Please provide a sample project or enough details to reproduce the issue.
Same problem for me. If a Permission exists already with the new content_type and permission name, IntegrityError is raised since it violates the unique_key constraint on permission model i.e. content_type_id_code_name
To get into the situation where you already have permissions with the content type you should be able to do the following: Start on Django <2.2 Create a model called 'TestModel' Migrate Delete the model called 'TestModel' Add a new proxy model called 'TestModel' Migrate Update to Django >=2.2 Migrate We think this is what happened in our case where we found this issue (​https://sentry.thalia.nu/share/issue/68be0f8c32764dec97855b3cbb3d8b55/). We have a proxy model with the same name that a previous non-proxy model once had. This changed during a refactor and the permissions + content type for the original model still exist. Our solution will probably be removing the existing permissions from the table, but that's really only a workaround.
Reproduced with steps from comment. It's probably regression in 181fb60159e54d442d3610f4afba6f066a6dac05.
What happens when creating a regular model, deleting it and creating a new proxy model: Create model 'RegularThenProxyModel' +----------------------------------+---------------------------+-----------------------+ | name | codename | model | +----------------------------------+---------------------------+-----------------------+ | Can add regular then proxy model | add_regularthenproxymodel | regularthenproxymodel | +----------------------------------+---------------------------+-----------------------+ Migrate Delete the model called 'RegularThenProxyModel' Add a new proxy model called 'RegularThenProxyModel' +----------------------------------+---------------------------+-----------------------+ | name | codename | model | +----------------------------------+---------------------------+-----------------------+ | Can add concrete model | add_concretemodel | concretemodel | | Can add regular then proxy model | add_regularthenproxymodel | concretemodel | | Can add regular then proxy model | add_regularthenproxymodel | regularthenproxymodel | +----------------------------------+---------------------------+-----------------------+ What happens when creating a proxy model right away: Create a proxy model 'RegularThenProxyModel' +----------------------------------+---------------------------+---------------+ | name | codename | model | +----------------------------------+---------------------------+---------------+ | Can add concrete model | add_concretemodel | concretemodel | | Can add regular then proxy model | add_regularthenproxymodel | concretemodel | +----------------------------------+---------------------------+---------------+ As you can see, the problem here is that permissions are not cleaned up, so we are left with an existing | Can add regular then proxy model | add_regularthenproxymodel | regularthenproxymodel | row. When the 2.2 migration is applied, it tries to create that exact same row, hence the IntegrityError. Unfortunately, there is no remove_stale_permission management command like the one for ContentType. So I think we can do one of the following: Show a nice error message to let the user delete the conflicting migration OR Re-use the existing permission I think 1. is much safer as it will force users to use a new permission and assign it accordingly to users/groups. Edit: I revised my initial comment after reproducing the error in my environment.
It's also possible to get this kind of integrity error on the auth.0011 migration if another app is migrated first causing the auth post_migrations hook to run. The auth post migrations hook runs django.contrib.auth.management.create_permissions, which writes the new form of the auth_permission records to the table. Then when the auth.0011 migration runs it tries to update things to the values that were just written. To reproduce this behavior: pip install Django==2.1.7 Create an app, let's call it app, with two models, TestModel(models.Model) and ProxyModel(TestModel) the second one with proxy=True python manage.py makemigrations python manage.py migrate pip install Django==2.2 Add another model to app python manage.py makemigrations migrate the app only, python manage.py migrate app. This does not run the auth migrations, but does run the auth post_migrations hook Note that new records have been added to auth_permission python manage.py migrate, this causes an integrity error when the auth.0011 migration tries to update records that are the same as the ones already added in step 8. This has the same exception as this bug report, I don't know if it's considered a different bug, or the same one.
Yes it is the same issue. My recommendation to let the users figure it out with a helpful message still stands even if it may sound a bit painful, because: It prevents data loss (we don't do an automatic delete/create of permissions) It prevents security oversights (we don't re-use an existing permission) It shouldn't happen for most use cases Again, I would love to hear some feedback or other alternatives.
I won’t have time to work on this for the next 2 weeks so I’m de-assigning myself. I’ll pick it up again if nobody does and I’m available to discuss feedback/suggestions.
I'll make a patch for this. I'll see about raising a suitable warning from the migration but we already warn in the release notes for this to audit permissions: my initial thought was that re-using the permission would be OK. (I see Arthur's comment. Other thoughts?)
Being my first contribution I wanted to be super (super) careful with security concerns, but given the existing warning in the release notes for auditing prior to update, I agree that re-using the permission feels pretty safe and would remove overhead for people running into this scenario. Thanks for taking this on Carlton, I'd be happy to review.

## Patch

```diff

diff --git a/django/contrib/auth/migrations/0011_update_proxy_permissions.py b/django/contrib/auth/migrations/0011_update_proxy_permissions.py
--- a/django/contrib/auth/migrations/0011_update_proxy_permissions.py
+++ b/django/contrib/auth/migrations/0011_update_proxy_permissions.py
@@ -1,5 +1,18 @@
-from django.db import migrations
+import sys
+
+from django.core.management.color import color_style
+from django.db import migrations, transaction
 from django.db.models import Q
+from django.db.utils import IntegrityError
+
+WARNING = """
+    A problem arose migrating proxy model permissions for {old} to {new}.
+
+      Permission(s) for {new} already existed.
+      Codenames Q: {query}
+
+    Ensure to audit ALL permissions for {old} and {new}.
+"""
 
 
 def update_proxy_model_permissions(apps, schema_editor, reverse=False):
@@ -7,6 +20,7 @@ def update_proxy_model_permissions(apps, schema_editor, reverse=False):
     Update the content_type of proxy model permissions to use the ContentType
     of the proxy model.
     """
+    style = color_style()
     Permission = apps.get_model('auth', 'Permission')
     ContentType = apps.get_model('contenttypes', 'ContentType')
     for Model in apps.get_models():
@@ -24,10 +38,16 @@ def update_proxy_model_permissions(apps, schema_editor, reverse=False):
         proxy_content_type = ContentType.objects.get_for_model(Model, for_concrete_model=False)
         old_content_type = proxy_content_type if reverse else concrete_content_type
         new_content_type = concrete_content_type if reverse else proxy_content_type
-        Permission.objects.filter(
-            permissions_query,
-            content_type=old_content_type,
-        ).update(content_type=new_content_type)
+        try:
+            with transaction.atomic():
+                Permission.objects.filter(
+                    permissions_query,
+                    content_type=old_content_type,
+                ).update(content_type=new_content_type)
+        except IntegrityError:
+            old = '{}_{}'.format(old_content_type.app_label, old_content_type.model)
+            new = '{}_{}'.format(new_content_type.app_label, new_content_type.model)
+            sys.stdout.write(style.WARNING(WARNING.format(old=old, new=new, query=permissions_query)))
 
 
 def revert_proxy_model_permissions(apps, schema_editor):


```

## Test Patch

```diff
diff --git a/tests/auth_tests/test_migrations.py b/tests/auth_tests/test_migrations.py
--- a/tests/auth_tests/test_migrations.py
+++ b/tests/auth_tests/test_migrations.py
@@ -4,6 +4,7 @@
 from django.contrib.auth.models import Permission, User
 from django.contrib.contenttypes.models import ContentType
 from django.test import TestCase
+from django.test.utils import captured_stdout
 
 from .models import Proxy, UserProxy
 
@@ -152,3 +153,27 @@ def test_user_keeps_same_permissions_after_migrating_backward(self):
         user = User._default_manager.get(pk=user.pk)
         for permission in [self.default_permission, self.custom_permission]:
             self.assertTrue(user.has_perm('auth_tests.' + permission.codename))
+
+    def test_migrate_with_existing_target_permission(self):
+        """
+        Permissions may already exist:
+
+        - Old workaround was to manually create permissions for proxy models.
+        - Model may have been concrete and then converted to proxy.
+
+        Output a reminder to audit relevant permissions.
+        """
+        proxy_model_content_type = ContentType.objects.get_for_model(Proxy, for_concrete_model=False)
+        Permission.objects.create(
+            content_type=proxy_model_content_type,
+            codename='add_proxy',
+            name='Can add proxy',
+        )
+        Permission.objects.create(
+            content_type=proxy_model_content_type,
+            codename='display_proxys',
+            name='May display proxys information',
+        )
+        with captured_stdout() as stdout:
+            update_proxy_permissions.update_proxy_model_permissions(apps, None)
+        self.assertIn('A problem arose migrating proxy model permissions', stdout.getvalue())

```

## Test Information

**Tests that should FAIL→PASS**: ["test_migrate_with_existing_target_permission (auth_tests.test_migrations.ProxyModelWithSameAppLabelTests)"]

**Tests that should PASS→PASS**: ["test_migrate_backwards (auth_tests.test_migrations.ProxyModelWithDifferentAppLabelTests)", "test_proxy_model_permissions_contenttype (auth_tests.test_migrations.ProxyModelWithDifferentAppLabelTests)", "test_user_has_now_proxy_model_permissions (auth_tests.test_migrations.ProxyModelWithDifferentAppLabelTests)", "test_user_keeps_same_permissions_after_migrating_backward (auth_tests.test_migrations.ProxyModelWithDifferentAppLabelTests)", "test_migrate_backwards (auth_tests.test_migrations.ProxyModelWithSameAppLabelTests)", "test_proxy_model_permissions_contenttype (auth_tests.test_migrations.ProxyModelWithSameAppLabelTests)", "test_user_keeps_same_permissions_after_migrating_backward (auth_tests.test_migrations.ProxyModelWithSameAppLabelTests)", "test_user_still_has_proxy_model_permissions (auth_tests.test_migrations.ProxyModelWithSameAppLabelTests)"]

**Base Commit**: 08a4ee06510ae45562c228eefbdcaac84bd38c7a
**Environment Setup Commit**: 419a78300f7cd27611196e1e464d50fd0385ff27
