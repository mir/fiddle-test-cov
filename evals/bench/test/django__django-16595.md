# django__django-16595

**Repository**: django/django
**Created**: 2023-02-24T10:30:35Z
**Version**: 5.0

## Problem Statement

Migration optimizer does not reduce multiple AlterField
Description
	
Let's consider the following operations: 
operations = [
	migrations.AddField(
		model_name="book",
		name="title",
		field=models.CharField(max_length=256, null=True),
	),
	migrations.AlterField(
		model_name="book",
		name="title",
		field=models.CharField(max_length=128, null=True),
	),
	migrations.AlterField(
		model_name="book",
		name="title",
		field=models.CharField(max_length=128, null=True, help_text="help"),
	),
	migrations.AlterField(
		model_name="book",
		name="title",
		field=models.CharField(max_length=128, null=True, help_text="help", default=None),
	),
]
If I run the optimizer, I get only the AddField, as we could expect. However, if the AddField model is separated from the AlterField (e.g. because of a non-elidable migration, or inside a non-squashed migration), none of the AlterField are reduced:
optimizer.optimize(operations[1:], "books") 
[<AlterField model_name='book', name='title', field=<django.db.models.fields.CharField>>,
 <AlterField model_name='book', name='title', field=<django.db.models.fields.CharField>>,
 <AlterField model_name='book', name='title', field=<django.db.models.fields.CharField>>]
Indeed, the AlterField.reduce does not consider the the case where operation is also an AlterField. 
Is this behaviour intended? If so, could it be documented? 
Otherwise, would it make sense to add something like
		if isinstance(operation, AlterField) and self.is_same_field_operation(
			operation
		):
			return [operation]


## Hints

Your analysis is correct Laurent, the reduction of multiple AlterField against the same model is simply not implemented today hence why you're running into this behaviour. Given you're already half way there ​I would encourage you to submit a PR that adds these changes and ​an optimizer regression test to cover them if you'd like to see this issue fixed in future versions of Django.
Thanks Simon, I submitted a PR.
​PR

## Patch

```diff

diff --git a/django/db/migrations/operations/fields.py b/django/db/migrations/operations/fields.py
--- a/django/db/migrations/operations/fields.py
+++ b/django/db/migrations/operations/fields.py
@@ -247,9 +247,9 @@ def migration_name_fragment(self):
         return "alter_%s_%s" % (self.model_name_lower, self.name_lower)
 
     def reduce(self, operation, app_label):
-        if isinstance(operation, RemoveField) and self.is_same_field_operation(
-            operation
-        ):
+        if isinstance(
+            operation, (AlterField, RemoveField)
+        ) and self.is_same_field_operation(operation):
             return [operation]
         elif (
             isinstance(operation, RenameField)


```

## Test Patch

```diff
diff --git a/tests/migrations/test_optimizer.py b/tests/migrations/test_optimizer.py
--- a/tests/migrations/test_optimizer.py
+++ b/tests/migrations/test_optimizer.py
@@ -221,10 +221,10 @@ def test_create_alter_owrt_delete_model(self):
             migrations.AlterOrderWithRespectTo("Foo", "a")
         )
 
-    def _test_alter_alter_model(self, alter_foo, alter_bar):
+    def _test_alter_alter(self, alter_foo, alter_bar):
         """
         Two AlterUniqueTogether/AlterIndexTogether/AlterOrderWithRespectTo
-        should collapse into the second.
+        /AlterField should collapse into the second.
         """
         self.assertOptimizesTo(
             [
@@ -237,29 +237,35 @@ def _test_alter_alter_model(self, alter_foo, alter_bar):
         )
 
     def test_alter_alter_table_model(self):
-        self._test_alter_alter_model(
+        self._test_alter_alter(
             migrations.AlterModelTable("Foo", "a"),
             migrations.AlterModelTable("Foo", "b"),
         )
 
     def test_alter_alter_unique_model(self):
-        self._test_alter_alter_model(
+        self._test_alter_alter(
             migrations.AlterUniqueTogether("Foo", [["a", "b"]]),
             migrations.AlterUniqueTogether("Foo", [["a", "c"]]),
         )
 
     def test_alter_alter_index_model(self):
-        self._test_alter_alter_model(
+        self._test_alter_alter(
             migrations.AlterIndexTogether("Foo", [["a", "b"]]),
             migrations.AlterIndexTogether("Foo", [["a", "c"]]),
         )
 
     def test_alter_alter_owrt_model(self):
-        self._test_alter_alter_model(
+        self._test_alter_alter(
             migrations.AlterOrderWithRespectTo("Foo", "a"),
             migrations.AlterOrderWithRespectTo("Foo", "b"),
         )
 
+    def test_alter_alter_field(self):
+        self._test_alter_alter(
+            migrations.AlterField("Foo", "name", models.IntegerField()),
+            migrations.AlterField("Foo", "name", models.IntegerField(help_text="help")),
+        )
+
     def test_optimize_through_create(self):
         """
         We should be able to optimize away create/delete through a create or

```

## Test Information

**Tests that should FAIL→PASS**: ["test_alter_alter_field (migrations.test_optimizer.OptimizerTests.test_alter_alter_field)"]

**Tests that should PASS→PASS**: ["AlterField should optimize into AddField.", "RemoveField should cancel AddField", "RenameField should optimize into AddField", "test_alter_alter_index_model (migrations.test_optimizer.OptimizerTests.test_alter_alter_index_model)", "test_alter_alter_owrt_model (migrations.test_optimizer.OptimizerTests.test_alter_alter_owrt_model)", "test_alter_alter_table_model (migrations.test_optimizer.OptimizerTests.test_alter_alter_table_model)", "test_alter_alter_unique_model (migrations.test_optimizer.OptimizerTests.test_alter_alter_unique_model)", "RemoveField should absorb AlterField", "RenameField should optimize to the other side of AlterField,", "test_create_alter_index_delete_model (migrations.test_optimizer.OptimizerTests.test_create_alter_index_delete_model)", "test_create_alter_index_field (migrations.test_optimizer.OptimizerTests.test_create_alter_index_field)", "test_create_alter_model_managers (migrations.test_optimizer.OptimizerTests.test_create_alter_model_managers)", "test_create_alter_model_options (migrations.test_optimizer.OptimizerTests.test_create_alter_model_options)", "test_create_alter_owrt_delete_model (migrations.test_optimizer.OptimizerTests.test_create_alter_owrt_delete_model)", "test_create_alter_owrt_field (migrations.test_optimizer.OptimizerTests.test_create_alter_owrt_field)", "test_create_alter_unique_delete_model (migrations.test_optimizer.OptimizerTests.test_create_alter_unique_delete_model)", "test_create_alter_unique_field (migrations.test_optimizer.OptimizerTests.test_create_alter_unique_field)", "CreateModel and DeleteModel should collapse into nothing.", "AddField should optimize into CreateModel.", "AddField should NOT optimize into CreateModel if it's an M2M using a", "AlterField should optimize into CreateModel.", "test_create_model_and_remove_model_options (migrations.test_optimizer.OptimizerTests.test_create_model_and_remove_model_options)", "CreateModel order remains unchanged if the later AddField operation", "A CreateModel that inherits from another isn't reordered to avoid", "RemoveField should optimize into CreateModel.", "RenameField should optimize into CreateModel.", "AddField optimizes into CreateModel if it's a FK to a model that's", "CreateModel reordering behavior doesn't result in an infinite loop if", "CreateModel should absorb RenameModels.", "test_none_app_label (migrations.test_optimizer.OptimizerTests.test_none_app_label)", "test_optimize_elidable_operation (migrations.test_optimizer.OptimizerTests.test_optimize_elidable_operation)", "We should be able to optimize away create/delete through a create or", "field-level through checking is working. This should manage to collapse", "test_rename_index (migrations.test_optimizer.OptimizerTests.test_rename_index)", "RenameModels should absorb themselves.", "The optimizer does nothing on a single operation,", "test_swapping_fields_names (migrations.test_optimizer.OptimizerTests.test_swapping_fields_names)"]

**Base Commit**: f9fe062de5fc0896d6bbbf3f260b5c44473b3c77
**Environment Setup Commit**: 4a72da71001f154ea60906a2f74898d32b7322a7
