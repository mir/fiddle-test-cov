# django__django-14997

**Repository**: django/django
**Created**: 2021-10-15T20:19:33Z
**Version**: 4.1

## Problem Statement

Remaking table with unique constraint crashes on SQLite.
Description
	
In Django 4.0a1, this model:
class Tag(models.Model):
	name = models.SlugField(help_text="The tag key.")
	value = models.CharField(max_length=150, help_text="The tag value.")
	class Meta:
		ordering = ["name", "value"]
		constraints = [
			models.UniqueConstraint(
				"name",
				"value",
				name="unique_name_value",
			)
		]
	def __str__(self):
		return f"{self.name}={self.value}"
with these migrations, using sqlite:
class Migration(migrations.Migration):
	initial = True
	dependencies = [
	]
	operations = [
		migrations.CreateModel(
			name='Tag',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('name', models.SlugField(help_text='The tag key.')),
				('value', models.CharField(help_text='The tag value.', max_length=200)),
			],
			options={
				'ordering': ['name', 'value'],
			},
		),
		migrations.AddConstraint(
			model_name='tag',
			constraint=models.UniqueConstraint(django.db.models.expressions.F('name'), django.db.models.expressions.F('value'), name='unique_name_value'),
		),
	]
class Migration(migrations.Migration):
	dependencies = [
		('myapp', '0001_initial'),
	]
	operations = [
		migrations.AlterField(
			model_name='tag',
			name='value',
			field=models.CharField(help_text='The tag value.', max_length=150),
		),
	]
raises this error:
manage.py migrate
Operations to perform:
 Apply all migrations: admin, auth, contenttypes, myapp, sessions
Running migrations:
 Applying myapp.0002_alter_tag_value...python-BaseException
Traceback (most recent call last):
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\backends\utils.py", line 84, in _execute
	return self.cursor.execute(sql, params)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\backends\sqlite3\base.py", line 416, in execute
	return Database.Cursor.execute(self, query, params)
sqlite3.OperationalError: the "." operator prohibited in index expressions
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\core\management\base.py", line 373, in run_from_argv
	self.execute(*args, **cmd_options)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\core\management\base.py", line 417, in execute
	output = self.handle(*args, **options)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\core\management\base.py", line 90, in wrapped
	res = handle_func(*args, **kwargs)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\core\management\commands\migrate.py", line 253, in handle
	post_migrate_state = executor.migrate(
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\migrations\executor.py", line 126, in migrate
	state = self._migrate_all_forwards(state, plan, full_plan, fake=fake, fake_initial=fake_initial)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\migrations\executor.py", line 156, in _migrate_all_forwards
	state = self.apply_migration(state, migration, fake=fake, fake_initial=fake_initial)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\migrations\executor.py", line 236, in apply_migration
	state = migration.apply(state, schema_editor)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\migrations\migration.py", line 125, in apply
	operation.database_forwards(self.app_label, schema_editor, old_state, project_state)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\migrations\operations\fields.py", line 225, in database_forwards
	schema_editor.alter_field(from_model, from_field, to_field)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\backends\sqlite3\schema.py", line 140, in alter_field
	super().alter_field(model, old_field, new_field, strict=strict)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\backends\base\schema.py", line 618, in alter_field
	self._alter_field(model, old_field, new_field, old_type, new_type,
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\backends\sqlite3\schema.py", line 362, in _alter_field
	self._remake_table(model, alter_field=(old_field, new_field))
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\backends\sqlite3\schema.py", line 303, in _remake_table
	self.execute(sql)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\backends\base\schema.py", line 151, in execute
	cursor.execute(sql, params)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\backends\utils.py", line 98, in execute
	return super().execute(sql, params)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\backends\utils.py", line 66, in execute
	return self._execute_with_wrappers(sql, params, many=False, executor=self._execute)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\backends\utils.py", line 75, in _execute_with_wrappers
	return executor(sql, params, many, context)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\backends\utils.py", line 84, in _execute
	return self.cursor.execute(sql, params)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\utils.py", line 90, in __exit__
	raise dj_exc_value.with_traceback(traceback) from exc_value
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\backends\utils.py", line 84, in _execute
	return self.cursor.execute(sql, params)
 File "D:\Projects\Development\sqliteerror\.venv\lib\site-packages\django\db\backends\sqlite3\base.py", line 416, in execute
	return Database.Cursor.execute(self, query, params)
django.db.utils.OperationalError: the "." operator prohibited in index expressions


## Hints

Thanks for the report. Regression in 3aa545281e0c0f9fac93753e3769df9e0334dbaa.
Thanks for the report! Looks like we don't check if an alias is set on the Col before we update it to new_table in Expressions.rename_table_references when running _remake_table.

## Patch

```diff

diff --git a/django/db/backends/ddl_references.py b/django/db/backends/ddl_references.py
--- a/django/db/backends/ddl_references.py
+++ b/django/db/backends/ddl_references.py
@@ -212,11 +212,7 @@ def __init__(self, table, expressions, compiler, quote_value):
     def rename_table_references(self, old_table, new_table):
         if self.table != old_table:
             return
-        expressions = deepcopy(self.expressions)
-        self.columns = []
-        for col in self.compiler.query._gen_cols([expressions]):
-            col.alias = new_table
-        self.expressions = expressions
+        self.expressions = self.expressions.relabeled_clone({old_table: new_table})
         super().rename_table_references(old_table, new_table)
 
     def rename_column_references(self, table, old_column, new_column):


```

## Test Patch

```diff
diff --git a/tests/backends/test_ddl_references.py b/tests/backends/test_ddl_references.py
--- a/tests/backends/test_ddl_references.py
+++ b/tests/backends/test_ddl_references.py
@@ -5,6 +5,7 @@
 from django.db.models import ExpressionList, F
 from django.db.models.functions import Upper
 from django.db.models.indexes import IndexExpression
+from django.db.models.sql import Query
 from django.test import SimpleTestCase, TransactionTestCase
 
 from .models import Person
@@ -229,6 +230,27 @@ def test_rename_table_references(self):
             str(self.expressions),
         )
 
+    def test_rename_table_references_without_alias(self):
+        compiler = Query(Person, alias_cols=False).get_compiler(connection=connection)
+        table = Person._meta.db_table
+        expressions = Expressions(
+            table=table,
+            expressions=ExpressionList(
+                IndexExpression(Upper('last_name')),
+                IndexExpression(F('first_name')),
+            ).resolve_expression(compiler.query),
+            compiler=compiler,
+            quote_value=self.editor.quote_value,
+        )
+        expressions.rename_table_references(table, 'other')
+        self.assertIs(expressions.references_table(table), False)
+        self.assertIs(expressions.references_table('other'), True)
+        expected_str = '(UPPER(%s)), %s' % (
+            self.editor.quote_name('last_name'),
+            self.editor.quote_name('first_name'),
+        )
+        self.assertEqual(str(expressions), expected_str)
+
     def test_rename_column_references(self):
         table = Person._meta.db_table
         self.expressions.rename_column_references(table, 'first_name', 'other')
diff --git a/tests/migrations/test_operations.py b/tests/migrations/test_operations.py
--- a/tests/migrations/test_operations.py
+++ b/tests/migrations/test_operations.py
@@ -2106,6 +2106,25 @@ def test_remove_func_index(self):
         self.assertEqual(definition[1], [])
         self.assertEqual(definition[2], {'model_name': 'Pony', 'name': index_name})
 
+    @skipUnlessDBFeature('supports_expression_indexes')
+    def test_alter_field_with_func_index(self):
+        app_label = 'test_alfuncin'
+        index_name = f'{app_label}_pony_idx'
+        table_name = f'{app_label}_pony'
+        project_state = self.set_up_test_model(
+            app_label,
+            indexes=[models.Index(Abs('pink'), name=index_name)],
+        )
+        operation = migrations.AlterField('Pony', 'pink', models.IntegerField(null=True))
+        new_state = project_state.clone()
+        operation.state_forwards(app_label, new_state)
+        with connection.schema_editor() as editor:
+            operation.database_forwards(app_label, editor, project_state, new_state)
+        self.assertIndexNameExists(table_name, index_name)
+        with connection.schema_editor() as editor:
+            operation.database_backwards(app_label, editor, new_state, project_state)
+        self.assertIndexNameExists(table_name, index_name)
+
     def test_alter_field_with_index(self):
         """
         Test AlterField operation with an index to ensure indexes created via
@@ -2664,6 +2683,26 @@ def test_remove_covering_unique_constraint(self):
             'name': 'covering_pink_constraint_rm',
         })
 
+    def test_alter_field_with_func_unique_constraint(self):
+        app_label = 'test_alfuncuc'
+        constraint_name = f'{app_label}_pony_uq'
+        table_name = f'{app_label}_pony'
+        project_state = self.set_up_test_model(
+            app_label,
+            constraints=[models.UniqueConstraint('pink', 'weight', name=constraint_name)]
+        )
+        operation = migrations.AlterField('Pony', 'pink', models.IntegerField(null=True))
+        new_state = project_state.clone()
+        operation.state_forwards(app_label, new_state)
+        with connection.schema_editor() as editor:
+            operation.database_forwards(app_label, editor, project_state, new_state)
+        if connection.features.supports_expression_indexes:
+            self.assertIndexNameExists(table_name, constraint_name)
+        with connection.schema_editor() as editor:
+            operation.database_backwards(app_label, editor, new_state, project_state)
+        if connection.features.supports_expression_indexes:
+            self.assertIndexNameExists(table_name, constraint_name)
+
     def test_add_func_unique_constraint(self):
         app_label = 'test_adfuncuc'
         constraint_name = f'{app_label}_pony_abs_uq'

```

## Test Information

**Tests that should FAIL→PASS**: ["test_rename_table_references_without_alias (backends.test_ddl_references.ExpressionsTests)", "test_alter_field_with_func_index (migrations.test_operations.OperationTests)", "test_alter_field_with_func_unique_constraint (migrations.test_operations.OperationTests)"]

**Tests that should PASS→PASS**: ["test_references_column (backends.test_ddl_references.ColumnsTests)", "test_references_table (backends.test_ddl_references.ColumnsTests)", "test_rename_column_references (backends.test_ddl_references.ColumnsTests)", "test_rename_table_references (backends.test_ddl_references.ColumnsTests)", "test_repr (backends.test_ddl_references.ColumnsTests)", "test_str (backends.test_ddl_references.ColumnsTests)", "test_references_model_mixin (migrations.test_operations.TestCreateModel)", "test_references_column (backends.test_ddl_references.ForeignKeyNameTests)", "test_references_table (backends.test_ddl_references.ForeignKeyNameTests)", "test_rename_column_references (backends.test_ddl_references.ForeignKeyNameTests)", "test_rename_table_references (backends.test_ddl_references.ForeignKeyNameTests)", "test_repr (backends.test_ddl_references.ForeignKeyNameTests)", "test_str (backends.test_ddl_references.ForeignKeyNameTests)", "test_references_table (backends.test_ddl_references.TableTests)", "test_rename_table_references (backends.test_ddl_references.TableTests)", "test_repr (backends.test_ddl_references.TableTests)", "test_str (backends.test_ddl_references.TableTests)", "test_references_column (backends.test_ddl_references.IndexNameTests)", "test_references_table (backends.test_ddl_references.IndexNameTests)", "test_rename_column_references (backends.test_ddl_references.IndexNameTests)", "test_rename_table_references (backends.test_ddl_references.IndexNameTests)", "test_repr (backends.test_ddl_references.IndexNameTests)", "test_str (backends.test_ddl_references.IndexNameTests)", "test_references_column (backends.test_ddl_references.StatementTests)", "test_references_table (backends.test_ddl_references.StatementTests)", "test_rename_column_references (backends.test_ddl_references.StatementTests)", "test_rename_table_references (backends.test_ddl_references.StatementTests)", "test_repr (backends.test_ddl_references.StatementTests)", "test_str (backends.test_ddl_references.StatementTests)", "test_reference_field_by_through_fields (migrations.test_operations.FieldOperationTests)", "test_references_field_by_from_fields (migrations.test_operations.FieldOperationTests)", "test_references_field_by_name (migrations.test_operations.FieldOperationTests)", "test_references_field_by_remote_field_model (migrations.test_operations.FieldOperationTests)", "test_references_field_by_through (migrations.test_operations.FieldOperationTests)", "test_references_field_by_to_fields (migrations.test_operations.FieldOperationTests)", "test_references_model (migrations.test_operations.FieldOperationTests)", "test_references_column (backends.test_ddl_references.ExpressionsTests)", "test_references_table (backends.test_ddl_references.ExpressionsTests)", "test_rename_column_references (backends.test_ddl_references.ExpressionsTests)", "test_rename_table_references (backends.test_ddl_references.ExpressionsTests)", "test_str (backends.test_ddl_references.ExpressionsTests)", "Tests the AddField operation.", "The CreateTable operation ignores swapped models.", "Tests the DeleteModel operation ignores swapped models.", "Add/RemoveIndex operations ignore swapped models.", "Tests the AddField operation on TextField/BinaryField.", "Tests the AddField operation on TextField.", "test_add_constraint (migrations.test_operations.OperationTests)", "test_add_constraint_combinable (migrations.test_operations.OperationTests)", "test_add_constraint_percent_escaping (migrations.test_operations.OperationTests)", "test_add_covering_unique_constraint (migrations.test_operations.OperationTests)", "test_add_deferred_unique_constraint (migrations.test_operations.OperationTests)", "Tests the AddField operation with a ManyToManyField.", "Tests the AddField operation's state alteration", "test_add_func_index (migrations.test_operations.OperationTests)", "test_add_func_unique_constraint (migrations.test_operations.OperationTests)", "Test the AddIndex operation.", "test_add_index_state_forwards (migrations.test_operations.OperationTests)", "test_add_or_constraint (migrations.test_operations.OperationTests)", "test_add_partial_unique_constraint (migrations.test_operations.OperationTests)", "Tests the AlterField operation.", "AlterField operation is a noop when adding only a db_column and the", "test_alter_field_m2m (migrations.test_operations.OperationTests)", "Tests the AlterField operation on primary keys (for things like PostgreSQL's SERIAL weirdness)", "Tests the AlterField operation on primary keys changes any FKs pointing to it.", "test_alter_field_pk_mti_fk (migrations.test_operations.OperationTests)", "If AlterField doesn't reload state appropriately, the second AlterField", "test_alter_field_reloads_state_on_fk_with_to_field_related_name_target_type_change (migrations.test_operations.OperationTests)", "test_alter_field_reloads_state_on_fk_with_to_field_target_type_change (migrations.test_operations.OperationTests)", "Test AlterField operation with an index to ensure indexes created via", "Creating and then altering an FK works correctly", "Altering an FK to a non-FK works (#23244)", "Tests the AlterIndexTogether operation.", "test_alter_index_together_remove (migrations.test_operations.OperationTests)", "test_alter_index_together_remove_with_unique_together (migrations.test_operations.OperationTests)", "The managers on a model are set.", "Tests the AlterModelOptions operation.", "The AlterModelOptions operation removes keys from the dict (#23121)", "Tests the AlterModelTable operation.", "AlterModelTable should rename auto-generated M2M tables.", "Tests the AlterModelTable operation if the table name is set to None.", "Tests the AlterModelTable operation if the table name is not changed.", "Tests the AlterOrderWithRespectTo operation.", "Tests the AlterUniqueTogether operation.", "test_alter_unique_together_remove (migrations.test_operations.OperationTests)", "A field may be migrated from AutoField to BigAutoField.", "Column names that are SQL keywords shouldn't cause problems when used", "Tests the CreateModel operation.", "Tests the CreateModel operation on a multi-table inheritance setup.", "Test the creation of a model with a ManyToMany field and the", "test_create_model_with_constraint (migrations.test_operations.OperationTests)", "test_create_model_with_deferred_unique_constraint (migrations.test_operations.OperationTests)", "test_create_model_with_duplicate_base (migrations.test_operations.OperationTests)", "test_create_model_with_duplicate_field_name (migrations.test_operations.OperationTests)", "test_create_model_with_duplicate_manager_name (migrations.test_operations.OperationTests)", "test_create_model_with_partial_unique_constraint (migrations.test_operations.OperationTests)", "Tests the CreateModel operation directly followed by an", "CreateModel ignores proxy models.", "CreateModel ignores unmanaged models.", "Tests the DeleteModel operation.", "test_delete_mti_model (migrations.test_operations.OperationTests)", "Tests the DeleteModel operation ignores proxy models.", "A model with BigAutoField can be created.", "test_remove_constraint (migrations.test_operations.OperationTests)", "test_remove_covering_unique_constraint (migrations.test_operations.OperationTests)", "test_remove_deferred_unique_constraint (migrations.test_operations.OperationTests)", "Tests the RemoveField operation.", "test_remove_field_m2m (migrations.test_operations.OperationTests)", "test_remove_field_m2m_with_through (migrations.test_operations.OperationTests)", "Tests the RemoveField operation on a foreign key.", "test_remove_func_index (migrations.test_operations.OperationTests)", "test_remove_func_unique_constraint (migrations.test_operations.OperationTests)", "Test the RemoveIndex operation.", "test_remove_index_state_forwards (migrations.test_operations.OperationTests)", "test_remove_partial_unique_constraint (migrations.test_operations.OperationTests)", "Tests the RenameField operation.", "test_rename_field_case (migrations.test_operations.OperationTests)", "If RenameField doesn't reload state appropriately, the AlterField", "test_rename_field_with_db_column (migrations.test_operations.OperationTests)", "RenameModel renames a many-to-many column after a RenameField.", "test_rename_m2m_target_model (migrations.test_operations.OperationTests)", "test_rename_m2m_through_model (migrations.test_operations.OperationTests)", "test_rename_missing_field (migrations.test_operations.OperationTests)", "Tests the RenameModel operation.", "RenameModel operations shouldn't trigger the caching of rendered apps", "test_rename_model_with_m2m (migrations.test_operations.OperationTests)", "Tests the RenameModel operation on model with self referential FK.", "test_rename_model_with_self_referential_m2m (migrations.test_operations.OperationTests)", "Tests the RenameModel operation on a model which has a superclass that", "test_rename_referenced_field_state_forward (migrations.test_operations.OperationTests)", "test_repoint_field_m2m (migrations.test_operations.OperationTests)", "Tests the RunPython operation", "Tests the RunPython operation correctly handles the \"atomic\" keyword", "#24098 - Tests no-op RunPython operations.", "#24282 - Model changes to a FK reverse side update the model", "Tests the RunSQL operation.", "test_run_sql_add_missing_semicolon_on_collect_sql (migrations.test_operations.OperationTests)", "#24098 - Tests no-op RunSQL operations.", "#23426 - RunSQL should accept parameters.", "#23426 - RunSQL should fail when a list of statements with an incorrect", "Tests the SeparateDatabaseAndState operation.", "A complex SeparateDatabaseAndState operation: Multiple operations both", "A field may be migrated from SmallAutoField to AutoField.", "A field may be migrated from SmallAutoField to BigAutoField."]

**Base Commit**: 0d4e575c96d408e0efb4dfd0cbfc864219776950
**Environment Setup Commit**: 647480166bfe7532e8c471fef0146e3a17e6c0c9
