# django__django-11910

**Repository**: django/django
**Created**: 2019-10-14T01:56:49Z
**Version**: 3.1

## Problem Statement

ForeignKey's to_field parameter gets the old field's name when renaming a PrimaryKey.
Description
	
Having these two models 
class ModelA(models.Model):
	field_wrong = models.CharField('field1', max_length=50, primary_key=True) # I'm a Primary key.
class ModelB(models.Model):
	field_fk = models.ForeignKey(ModelA, blank=True, null=True, on_delete=models.CASCADE) 
... migrations applyed ...
the ModelA.field_wrong field has been renamed ... and Django recognizes the "renaming"
# Primary key renamed
class ModelA(models.Model):
	field_fixed = models.CharField('field1', max_length=50, primary_key=True) # I'm a Primary key.
Attempts to to_field parameter. 
The to_field points to the old_name (field_typo) and not to the new one ("field_fixed")
class Migration(migrations.Migration):
	dependencies = [
		('app1', '0001_initial'),
	]
	operations = [
		migrations.RenameField(
			model_name='modela',
			old_name='field_wrong',
			new_name='field_fixed',
		),
		migrations.AlterField(
			model_name='modelb',
			name='modela',
			field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app1.ModelB', to_field='field_wrong'),
		),
	]


## Hints

Thanks for this ticket. It looks like a regression in dcdd219ee1e062dc6189f382e0298e0adf5d5ddf, because an AlterField operation wasn't generated in such cases before this change (and I don't think we need it).

## Patch

```diff

diff --git a/django/db/migrations/autodetector.py b/django/db/migrations/autodetector.py
--- a/django/db/migrations/autodetector.py
+++ b/django/db/migrations/autodetector.py
@@ -927,6 +927,10 @@ def generate_altered_fields(self):
                 if remote_field_name:
                     to_field_rename_key = rename_key + (remote_field_name,)
                     if to_field_rename_key in self.renamed_fields:
+                        # Repoint both model and field name because to_field
+                        # inclusion in ForeignKey.deconstruct() is based on
+                        # both.
+                        new_field.remote_field.model = old_field.remote_field.model
                         new_field.remote_field.field_name = old_field.remote_field.field_name
                 # Handle ForeignObjects which can have multiple from_fields/to_fields.
                 from_fields = getattr(new_field, 'from_fields', None)


```

## Test Patch

```diff
diff --git a/tests/migrations/test_autodetector.py b/tests/migrations/test_autodetector.py
--- a/tests/migrations/test_autodetector.py
+++ b/tests/migrations/test_autodetector.py
@@ -932,6 +932,30 @@ def test_rename_foreign_object_fields(self):
             changes, 'app', 0, 1, model_name='bar', old_name='second', new_name='second_renamed',
         )
 
+    def test_rename_referenced_primary_key(self):
+        before = [
+            ModelState('app', 'Foo', [
+                ('id', models.CharField(primary_key=True, serialize=False)),
+            ]),
+            ModelState('app', 'Bar', [
+                ('id', models.AutoField(primary_key=True)),
+                ('foo', models.ForeignKey('app.Foo', models.CASCADE)),
+            ]),
+        ]
+        after = [
+            ModelState('app', 'Foo', [
+                ('renamed_id', models.CharField(primary_key=True, serialize=False))
+            ]),
+            ModelState('app', 'Bar', [
+                ('id', models.AutoField(primary_key=True)),
+                ('foo', models.ForeignKey('app.Foo', models.CASCADE)),
+            ]),
+        ]
+        changes = self.get_changes(before, after, MigrationQuestioner({'ask_rename': True}))
+        self.assertNumberMigrations(changes, 'app', 1)
+        self.assertOperationTypes(changes, 'app', 0, ['RenameField'])
+        self.assertOperationAttributes(changes, 'app', 0, 0, old_name='id', new_name='renamed_id')
+
     def test_rename_field_preserved_db_column(self):
         """
         RenameField is used if a field is renamed and db_column equal to the

```

## Test Information

**Tests that should FAIL→PASS**: ["test_rename_referenced_primary_key (migrations.test_autodetector.AutodetectorTests)"]

**Tests that should PASS→PASS**: ["test_add_alter_order_with_respect_to (migrations.test_autodetector.AutodetectorTests)", "test_add_blank_textfield_and_charfield (migrations.test_autodetector.AutodetectorTests)", "Test change detection of new constraints.", "test_add_date_fields_with_auto_now_add_asking_for_default (migrations.test_autodetector.AutodetectorTests)", "test_add_date_fields_with_auto_now_add_not_asking_for_null_addition (migrations.test_autodetector.AutodetectorTests)", "test_add_date_fields_with_auto_now_not_asking_for_default (migrations.test_autodetector.AutodetectorTests)", "Tests autodetection of new fields.", "test_add_field_and_foo_together (migrations.test_autodetector.AutodetectorTests)", "#22030 - Adding a field with a default should work.", "Tests index/unique_together detection.", "Test change detection of new indexes.", "#22435 - Adding a ManyToManyField should not prompt for a default.", "test_add_model_order_with_respect_to (migrations.test_autodetector.AutodetectorTests)", "test_add_non_blank_textfield_and_charfield (migrations.test_autodetector.AutodetectorTests)", "Tests detection for adding db_table in model's options.", "Tests detection for changing db_table in model's options'.", "test_alter_db_table_no_changes (migrations.test_autodetector.AutodetectorTests)", "Tests detection for removing db_table in model's options.", "test_alter_db_table_with_model_change (migrations.test_autodetector.AutodetectorTests)", "test_alter_field_to_fk_dependency_other_app (migrations.test_autodetector.AutodetectorTests)", "test_alter_field_to_not_null_oneoff_default (migrations.test_autodetector.AutodetectorTests)", "test_alter_field_to_not_null_with_default (migrations.test_autodetector.AutodetectorTests)", "test_alter_field_to_not_null_without_default (migrations.test_autodetector.AutodetectorTests)", "test_alter_fk_before_model_deletion (migrations.test_autodetector.AutodetectorTests)", "test_alter_many_to_many (migrations.test_autodetector.AutodetectorTests)", "test_alter_model_managers (migrations.test_autodetector.AutodetectorTests)", "Changing a model's options should make a change.", "Changing a proxy model's options should also make a change.", "Tests auto-naming of migrations for graph matching.", "Bases of other models come first.", "test_circular_dependency_mixed_addcreate (migrations.test_autodetector.AutodetectorTests)", "test_circular_dependency_swappable (migrations.test_autodetector.AutodetectorTests)", "test_circular_dependency_swappable2 (migrations.test_autodetector.AutodetectorTests)", "test_circular_dependency_swappable_self (migrations.test_autodetector.AutodetectorTests)", "test_circular_fk_dependency (migrations.test_autodetector.AutodetectorTests)", "test_concrete_field_changed_to_many_to_many (migrations.test_autodetector.AutodetectorTests)", "test_create_model_and_unique_together (migrations.test_autodetector.AutodetectorTests)", "Test creation of new model with constraints already defined.", "Test creation of new model with indexes already defined.", "test_create_with_through_model (migrations.test_autodetector.AutodetectorTests)", "test_custom_deconstructible (migrations.test_autodetector.AutodetectorTests)", "Tests custom naming of migrations for graph matching.", "Field instances are handled correctly by nested deconstruction.", "test_deconstruct_type (migrations.test_autodetector.AutodetectorTests)", "Nested deconstruction descends into dict values.", "Nested deconstruction descends into lists.", "Nested deconstruction descends into tuples.", "test_default_related_name_option (migrations.test_autodetector.AutodetectorTests)", "test_different_regex_does_alter (migrations.test_autodetector.AutodetectorTests)", "test_empty_foo_together (migrations.test_autodetector.AutodetectorTests)", "test_first_dependency (migrations.test_autodetector.AutodetectorTests)", "Having a ForeignKey automatically adds a dependency.", "test_fk_dependency_other_app (migrations.test_autodetector.AutodetectorTests)", "test_foo_together_no_changes (migrations.test_autodetector.AutodetectorTests)", "test_foo_together_ordering (migrations.test_autodetector.AutodetectorTests)", "Tests unique_together and field removal detection & ordering", "test_foreign_key_removed_before_target_model (migrations.test_autodetector.AutodetectorTests)", "test_identical_regex_doesnt_alter (migrations.test_autodetector.AutodetectorTests)", "test_keep_db_table_with_model_change (migrations.test_autodetector.AutodetectorTests)", "test_last_dependency (migrations.test_autodetector.AutodetectorTests)", "test_m2m_w_through_multistep_remove (migrations.test_autodetector.AutodetectorTests)", "test_managed_to_unmanaged (migrations.test_autodetector.AutodetectorTests)", "test_many_to_many_changed_to_concrete_field (migrations.test_autodetector.AutodetectorTests)", "test_many_to_many_removed_before_through_model (migrations.test_autodetector.AutodetectorTests)", "test_many_to_many_removed_before_through_model_2 (migrations.test_autodetector.AutodetectorTests)", "test_mti_inheritance_model_removal (migrations.test_autodetector.AutodetectorTests)", "#23956 - Inheriting models doesn't move *_ptr fields into AddField operations.", "test_nested_deconstructible_objects (migrations.test_autodetector.AutodetectorTests)", "Tests autodetection of new models.", "test_non_circular_foreignkey_dependency_removal (migrations.test_autodetector.AutodetectorTests)", "Tests deletion of old models.", "Test change detection of reordering of fields in indexes.", "test_pk_fk_included (migrations.test_autodetector.AutodetectorTests)", "The autodetector correctly deals with proxy models.", "Bases of proxies come first.", "test_proxy_custom_pk (migrations.test_autodetector.AutodetectorTests)", "FK dependencies still work on proxy models.", "test_proxy_to_mti_with_fk_to_proxy (migrations.test_autodetector.AutodetectorTests)", "test_proxy_to_mti_with_fk_to_proxy_proxy (migrations.test_autodetector.AutodetectorTests)", "test_remove_alter_order_with_respect_to (migrations.test_autodetector.AutodetectorTests)", "Test change detection of removed constraints.", "Tests autodetection of removed fields.", "test_remove_field_and_foo_together (migrations.test_autodetector.AutodetectorTests)", "Test change detection of removed indexes.", "Tests autodetection of renamed fields.", "test_rename_field_and_foo_together (migrations.test_autodetector.AutodetectorTests)", "test_rename_field_foreign_key_to_field (migrations.test_autodetector.AutodetectorTests)", "test_rename_field_preserved_db_column (migrations.test_autodetector.AutodetectorTests)", "test_rename_foreign_object_fields (migrations.test_autodetector.AutodetectorTests)", "test_rename_m2m_through_model (migrations.test_autodetector.AutodetectorTests)", "Tests autodetection of renamed models.", "test_rename_model_reverse_relation_dependencies (migrations.test_autodetector.AutodetectorTests)", "test_rename_model_with_fks_in_different_position (migrations.test_autodetector.AutodetectorTests)", "test_rename_model_with_renamed_rel_field (migrations.test_autodetector.AutodetectorTests)", "test_rename_related_field_preserved_db_column (migrations.test_autodetector.AutodetectorTests)", "test_replace_string_with_foreignkey (migrations.test_autodetector.AutodetectorTests)", "test_same_app_circular_fk_dependency (migrations.test_autodetector.AutodetectorTests)", "test_same_app_circular_fk_dependency_with_unique_together_and_indexes (migrations.test_autodetector.AutodetectorTests)", "test_same_app_no_fk_dependency (migrations.test_autodetector.AutodetectorTests)", "Setting order_with_respect_to adds a field.", "test_supports_functools_partial (migrations.test_autodetector.AutodetectorTests)", "test_swappable (migrations.test_autodetector.AutodetectorTests)", "test_swappable_changed (migrations.test_autodetector.AutodetectorTests)", "test_swappable_circular_multi_mti (migrations.test_autodetector.AutodetectorTests)", "Swappable models get their CreateModel first.", "test_trim_apps (migrations.test_autodetector.AutodetectorTests)", "The autodetector correctly deals with managed models.", "test_unmanaged_custom_pk (migrations.test_autodetector.AutodetectorTests)", "test_unmanaged_delete (migrations.test_autodetector.AutodetectorTests)", "test_unmanaged_to_managed (migrations.test_autodetector.AutodetectorTests)"]

**Base Commit**: d232fd76a85870daf345fd8f8d617fe7802ae194
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
