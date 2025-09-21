# django__django-11039

**Repository**: django/django
**Created**: 2019-03-01T10:24:38Z
**Version**: 3.0

## Problem Statement

sqlmigrate wraps it's outpout in BEGIN/COMMIT even if the database doesn't support transactional DDL
Description
	 
		(last modified by Simon Charette)
	 
The migration executor only adds the outer BEGIN/COMMIT ​if the migration is atomic and ​the schema editor can rollback DDL but the current sqlmigrate logic only takes migration.atomic into consideration.
The issue can be addressed by
Changing sqlmigrate ​assignment of self.output_transaction to consider connection.features.can_rollback_ddl as well.
Adding a test in tests/migrations/test_commands.py based on ​an existing test for non-atomic migrations that mocks connection.features.can_rollback_ddl to False instead of overdidding MIGRATION_MODULES to point to a non-atomic migration.
I marked the ticket as easy picking because I included the above guidelines but feel free to uncheck it if you deem it inappropriate.


## Hints

I marked the ticket as easy picking because I included the above guidelines but feel free to uncheck it if you deem it inappropriate. Super. We don't have enough Easy Pickings tickets for the demand, so this kind of thing is great. (IMO 🙂)
Hey, I'm working on this ticket, I would like you to know as this is my first ticket it may take little longer to complete :). Here is a ​| link to the working branch You may feel free to post references or elaborate more on the topic.
Hi Parth. No problem. If you need help please reach out to e.g. ​django-core-mentorship citing this issue, and where you've got to/got stuck. Welcome aboard, and have fun! ✨

## Patch

```diff

diff --git a/django/core/management/commands/sqlmigrate.py b/django/core/management/commands/sqlmigrate.py
--- a/django/core/management/commands/sqlmigrate.py
+++ b/django/core/management/commands/sqlmigrate.py
@@ -55,8 +55,9 @@ def handle(self, *args, **options):
                 migration_name, app_label))
         targets = [(app_label, migration.name)]
 
-        # Show begin/end around output only for atomic migrations
-        self.output_transaction = migration.atomic
+        # Show begin/end around output for atomic migrations, if the database
+        # supports transactional DDL.
+        self.output_transaction = migration.atomic and connection.features.can_rollback_ddl
 
         # Make a plan that represents just the requested migrations and show SQL
         # for it


```

## Test Patch

```diff
diff --git a/tests/migrations/test_commands.py b/tests/migrations/test_commands.py
--- a/tests/migrations/test_commands.py
+++ b/tests/migrations/test_commands.py
@@ -536,7 +536,13 @@ def test_sqlmigrate_forwards(self):
         index_op_desc_unique_together = output.find('-- alter unique_together')
         index_tx_end = output.find(connection.ops.end_transaction_sql().lower())
 
-        self.assertGreater(index_tx_start, -1, "Transaction start not found")
+        if connection.features.can_rollback_ddl:
+            self.assertGreater(index_tx_start, -1, "Transaction start not found")
+            self.assertGreater(
+                index_tx_end, index_op_desc_unique_together,
+                "Transaction end not found or found before operation description (unique_together)"
+            )
+
         self.assertGreater(
             index_op_desc_author, index_tx_start,
             "Operation description (author) not found or found before transaction start"
@@ -553,10 +559,6 @@ def test_sqlmigrate_forwards(self):
             index_op_desc_unique_together, index_op_desc_tribble,
             "Operation description (unique_together) not found or found before operation description (tribble)"
         )
-        self.assertGreater(
-            index_tx_end, index_op_desc_unique_together,
-            "Transaction end not found or found before operation description (unique_together)"
-        )
 
     @override_settings(MIGRATION_MODULES={"migrations": "migrations.test_migrations"})
     def test_sqlmigrate_backwards(self):
@@ -577,7 +579,12 @@ def test_sqlmigrate_backwards(self):
         index_drop_table = output.rfind('drop table')
         index_tx_end = output.find(connection.ops.end_transaction_sql().lower())
 
-        self.assertGreater(index_tx_start, -1, "Transaction start not found")
+        if connection.features.can_rollback_ddl:
+            self.assertGreater(index_tx_start, -1, "Transaction start not found")
+            self.assertGreater(
+                index_tx_end, index_op_desc_unique_together,
+                "Transaction end not found or found before DROP TABLE"
+            )
         self.assertGreater(
             index_op_desc_unique_together, index_tx_start,
             "Operation description (unique_together) not found or found before transaction start"
@@ -595,10 +602,6 @@ def test_sqlmigrate_backwards(self):
             index_drop_table, index_op_desc_author,
             "DROP TABLE not found or found before operation description (author)"
         )
-        self.assertGreater(
-            index_tx_end, index_op_desc_unique_together,
-            "Transaction end not found or found before DROP TABLE"
-        )
 
         # Cleanup by unmigrating everything
         call_command("migrate", "migrations", "zero", verbosity=0)
@@ -616,6 +619,22 @@ def test_sqlmigrate_for_non_atomic_migration(self):
             self.assertNotIn(connection.ops.start_transaction_sql().lower(), queries)
         self.assertNotIn(connection.ops.end_transaction_sql().lower(), queries)
 
+    @override_settings(MIGRATION_MODULES={'migrations': 'migrations.test_migrations'})
+    def test_sqlmigrate_for_non_transactional_databases(self):
+        """
+        Transaction wrappers aren't shown for databases that don't support
+        transactional DDL.
+        """
+        out = io.StringIO()
+        with mock.patch.object(connection.features, 'can_rollback_ddl', False):
+            call_command('sqlmigrate', 'migrations', '0001', stdout=out)
+        output = out.getvalue().lower()
+        queries = [q.strip() for q in output.splitlines()]
+        start_transaction_sql = connection.ops.start_transaction_sql()
+        if start_transaction_sql:
+            self.assertNotIn(start_transaction_sql.lower(), queries)
+        self.assertNotIn(connection.ops.end_transaction_sql().lower(), queries)
+
     @override_settings(
         INSTALLED_APPS=[
             "migrations.migrations_test_apps.migrated_app",

```

## Test Information

**Tests that should FAIL→PASS**: ["test_sqlmigrate_for_non_transactional_databases (migrations.test_commands.MigrateTests)"]

**Tests that should PASS→PASS**: ["test_makemigrations_app_name_specified_as_label (migrations.test_commands.AppLabelErrorTests)", "test_makemigrations_nonexistent_app_label (migrations.test_commands.AppLabelErrorTests)", "test_migrate_app_name_specified_as_label (migrations.test_commands.AppLabelErrorTests)", "test_migrate_nonexistent_app_label (migrations.test_commands.AppLabelErrorTests)", "test_showmigrations_app_name_specified_as_label (migrations.test_commands.AppLabelErrorTests)", "test_showmigrations_nonexistent_app_label (migrations.test_commands.AppLabelErrorTests)", "test_sqlmigrate_app_name_specified_as_label (migrations.test_commands.AppLabelErrorTests)", "test_sqlmigrate_nonexistent_app_label (migrations.test_commands.AppLabelErrorTests)", "test_squashmigrations_app_name_specified_as_label (migrations.test_commands.AppLabelErrorTests)", "test_squashmigrations_nonexistent_app_label (migrations.test_commands.AppLabelErrorTests)", "--squashed-name specifies the new migration's name.", "--squashed-name also works if a start migration is omitted.", "test_squashmigrations_initial_attribute (migrations.test_commands.SquashMigrationsTests)", "test_squashmigrations_invalid_start (migrations.test_commands.SquashMigrationsTests)", "test_squashmigrations_optimizes (migrations.test_commands.SquashMigrationsTests)", "test_squashmigrations_squashes (migrations.test_commands.SquashMigrationsTests)", "test_squashmigrations_valid_start (migrations.test_commands.SquashMigrationsTests)", "test_ticket_23799_squashmigrations_no_optimize (migrations.test_commands.SquashMigrationsTests)", "test_failing_migration (migrations.test_commands.MakeMigrationsTests)", "test_files_content (migrations.test_commands.MakeMigrationsTests)", "test_makemigration_merge_dry_run (migrations.test_commands.MakeMigrationsTests)", "test_makemigration_merge_dry_run_verbosity_3 (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_auto_now_add_interactive (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_check (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_conflict_exit (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_consistency_checks_respect_routers (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_default_merge_name (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_disabled_migrations_for_app (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_dry_run (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_dry_run_verbosity_3 (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_empty_connections (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_empty_migration (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_empty_no_app_specified (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_handle_merge (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_inconsistent_history (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_interactive_accept (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_interactive_by_default (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_interactive_reject (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_merge_dont_output_dependency_operations (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_merge_no_conflict (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_migration_path_output (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_migration_path_output_valueerror (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_migrations_announce (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_migrations_modules_nonexistent_toplevel_package (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_migrations_modules_path_not_exist (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_no_apps_initial (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_no_changes (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_no_changes_no_apps (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_no_common_ancestor (migrations.test_commands.MakeMigrationsTests)", "Migration directories without an __init__.py file are allowed.", "test_makemigrations_non_interactive_no_field_rename (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_non_interactive_no_model_rename (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_non_interactive_not_null_addition (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_non_interactive_not_null_alteration (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_order (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_unspecified_app_with_conflict_merge (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_unspecified_app_with_conflict_no_merge (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_with_custom_name (migrations.test_commands.MakeMigrationsTests)", "test_makemigrations_with_invalid_custom_name (migrations.test_commands.MakeMigrationsTests)", "test_ambigious_prefix (migrations.test_commands.MigrateTests)", "test_app_without_migrations (migrations.test_commands.MigrateTests)", "test_migrate (migrations.test_commands.MigrateTests)", "test_migrate_conflict_exit (migrations.test_commands.MigrateTests)", "test_migrate_fake_initial (migrations.test_commands.MigrateTests)", "test_migrate_fake_split_initial (migrations.test_commands.MigrateTests)", "test_migrate_inconsistent_history (migrations.test_commands.MigrateTests)", "test_migrate_initial_false (migrations.test_commands.MigrateTests)", "Tests migrate --plan output.", "test_migrate_record_replaced (migrations.test_commands.MigrateTests)", "test_migrate_record_squashed (migrations.test_commands.MigrateTests)", "test_migrate_syncdb_app_label (migrations.test_commands.MigrateTests)", "test_migrate_syncdb_app_with_migrations (migrations.test_commands.MigrateTests)", "test_migrate_syncdb_deferred_sql_executed_with_schemaeditor (migrations.test_commands.MigrateTests)", "test_migrate_with_system_checks (migrations.test_commands.MigrateTests)", "test_regression_22823_unmigrated_fk_to_migrated_model (migrations.test_commands.MigrateTests)", "test_showmigrations_list (migrations.test_commands.MigrateTests)", "test_showmigrations_no_migrations (migrations.test_commands.MigrateTests)", "test_showmigrations_plan (migrations.test_commands.MigrateTests)", "test_showmigrations_plan_app_label_no_migrations (migrations.test_commands.MigrateTests)", "test_showmigrations_plan_multiple_app_labels (migrations.test_commands.MigrateTests)", "test_showmigrations_plan_no_migrations (migrations.test_commands.MigrateTests)", "test_showmigrations_plan_single_app_label (migrations.test_commands.MigrateTests)", "test_showmigrations_plan_squashed (migrations.test_commands.MigrateTests)", "test_showmigrations_unmigrated_app (migrations.test_commands.MigrateTests)", "test_sqlmigrate_backwards (migrations.test_commands.MigrateTests)", "test_sqlmigrate_for_non_atomic_migration (migrations.test_commands.MigrateTests)", "test_sqlmigrate_forwards (migrations.test_commands.MigrateTests)", "test_unknown_prefix (migrations.test_commands.MigrateTests)"]

**Base Commit**: d5276398046ce4a102776a1e67dcac2884d80dfe
**Environment Setup Commit**: 419a78300f7cd27611196e1e464d50fd0385ff27
