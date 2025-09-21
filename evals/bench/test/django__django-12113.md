# django__django-12113

**Repository**: django/django
**Created**: 2019-11-20T17:49:06Z
**Version**: 3.1

## Problem Statement

admin_views.test_multidb fails with persistent test SQLite database.
Description
	 
		(last modified by Mariusz Felisiak)
	 
I've tried using persistent SQLite databases for the tests (to make use of
--keepdb), but at least some test fails with:
sqlite3.OperationalError: database is locked
This is not an issue when only using TEST["NAME"] with "default" (which is good enough in terms of performance).
diff --git i/tests/test_sqlite.py w/tests/test_sqlite.py
index f1b65f7d01..9ce4e32e14 100644
--- i/tests/test_sqlite.py
+++ w/tests/test_sqlite.py
@@ -15,9 +15,15 @@
 DATABASES = {
	 'default': {
		 'ENGINE': 'django.db.backends.sqlite3',
+		'TEST': {
+			'NAME': 'test_default.sqlite3'
+		},
	 },
	 'other': {
		 'ENGINE': 'django.db.backends.sqlite3',
+		'TEST': {
+			'NAME': 'test_other.sqlite3'
+		},
	 }
 }
% tests/runtests.py admin_views.test_multidb -v 3 --keepdb --parallel 1
…
Operations to perform:
 Synchronize unmigrated apps: admin_views, auth, contenttypes, messages, sessions, staticfiles
 Apply all migrations: admin, sites
Running pre-migrate handlers for application contenttypes
Running pre-migrate handlers for application auth
Running pre-migrate handlers for application sites
Running pre-migrate handlers for application sessions
Running pre-migrate handlers for application admin
Running pre-migrate handlers for application admin_views
Synchronizing apps without migrations:
 Creating tables...
	Running deferred SQL...
Running migrations:
 No migrations to apply.
Running post-migrate handlers for application contenttypes
Running post-migrate handlers for application auth
Running post-migrate handlers for application sites
Running post-migrate handlers for application sessions
Running post-migrate handlers for application admin
Running post-migrate handlers for application admin_views
System check identified no issues (0 silenced).
ERROR
======================================================================
ERROR: setUpClass (admin_views.test_multidb.MultiDatabaseTests)
----------------------------------------------------------------------
Traceback (most recent call last):
 File "…/Vcs/django/django/db/backends/utils.py", line 84, in _execute
	return self.cursor.execute(sql, params)
 File "…/Vcs/django/django/db/backends/sqlite3/base.py", line 391, in execute
	return Database.Cursor.execute(self, query, params)
sqlite3.OperationalError: database is locked
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
 File "…/Vcs/django/django/test/testcases.py", line 1137, in setUpClass
	cls.setUpTestData()
 File "…/Vcs/django/tests/admin_views/test_multidb.py", line 40, in setUpTestData
	username='admin', password='something', email='test@test.org',
 File "…/Vcs/django/django/contrib/auth/models.py", line 158, in create_superuser
	return self._create_user(username, email, password, **extra_fields)
 File "…/Vcs/django/django/contrib/auth/models.py", line 141, in _create_user
	user.save(using=self._db)
 File "…/Vcs/django/django/contrib/auth/base_user.py", line 66, in save
	super().save(*args, **kwargs)
 File "…/Vcs/django/django/db/models/base.py", line 741, in save
	force_update=force_update, update_fields=update_fields)
 File "…/Vcs/django/django/db/models/base.py", line 779, in save_base
	force_update, using, update_fields,
 File "…/Vcs/django/django/db/models/base.py", line 870, in _save_table
	result = self._do_insert(cls._base_manager, using, fields, update_pk, raw)
 File "…/Vcs/django/django/db/models/base.py", line 908, in _do_insert
	using=using, raw=raw)
 File "…/Vcs/django/django/db/models/manager.py", line 82, in manager_method
	return getattr(self.get_queryset(), name)(*args, **kwargs)
 File "…/Vcs/django/django/db/models/query.py", line 1175, in _insert
	return query.get_compiler(using=using).execute_sql(return_id)
 File "…/Vcs/django/django/db/models/sql/compiler.py", line 1321, in execute_sql
	cursor.execute(sql, params)
 File "…/Vcs/django/django/db/backends/utils.py", line 67, in execute
	return self._execute_with_wrappers(sql, params, many=False, executor=self._execute)
 File "…/Vcs/django/django/db/backends/utils.py", line 76, in _execute_with_wrappers
	return executor(sql, params, many, context)
 File "…/Vcs/django/django/db/backends/utils.py", line 84, in _execute
	return self.cursor.execute(sql, params)
 File "…/Vcs/django/django/db/utils.py", line 89, in __exit__
	raise dj_exc_value.with_traceback(traceback) from exc_value
 File "…/Vcs/django/django/db/backends/utils.py", line 84, in _execute
	return self.cursor.execute(sql, params)
 File "…/Vcs/django/django/db/backends/sqlite3/base.py", line 391, in execute
	return Database.Cursor.execute(self, query, params)
django.db.utils.OperationalError: database is locked


## Hints

This is only an issue when setting TEST["NAME"], but not NAME. The following works: DATABASES = { 'default': { 'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'django_tests_default.sqlite3', }, 'other': { 'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'django_tests_other.sqlite3', } }
Reproduced at 0dd2308cf6f559a4f4b50edd7c005c7cf025d1aa.
Created ​PR
Hey, I am able to replicate this bug and was able to fix it as well with the help of ​https://github.com/django/django/pull/11678, but the point I am stuck at is how to test it, I am not able to manipulate the cls variable so the next option that is left is create a file like test_sqlite and pass it as a parameter in runtests, should I be doing that?
I think we should add tests/backends/sqlite/test_creation.py with regressions tests for test_db_signature(), you can take a look at tests/backends/base/test_creation.py with similar tests.

## Patch

```diff

diff --git a/django/db/backends/sqlite3/creation.py b/django/db/backends/sqlite3/creation.py
--- a/django/db/backends/sqlite3/creation.py
+++ b/django/db/backends/sqlite3/creation.py
@@ -98,4 +98,6 @@ def test_db_signature(self):
         sig = [self.connection.settings_dict['NAME']]
         if self.is_in_memory_db(test_database_name):
             sig.append(self.connection.alias)
+        else:
+            sig.append(test_database_name)
         return tuple(sig)


```

## Test Patch

```diff
diff --git a/tests/backends/sqlite/test_creation.py b/tests/backends/sqlite/test_creation.py
new file mode 100644
--- /dev/null
+++ b/tests/backends/sqlite/test_creation.py
@@ -0,0 +1,18 @@
+import copy
+import unittest
+
+from django.db import connection
+from django.test import SimpleTestCase
+
+
+@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests')
+class TestDbSignatureTests(SimpleTestCase):
+    def test_custom_test_name(self):
+        saved_settings = copy.deepcopy(connection.settings_dict)
+        try:
+            connection.settings_dict['NAME'] = None
+            connection.settings_dict['TEST']['NAME'] = 'custom.sqlite.db'
+            signature = connection.creation.test_db_signature()
+            self.assertEqual(signature, (None, 'custom.sqlite.db'))
+        finally:
+            connection.settings_dict = saved_settings

```

## Test Information

**Tests that should FAIL→PASS**: ["test_custom_test_name (backends.sqlite.test_creation.TestDbSignatureTests)"]

**Tests that should PASS→PASS**: []

**Base Commit**: 62254c5202e80a68f4fe6572a2be46a3d953de1a
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
