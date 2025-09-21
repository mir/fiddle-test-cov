# django__django-12708

**Repository**: django/django
**Created**: 2020-04-12T22:20:59Z
**Version**: 3.1

## Problem Statement

Migration crashes deleting an index_together if there is a unique_together on the same fields
Description
	
Happens with Django 1.11.10
Steps to reproduce:
1) Create models with 2 fields, add 2 same fields to unique_together and to index_together
2) Delete index_together -> Fail
It will fail at django/db/backends/base/schema.py, line 378, in _delete_composed_index(), ValueError: Found wrong number (2) of constraints for as this one will find two constraints, the _uniq and the _idx one. No way to get out of this...
The worst in my case is that happened as I wanted to refactor my code to use the "new" (Dj 1.11) Options.indexes feature. I am actually not deleting the index, just the way it is declared in my code.
I think there are 2 different points here:
1) The deletion of index_together should be possible alone or made coherent (migrations side?) with unique_together
2) Moving the declaration of an index should not result in an index re-creation


## Hints

Reproduced on master at 623139b5d1bd006eac78b375bcaf5948e695c3c6.
I haven't looked under the hood on this yet, but could it be related to the ordering of the operations generated for the mgiration? on first inspection it feels like this and #28862 could be caused by the same/similar underlying problem in how FieldRelatedOptionOperation subclasses ordering is handled in the migration autodetector's migration optimizer.

## Patch

```diff

diff --git a/django/db/backends/base/schema.py b/django/db/backends/base/schema.py
--- a/django/db/backends/base/schema.py
+++ b/django/db/backends/base/schema.py
@@ -393,7 +393,12 @@ def alter_index_together(self, model, old_index_together, new_index_together):
         news = {tuple(fields) for fields in new_index_together}
         # Deleted indexes
         for fields in olds.difference(news):
-            self._delete_composed_index(model, fields, {'index': True}, self.sql_delete_index)
+            self._delete_composed_index(
+                model,
+                fields,
+                {'index': True, 'unique': False},
+                self.sql_delete_index,
+            )
         # Created indexes
         for field_names in news.difference(olds):
             fields = [model._meta.get_field(field) for field in field_names]


```

## Test Patch

```diff
diff --git a/tests/migrations/test_base.py b/tests/migrations/test_base.py
--- a/tests/migrations/test_base.py
+++ b/tests/migrations/test_base.py
@@ -62,7 +62,11 @@ def assertIndexExists(self, table, columns, value=True, using='default', index_t
                 any(
                     c["index"]
                     for c in connections[using].introspection.get_constraints(cursor, table).values()
-                    if c['columns'] == list(columns) and (index_type is None or c['type'] == index_type)
+                    if (
+                        c['columns'] == list(columns) and
+                        (index_type is None or c['type'] == index_type) and
+                        not c['unique']
+                    )
                 ),
             )
 
@@ -80,6 +84,14 @@ def assertConstraintExists(self, table, name, value=True, using='default'):
     def assertConstraintNotExists(self, table, name):
         return self.assertConstraintExists(table, name, False)
 
+    def assertUniqueConstraintExists(self, table, columns, value=True, using='default'):
+        with connections[using].cursor() as cursor:
+            constraints = connections[using].introspection.get_constraints(cursor, table).values()
+            self.assertEqual(
+                value,
+                any(c['unique'] for c in constraints if c['columns'] == list(columns)),
+            )
+
     def assertFKExists(self, table, columns, to, value=True, using='default'):
         with connections[using].cursor() as cursor:
             self.assertEqual(
diff --git a/tests/migrations/test_operations.py b/tests/migrations/test_operations.py
--- a/tests/migrations/test_operations.py
+++ b/tests/migrations/test_operations.py
@@ -1759,6 +1759,29 @@ def test_alter_index_together_remove(self):
         operation = migrations.AlterIndexTogether("Pony", None)
         self.assertEqual(operation.describe(), "Alter index_together for Pony (0 constraint(s))")
 
+    @skipUnlessDBFeature('allows_multiple_constraints_on_same_fields')
+    def test_alter_index_together_remove_with_unique_together(self):
+        app_label = 'test_alintoremove_wunto'
+        table_name = '%s_pony' % app_label
+        project_state = self.set_up_test_model(app_label, unique_together=True)
+        self.assertUniqueConstraintExists(table_name, ['pink', 'weight'])
+        # Add index together.
+        new_state = project_state.clone()
+        operation = migrations.AlterIndexTogether('Pony', [('pink', 'weight')])
+        operation.state_forwards(app_label, new_state)
+        with connection.schema_editor() as editor:
+            operation.database_forwards(app_label, editor, project_state, new_state)
+        self.assertIndexExists(table_name, ['pink', 'weight'])
+        # Remove index together.
+        project_state = new_state
+        new_state = project_state.clone()
+        operation = migrations.AlterIndexTogether('Pony', set())
+        operation.state_forwards(app_label, new_state)
+        with connection.schema_editor() as editor:
+            operation.database_forwards(app_label, editor, project_state, new_state)
+        self.assertIndexNotExists(table_name, ['pink', 'weight'])
+        self.assertUniqueConstraintExists(table_name, ['pink', 'weight'])
+
     @skipUnlessDBFeature('supports_table_check_constraints')
     def test_add_constraint(self):
         project_state = self.set_up_test_model("test_addconstraint")

```

## Test Information

**Tests that should FAIL→PASS**: ["test_alter_index_together_remove_with_unique_together (migrations.test_operations.OperationTests)"]

**Tests that should PASS→PASS**: ["test_references_model_mixin (migrations.test_operations.TestCreateModel)", "test_reference_field_by_through_fields (migrations.test_operations.FieldOperationTests)", "test_references_field_by_from_fields (migrations.test_operations.FieldOperationTests)", "test_references_field_by_name (migrations.test_operations.FieldOperationTests)", "test_references_field_by_remote_field_model (migrations.test_operations.FieldOperationTests)", "test_references_field_by_through (migrations.test_operations.FieldOperationTests)", "test_references_field_by_to_fields (migrations.test_operations.FieldOperationTests)", "test_references_model (migrations.test_operations.FieldOperationTests)", "test_add_field_ignore_swapped (migrations.test_operations.SwappableOperationTests)", "test_create_ignore_swapped (migrations.test_operations.SwappableOperationTests)", "test_delete_ignore_swapped (migrations.test_operations.SwappableOperationTests)", "test_indexes_ignore_swapped (migrations.test_operations.SwappableOperationTests)", "test_add_binaryfield (migrations.test_operations.OperationTests)", "test_add_charfield (migrations.test_operations.OperationTests)", "test_add_constraint (migrations.test_operations.OperationTests)", "test_add_constraint_combinable (migrations.test_operations.OperationTests)", "test_add_constraint_percent_escaping (migrations.test_operations.OperationTests)", "test_add_field (migrations.test_operations.OperationTests)", "test_add_field_m2m (migrations.test_operations.OperationTests)", "test_add_field_preserve_default (migrations.test_operations.OperationTests)", "test_add_index (migrations.test_operations.OperationTests)", "test_add_index_state_forwards (migrations.test_operations.OperationTests)", "test_add_or_constraint (migrations.test_operations.OperationTests)", "test_add_partial_unique_constraint (migrations.test_operations.OperationTests)", "test_add_textfield (migrations.test_operations.OperationTests)", "test_alter_field (migrations.test_operations.OperationTests)", "test_alter_field_m2m (migrations.test_operations.OperationTests)", "test_alter_field_pk (migrations.test_operations.OperationTests)", "test_alter_field_pk_fk (migrations.test_operations.OperationTests)", "test_alter_field_reloads_state_on_fk_target_changes (migrations.test_operations.OperationTests)", "test_alter_field_reloads_state_on_fk_with_to_field_related_name_target_type_change (migrations.test_operations.OperationTests)", "test_alter_field_reloads_state_on_fk_with_to_field_target_changes (migrations.test_operations.OperationTests)", "test_alter_field_reloads_state_on_fk_with_to_field_target_type_change (migrations.test_operations.OperationTests)", "test_alter_field_with_index (migrations.test_operations.OperationTests)", "test_alter_fk (migrations.test_operations.OperationTests)", "test_alter_fk_non_fk (migrations.test_operations.OperationTests)", "test_alter_index_together (migrations.test_operations.OperationTests)", "test_alter_index_together_remove (migrations.test_operations.OperationTests)", "test_alter_model_managers (migrations.test_operations.OperationTests)", "test_alter_model_managers_emptying (migrations.test_operations.OperationTests)", "test_alter_model_options (migrations.test_operations.OperationTests)", "test_alter_model_options_emptying (migrations.test_operations.OperationTests)", "test_alter_model_table (migrations.test_operations.OperationTests)", "test_alter_model_table_m2m (migrations.test_operations.OperationTests)", "test_alter_model_table_none (migrations.test_operations.OperationTests)", "test_alter_model_table_noop (migrations.test_operations.OperationTests)", "test_alter_order_with_respect_to (migrations.test_operations.OperationTests)", "test_alter_unique_together (migrations.test_operations.OperationTests)", "test_alter_unique_together_remove (migrations.test_operations.OperationTests)", "A field may be migrated from AutoField to BigAutoField.", "test_column_name_quoting (migrations.test_operations.OperationTests)", "test_create_model (migrations.test_operations.OperationTests)", "test_create_model_inheritance (migrations.test_operations.OperationTests)", "test_create_model_m2m (migrations.test_operations.OperationTests)", "test_create_model_managers (migrations.test_operations.OperationTests)", "test_create_model_with_constraint (migrations.test_operations.OperationTests)", "test_create_model_with_duplicate_base (migrations.test_operations.OperationTests)", "test_create_model_with_duplicate_field_name (migrations.test_operations.OperationTests)", "test_create_model_with_duplicate_manager_name (migrations.test_operations.OperationTests)", "test_create_model_with_partial_unique_constraint (migrations.test_operations.OperationTests)", "test_create_model_with_unique_after (migrations.test_operations.OperationTests)", "test_create_proxy_model (migrations.test_operations.OperationTests)", "test_create_unmanaged_model (migrations.test_operations.OperationTests)", "test_delete_model (migrations.test_operations.OperationTests)", "test_delete_mti_model (migrations.test_operations.OperationTests)", "test_delete_proxy_model (migrations.test_operations.OperationTests)", "test_model_with_bigautofield (migrations.test_operations.OperationTests)", "test_remove_constraint (migrations.test_operations.OperationTests)", "test_remove_field (migrations.test_operations.OperationTests)", "test_remove_field_m2m (migrations.test_operations.OperationTests)", "test_remove_field_m2m_with_through (migrations.test_operations.OperationTests)", "test_remove_fk (migrations.test_operations.OperationTests)", "test_remove_index (migrations.test_operations.OperationTests)", "test_remove_index_state_forwards (migrations.test_operations.OperationTests)", "test_remove_partial_unique_constraint (migrations.test_operations.OperationTests)", "test_rename_field (migrations.test_operations.OperationTests)", "test_rename_field_reloads_state_on_fk_target_changes (migrations.test_operations.OperationTests)", "RenameModel renames a many-to-many column after a RenameField.", "test_rename_m2m_target_model (migrations.test_operations.OperationTests)", "test_rename_m2m_through_model (migrations.test_operations.OperationTests)", "test_rename_missing_field (migrations.test_operations.OperationTests)", "test_rename_model (migrations.test_operations.OperationTests)", "test_rename_model_state_forwards (migrations.test_operations.OperationTests)", "test_rename_model_with_m2m (migrations.test_operations.OperationTests)", "test_rename_model_with_self_referential_fk (migrations.test_operations.OperationTests)", "test_rename_model_with_self_referential_m2m (migrations.test_operations.OperationTests)", "test_rename_model_with_superclass_fk (migrations.test_operations.OperationTests)", "test_rename_referenced_field_state_forward (migrations.test_operations.OperationTests)", "test_repoint_field_m2m (migrations.test_operations.OperationTests)", "test_run_python (migrations.test_operations.OperationTests)", "test_run_python_atomic (migrations.test_operations.OperationTests)", "test_run_python_noop (migrations.test_operations.OperationTests)", "test_run_python_related_assignment (migrations.test_operations.OperationTests)", "test_run_sql (migrations.test_operations.OperationTests)", "test_run_sql_noop (migrations.test_operations.OperationTests)", "test_run_sql_params (migrations.test_operations.OperationTests)", "test_run_sql_params_invalid (migrations.test_operations.OperationTests)", "test_separate_database_and_state (migrations.test_operations.OperationTests)", "test_separate_database_and_state2 (migrations.test_operations.OperationTests)", "A field may be migrated from SmallAutoField to AutoField.", "A field may be migrated from SmallAutoField to BigAutoField."]

**Base Commit**: 447980e72ac01da1594dd3373a03ba40b7ee6f80
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
