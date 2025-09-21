# django__django-13448

**Repository**: django/django
**Created**: 2020-09-22T10:28:46Z
**Version**: 3.2

## Problem Statement

Test runner setup_databases crashes with "TEST": {"MIGRATE": False}.
Description
	
I'm trying to upgrade a project from Django 3.0 to Django 3.1 and wanted to try out the new "TEST": {"MIGRATE": False} database setting.
Sadly I'm running into an issue immediately when running ./manage.py test.
Removing the "TEST": {"MIGRATE": False} line allows the tests to run. So this is not blocking the upgrade for us, but it would be nice if we were able to use the new feature to skip migrations during testing.
For reference, this project was recently upgraded from Django 1.4 all the way to 3.0 so there might be some legacy cruft somewhere that triggers this.
Here's the trackeback. I'll try to debug this some more.
Traceback (most recent call last):
 File "/usr/local/lib/python3.6/site-packages/django/db/backends/utils.py", line 84, in _execute
	return self.cursor.execute(sql, params)
psycopg2.errors.UndefinedTable: relation "django_admin_log" does not exist
LINE 1: ...n_flag", "django_admin_log"."change_message" FROM "django_ad...
															 ^
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
 File "/usr/local/lib/python3.6/site-packages/django/db/models/sql/compiler.py", line 1156, in execute_sql
	cursor.execute(sql, params)
 File "/usr/local/lib/python3.6/site-packages/django/db/backends/utils.py", line 66, in execute
	return self._execute_with_wrappers(sql, params, many=False, executor=self._execute)
 File "/usr/local/lib/python3.6/site-packages/django/db/backends/utils.py", line 75, in _execute_with_wrappers
	return executor(sql, params, many, context)
 File "/usr/local/lib/python3.6/site-packages/django/db/backends/utils.py", line 84, in _execute
	return self.cursor.execute(sql, params)
 File "/usr/local/lib/python3.6/site-packages/django/db/utils.py", line 90, in __exit__
	raise dj_exc_value.with_traceback(traceback) from exc_value
 File "/usr/local/lib/python3.6/site-packages/django/db/backends/utils.py", line 84, in _execute
	return self.cursor.execute(sql, params)
django.db.utils.ProgrammingError: relation "django_admin_log" does not exist
LINE 1: ...n_flag", "django_admin_log"."change_message" FROM "django_ad...
															 ^
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
 File "./manage.py", line 15, in <module>
	main()
 File "./manage.py", line 11, in main
	execute_from_command_line(sys.argv)
 File "/usr/local/lib/python3.6/site-packages/django/core/management/__init__.py", line 401, in execute_from_command_line
	utility.execute()
 File "/usr/local/lib/python3.6/site-packages/django/core/management/__init__.py", line 395, in execute
	self.fetch_command(subcommand).run_from_argv(self.argv)
 File "/usr/local/lib/python3.6/site-packages/django/core/management/commands/test.py", line 23, in run_from_argv
	super().run_from_argv(argv)
 File "/usr/local/lib/python3.6/site-packages/django/core/management/base.py", line 330, in run_from_argv
	self.execute(*args, **cmd_options)
 File "/usr/local/lib/python3.6/site-packages/django/core/management/base.py", line 371, in execute
	output = self.handle(*args, **options)
 File "/usr/local/lib/python3.6/site-packages/django/core/management/commands/test.py", line 53, in handle
	failures = test_runner.run_tests(test_labels)
 File "/usr/local/lib/python3.6/site-packages/django/test/runner.py", line 695, in run_tests
	old_config = self.setup_databases(aliases=databases)
 File "/usr/local/lib/python3.6/site-packages/django/test/runner.py", line 616, in setup_databases
	self.parallel, **kwargs
 File "/usr/local/lib/python3.6/site-packages/django/test/utils.py", line 174, in setup_databases
	serialize=connection.settings_dict['TEST'].get('SERIALIZE', True),
 File "/usr/local/lib/python3.6/site-packages/django/db/backends/base/creation.py", line 78, in create_test_db
	self.connection._test_serialized_contents = self.serialize_db_to_string()
 File "/usr/local/lib/python3.6/site-packages/django/db/backends/base/creation.py", line 121, in serialize_db_to_string
	serializers.serialize("json", get_objects(), indent=None, stream=out)
 File "/usr/local/lib/python3.6/site-packages/django/core/serializers/__init__.py", line 128, in serialize
	s.serialize(queryset, **options)
 File "/usr/local/lib/python3.6/site-packages/django/core/serializers/base.py", line 90, in serialize
	for count, obj in enumerate(queryset, start=1):
 File "/usr/local/lib/python3.6/site-packages/django/db/backends/base/creation.py", line 118, in get_objects
	yield from queryset.iterator()
 File "/usr/local/lib/python3.6/site-packages/django/db/models/query.py", line 360, in _iterator
	yield from self._iterable_class(self, chunked_fetch=use_chunked_fetch, chunk_size=chunk_size)
 File "/usr/local/lib/python3.6/site-packages/django/db/models/query.py", line 53, in __iter__
	results = compiler.execute_sql(chunked_fetch=self.chunked_fetch, chunk_size=self.chunk_size)
 File "/usr/local/lib/python3.6/site-packages/django/db/models/sql/compiler.py", line 1159, in execute_sql
	cursor.close()
psycopg2.errors.InvalidCursorName: cursor "_django_curs_139860821038912_sync_1" does not exist


## Hints

Thanks for this report, now I see that we need to synchronize all apps when MIGRATE is False, see comment. I've totally missed this when reviewing f5ebdfce5c417f9844e86bccc2f12577064d4bad. We can remove the feature from 3.1 if fix is not trivial.
Mocking settings.MIGRATION_MODULES to None for all apps sounds like an easier fix, see draft below: diff --git a/django/db/backends/base/creation.py b/django/db/backends/base/creation.py index 503f7f56fd..3c0338d359 100644 --- a/django/db/backends/base/creation.py +++ b/django/db/backends/base/creation.py @@ -69,6 +69,22 @@ class BaseDatabaseCreation: database=self.connection.alias, run_syncdb=True, ) + else: + try: + old = settings.MIGRATION_MODULES + settings.MIGRATION_MODULES = { + app.label: None + for app in apps.get_app_configs() + } + call_command( + 'migrate', + verbosity=max(verbosity - 1, 0), + interactive=False, + database=self.connection.alias, + run_syncdb=True, + ) + finally: + settings.MIGRATION_MODULES = old # We then serialize the current state of the database into a string # and store it on the connection. This slightly horrific process is so people but I'm not convinced.
That seems similar to the solution I've been using for a while: class NoMigrations: """Disable migrations for all apps""" def __getitem__(self, item): return None def __contains__(self, item): return True MIGRATION_MODULES = NoMigrations() (Which I also suggested it as a temporary solution in the original ticket https://code.djangoproject.com/ticket/25388#comment:20) I hadn't actually tried this MIGRATION_MODULES override on this project before. I just did a test run with the override and or some reason I had to add a fixtures = ['myapp/initial_data.json'] line to some of the TestCase classes that worked fine without it before. It seems that these test cases really needed this fixture, but for some reason worked fine when migrations are enabled. Is (test) fixture loading somehow tied to migrations? Anyway, the tests work fine (the same 3 failures) with the MIGRATION_MODULES override, so it seems like it would be a reasonable alternative solution.
Is (test) fixture loading somehow tied to migrations? I don't think so, you've probably have these data somewhere is migrations.

## Patch

```diff

diff --git a/django/db/backends/base/creation.py b/django/db/backends/base/creation.py
--- a/django/db/backends/base/creation.py
+++ b/django/db/backends/base/creation.py
@@ -58,7 +58,14 @@ def create_test_db(self, verbosity=1, autoclobber=False, serialize=True, keepdb=
         settings.DATABASES[self.connection.alias]["NAME"] = test_database_name
         self.connection.settings_dict["NAME"] = test_database_name
 
-        if self.connection.settings_dict['TEST']['MIGRATE']:
+        try:
+            if self.connection.settings_dict['TEST']['MIGRATE'] is False:
+                # Disable migrations for all apps.
+                old_migration_modules = settings.MIGRATION_MODULES
+                settings.MIGRATION_MODULES = {
+                    app.label: None
+                    for app in apps.get_app_configs()
+                }
             # We report migrate messages at one level lower than that
             # requested. This ensures we don't get flooded with messages during
             # testing (unless you really ask to be flooded).
@@ -69,6 +76,9 @@ def create_test_db(self, verbosity=1, autoclobber=False, serialize=True, keepdb=
                 database=self.connection.alias,
                 run_syncdb=True,
             )
+        finally:
+            if self.connection.settings_dict['TEST']['MIGRATE'] is False:
+                settings.MIGRATION_MODULES = old_migration_modules
 
         # We then serialize the current state of the database into a string
         # and store it on the connection. This slightly horrific process is so people


```

## Test Patch

```diff
diff --git a/tests/backends/base/app_unmigrated/__init__.py b/tests/backends/base/app_unmigrated/__init__.py
new file mode 100644
diff --git a/tests/backends/base/app_unmigrated/migrations/0001_initial.py b/tests/backends/base/app_unmigrated/migrations/0001_initial.py
new file mode 100644
--- /dev/null
+++ b/tests/backends/base/app_unmigrated/migrations/0001_initial.py
@@ -0,0 +1,17 @@
+from django.db import migrations, models
+
+
+class Migration(migrations.Migration):
+    initial = True
+
+    dependencies = []
+
+    operations = [
+        migrations.CreateModel(
+            name='Foo',
+            fields=[
+                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('name', models.CharField(max_length=255)),
+            ],
+        ),
+    ]
diff --git a/tests/backends/base/app_unmigrated/migrations/__init__.py b/tests/backends/base/app_unmigrated/migrations/__init__.py
new file mode 100644
diff --git a/tests/backends/base/app_unmigrated/models.py b/tests/backends/base/app_unmigrated/models.py
new file mode 100644
--- /dev/null
+++ b/tests/backends/base/app_unmigrated/models.py
@@ -0,0 +1,8 @@
+from django.db import models
+
+
+class Foo(models.Model):
+    name = models.CharField(max_length=255)
+
+    class Meta:
+        app_label = 'app_unmigrated'
diff --git a/tests/backends/base/test_creation.py b/tests/backends/base/test_creation.py
--- a/tests/backends/base/test_creation.py
+++ b/tests/backends/base/test_creation.py
@@ -6,6 +6,7 @@
     TEST_DATABASE_PREFIX, BaseDatabaseCreation,
 )
 from django.test import SimpleTestCase, TransactionTestCase
+from django.test.utils import override_settings
 
 from ..models import (
     CircularA, CircularB, Object, ObjectReference, ObjectSelfReference,
@@ -49,31 +50,57 @@ def test_custom_test_name_with_test_prefix(self):
         self.assertEqual(signature[3], test_name)
 
 
+@override_settings(INSTALLED_APPS=['backends.base.app_unmigrated'])
 @mock.patch.object(connection, 'ensure_connection')
-@mock.patch('django.core.management.commands.migrate.Command.handle', return_value=None)
+@mock.patch.object(connection, 'prepare_database')
+@mock.patch('django.db.migrations.recorder.MigrationRecorder.has_table', return_value=False)
+@mock.patch('django.db.migrations.executor.MigrationExecutor.migrate')
+@mock.patch('django.core.management.commands.migrate.Command.sync_apps')
 class TestDbCreationTests(SimpleTestCase):
-    def test_migrate_test_setting_false(self, mocked_migrate, mocked_ensure_connection):
+    available_apps = ['backends.base.app_unmigrated']
+
+    def test_migrate_test_setting_false(self, mocked_sync_apps, mocked_migrate, *mocked_objects):
         test_connection = get_connection_copy()
         test_connection.settings_dict['TEST']['MIGRATE'] = False
         creation = test_connection.creation_class(test_connection)
+        if connection.vendor == 'oracle':
+            # Don't close connection on Oracle.
+            creation.connection.close = mock.Mock()
         old_database_name = test_connection.settings_dict['NAME']
         try:
             with mock.patch.object(creation, '_create_test_db'):
                 creation.create_test_db(verbosity=0, autoclobber=True, serialize=False)
-            mocked_migrate.assert_not_called()
+            # Migrations don't run.
+            mocked_migrate.assert_called()
+            args, kwargs = mocked_migrate.call_args
+            self.assertEqual(args, ([],))
+            self.assertEqual(kwargs['plan'], [])
+            # App is synced.
+            mocked_sync_apps.assert_called()
+            mocked_args, _ = mocked_sync_apps.call_args
+            self.assertEqual(mocked_args[1], {'app_unmigrated'})
         finally:
             with mock.patch.object(creation, '_destroy_test_db'):
                 creation.destroy_test_db(old_database_name, verbosity=0)
 
-    def test_migrate_test_setting_true(self, mocked_migrate, mocked_ensure_connection):
+    def test_migrate_test_setting_true(self, mocked_sync_apps, mocked_migrate, *mocked_objects):
         test_connection = get_connection_copy()
         test_connection.settings_dict['TEST']['MIGRATE'] = True
         creation = test_connection.creation_class(test_connection)
+        if connection.vendor == 'oracle':
+            # Don't close connection on Oracle.
+            creation.connection.close = mock.Mock()
         old_database_name = test_connection.settings_dict['NAME']
         try:
             with mock.patch.object(creation, '_create_test_db'):
                 creation.create_test_db(verbosity=0, autoclobber=True, serialize=False)
-            mocked_migrate.assert_called_once()
+            # Migrations run.
+            mocked_migrate.assert_called()
+            args, kwargs = mocked_migrate.call_args
+            self.assertEqual(args, ([('app_unmigrated', '0001_initial')],))
+            self.assertEqual(len(kwargs['plan']), 1)
+            # App is not synced.
+            mocked_sync_apps.assert_not_called()
         finally:
             with mock.patch.object(creation, '_destroy_test_db'):
                 creation.destroy_test_db(old_database_name, verbosity=0)

```

## Test Information

**Tests that should FAIL→PASS**: ["test_migrate_test_setting_false (backends.base.test_creation.TestDbCreationTests)"]

**Tests that should PASS→PASS**: ["test_custom_test_name (backends.base.test_creation.TestDbSignatureTests)", "test_custom_test_name_with_test_prefix (backends.base.test_creation.TestDbSignatureTests)", "test_default_name (backends.base.test_creation.TestDbSignatureTests)", "test_migrate_test_setting_true (backends.base.test_creation.TestDbCreationTests)", "test_circular_reference (backends.base.test_creation.TestDeserializeDbFromString)", "test_circular_reference_with_natural_key (backends.base.test_creation.TestDeserializeDbFromString)", "test_self_reference (backends.base.test_creation.TestDeserializeDbFromString)"]

**Base Commit**: 7b9596b974fb0ad1868b10c8c2174e10b72be403
**Environment Setup Commit**: 65dfb06a1ab56c238cc80f5e1c31f61210c4577d
