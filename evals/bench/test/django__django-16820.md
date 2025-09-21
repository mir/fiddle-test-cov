# django__django-16820

**Repository**: django/django
**Created**: 2023-05-02T06:32:13Z
**Version**: 5.0

## Problem Statement

Squashing migrations with Meta.index_together -> indexes transition should remove deprecation warnings.
Description
	
Squashing migrations with Meta.index_together -> Meta.indexes transition should remove deprecation warnings. As far as I'm aware, it's a 4.2 release blocker because you cannot get rid of the index_together deprecation warnings without rewriting migrations, see comment.


## Patch

```diff

diff --git a/django/db/migrations/operations/models.py b/django/db/migrations/operations/models.py
--- a/django/db/migrations/operations/models.py
+++ b/django/db/migrations/operations/models.py
@@ -303,6 +303,71 @@ def reduce(self, operation, app_label):
                         managers=self.managers,
                     ),
                 ]
+        elif (
+            isinstance(operation, IndexOperation)
+            and self.name_lower == operation.model_name_lower
+        ):
+            if isinstance(operation, AddIndex):
+                return [
+                    CreateModel(
+                        self.name,
+                        fields=self.fields,
+                        options={
+                            **self.options,
+                            "indexes": [
+                                *self.options.get("indexes", []),
+                                operation.index,
+                            ],
+                        },
+                        bases=self.bases,
+                        managers=self.managers,
+                    ),
+                ]
+            elif isinstance(operation, RemoveIndex):
+                options_indexes = [
+                    index
+                    for index in self.options.get("indexes", [])
+                    if index.name != operation.name
+                ]
+                return [
+                    CreateModel(
+                        self.name,
+                        fields=self.fields,
+                        options={
+                            **self.options,
+                            "indexes": options_indexes,
+                        },
+                        bases=self.bases,
+                        managers=self.managers,
+                    ),
+                ]
+            elif isinstance(operation, RenameIndex) and operation.old_fields:
+                options_index_together = {
+                    fields
+                    for fields in self.options.get("index_together", [])
+                    if fields != operation.old_fields
+                }
+                if options_index_together:
+                    self.options["index_together"] = options_index_together
+                else:
+                    self.options.pop("index_together", None)
+                return [
+                    CreateModel(
+                        self.name,
+                        fields=self.fields,
+                        options={
+                            **self.options,
+                            "indexes": [
+                                *self.options.get("indexes", []),
+                                models.Index(
+                                    fields=operation.old_fields, name=operation.new_name
+                                ),
+                            ],
+                        },
+                        bases=self.bases,
+                        managers=self.managers,
+                    ),
+                ]
         return super().reduce(operation, app_label)
 
 


```

## Test Patch

```diff
diff --git a/tests/migrations/test_autodetector.py b/tests/migrations/test_autodetector.py
--- a/tests/migrations/test_autodetector.py
+++ b/tests/migrations/test_autodetector.py
@@ -2266,10 +2266,9 @@ def test_same_app_circular_fk_dependency_with_unique_together_and_indexes(self):
             changes,
             "eggs",
             0,
-            ["CreateModel", "CreateModel", "AddIndex", "AlterUniqueTogether"],
+            ["CreateModel", "CreateModel"],
         )
         self.assertNotIn("unique_together", changes["eggs"][0].operations[0].options)
-        self.assertNotIn("unique_together", changes["eggs"][0].operations[1].options)
         self.assertMigrationDependencies(changes, "eggs", 0, [])
 
     def test_alter_db_table_add(self):
@@ -2565,6 +2564,9 @@ def test(from_state, to_state, msg):
 
     def test_create_model_with_indexes(self):
         """Test creation of new model with indexes already defined."""
+        added_index = models.Index(
+            fields=["name"], name="create_model_with_indexes_idx"
+        )
         author = ModelState(
             "otherapp",
             "Author",
@@ -2573,25 +2575,25 @@ def test_create_model_with_indexes(self):
                 ("name", models.CharField(max_length=200)),
             ],
             {
-                "indexes": [
-                    models.Index(fields=["name"], name="create_model_with_indexes_idx")
-                ]
+                "indexes": [added_index],
             },
         )
         changes = self.get_changes([], [author])
-        added_index = models.Index(
-            fields=["name"], name="create_model_with_indexes_idx"
-        )
         # Right number of migrations?
         self.assertEqual(len(changes["otherapp"]), 1)
         # Right number of actions?
         migration = changes["otherapp"][0]
-        self.assertEqual(len(migration.operations), 2)
+        self.assertEqual(len(migration.operations), 1)
         # Right actions order?
-        self.assertOperationTypes(changes, "otherapp", 0, ["CreateModel", "AddIndex"])
+        self.assertOperationTypes(changes, "otherapp", 0, ["CreateModel"])
         self.assertOperationAttributes(changes, "otherapp", 0, 0, name="Author")
         self.assertOperationAttributes(
-            changes, "otherapp", 0, 1, model_name="author", index=added_index
+            changes,
+            "otherapp",
+            0,
+            0,
+            name="Author",
+            options={"indexes": [added_index]},
         )
 
     def test_add_indexes(self):
@@ -4043,62 +4045,69 @@ def test_add_model_order_with_respect_to_unique_together(self):
             },
         )
 
-    def test_add_model_order_with_respect_to_index_constraint(self):
-        tests = [
-            (
-                "AddIndex",
-                {
-                    "indexes": [
-                        models.Index(fields=["_order"], name="book_order_idx"),
-                    ]
-                },
-            ),
-            (
-                "AddConstraint",
-                {
-                    "constraints": [
-                        models.CheckConstraint(
-                            check=models.Q(_order__gt=1),
-                            name="book_order_gt_1",
-                        ),
-                    ]
-                },
-            ),
-        ]
-        for operation, extra_option in tests:
-            with self.subTest(operation=operation):
-                after = ModelState(
-                    "testapp",
-                    "Author",
-                    [
-                        ("id", models.AutoField(primary_key=True)),
-                        ("name", models.CharField(max_length=200)),
-                        ("book", models.ForeignKey("otherapp.Book", models.CASCADE)),
-                    ],
-                    options={
-                        "order_with_respect_to": "book",
-                        **extra_option,
-                    },
-                )
-                changes = self.get_changes([], [self.book, after])
-                self.assertNumberMigrations(changes, "testapp", 1)
-                self.assertOperationTypes(
-                    changes,
-                    "testapp",
-                    0,
-                    [
-                        "CreateModel",
-                        operation,
-                    ],
-                )
-                self.assertOperationAttributes(
-                    changes,
-                    "testapp",
-                    0,
-                    0,
-                    name="Author",
-                    options={"order_with_respect_to": "book"},
-                )
+    def test_add_model_order_with_respect_to_constraint(self):
+        after = ModelState(
+            "testapp",
+            "Author",
+            [
+                ("id", models.AutoField(primary_key=True)),
+                ("name", models.CharField(max_length=200)),
+                ("book", models.ForeignKey("otherapp.Book", models.CASCADE)),
+            ],
+            options={
+                "order_with_respect_to": "book",
+                "constraints": [
+                    models.CheckConstraint(
+                        check=models.Q(_order__gt=1), name="book_order_gt_1"
+                    ),
+                ],
+            },
+        )
+        changes = self.get_changes([], [self.book, after])
+        self.assertNumberMigrations(changes, "testapp", 1)
+        self.assertOperationTypes(
+            changes,
+            "testapp",
+            0,
+            ["CreateModel", "AddConstraint"],
+        )
+        self.assertOperationAttributes(
+            changes,
+            "testapp",
+            0,
+            0,
+            name="Author",
+            options={"order_with_respect_to": "book"},
+        )
+
+    def test_add_model_order_with_respect_to_index(self):
+        after = ModelState(
+            "testapp",
+            "Author",
+            [
+                ("id", models.AutoField(primary_key=True)),
+                ("name", models.CharField(max_length=200)),
+                ("book", models.ForeignKey("otherapp.Book", models.CASCADE)),
+            ],
+            options={
+                "order_with_respect_to": "book",
+                "indexes": [models.Index(fields=["_order"], name="book_order_idx")],
+            },
+        )
+        changes = self.get_changes([], [self.book, after])
+        self.assertNumberMigrations(changes, "testapp", 1)
+        self.assertOperationTypes(changes, "testapp", 0, ["CreateModel"])
+        self.assertOperationAttributes(
+            changes,
+            "testapp",
+            0,
+            0,
+            name="Author",
+            options={
+                "order_with_respect_to": "book",
+                "indexes": [models.Index(fields=["_order"], name="book_order_idx")],
+            },
+        )
 
     def test_set_alter_order_with_respect_to_index_constraint_unique_together(self):
         tests = [
diff --git a/tests/migrations/test_optimizer.py b/tests/migrations/test_optimizer.py
--- a/tests/migrations/test_optimizer.py
+++ b/tests/migrations/test_optimizer.py
@@ -1172,3 +1172,181 @@ def test_add_remove_index(self):
             ],
             [],
         )
+
+    def test_create_model_add_index(self):
+        self.assertOptimizesTo(
+            [
+                migrations.CreateModel(
+                    name="Pony",
+                    fields=[
+                        ("weight", models.IntegerField()),
+                        ("age", models.IntegerField()),
+                    ],
+                    options={
+                        "indexes": [models.Index(fields=["age"], name="idx_pony_age")],
+                    },
+                ),
+                migrations.AddIndex(
+                    "Pony",
+                    models.Index(fields=["weight"], name="idx_pony_weight"),
+                ),
+            ],
+            [
+                migrations.CreateModel(
+                    name="Pony",
+                    fields=[
+                        ("weight", models.IntegerField()),
+                        ("age", models.IntegerField()),
+                    ],
+                    options={
+                        "indexes": [
+                            models.Index(fields=["age"], name="idx_pony_age"),
+                            models.Index(fields=["weight"], name="idx_pony_weight"),
+                        ],
+                    },
+                ),
+            ],
+        )
+
+    def test_create_model_remove_index(self):
+        self.assertOptimizesTo(
+            [
+                migrations.CreateModel(
+                    name="Pony",
+                    fields=[
+                        ("weight", models.IntegerField()),
+                        ("age", models.IntegerField()),
+                    ],
+                    options={
+                        "indexes": [
+                            models.Index(fields=["age"], name="idx_pony_age"),
+                            models.Index(fields=["weight"], name="idx_pony_weight"),
+                        ],
+                    },
+                ),
+                migrations.RemoveIndex("Pony", "idx_pony_age"),
+            ],
+            [
+                migrations.CreateModel(
+                    name="Pony",
+                    fields=[
+                        ("weight", models.IntegerField()),
+                        ("age", models.IntegerField()),
+                    ],
+                    options={
+                        "indexes": [
+                            models.Index(fields=["weight"], name="idx_pony_weight"),
+                        ],
+                    },
+                ),
+            ],
+        )
+
+    def test_create_model_remove_index_together_rename_index(self):
+        self.assertOptimizesTo(
+            [
+                migrations.CreateModel(
+                    name="Pony",
+                    fields=[
+                        ("weight", models.IntegerField()),
+                        ("age", models.IntegerField()),
+                    ],
+                    options={
+                        "index_together": [("age", "weight")],
+                    },
+                ),
+                migrations.RenameIndex(
+                    "Pony", new_name="idx_pony_age_weight", old_fields=("age", "weight")
+                ),
+            ],
+            [
+                migrations.CreateModel(
+                    name="Pony",
+                    fields=[
+                        ("weight", models.IntegerField()),
+                        ("age", models.IntegerField()),
+                    ],
+                    options={
+                        "indexes": [
+                            models.Index(
+                                fields=["age", "weight"], name="idx_pony_age_weight"
+                            ),
+                        ],
+                    },
+                ),
+            ],
+        )
+
+    def test_create_model_index_together_rename_index(self):
+        self.assertOptimizesTo(
+            [
+                migrations.CreateModel(
+                    name="Pony",
+                    fields=[
+                        ("weight", models.IntegerField()),
+                        ("age", models.IntegerField()),
+                        ("height", models.IntegerField()),
+                        ("rank", models.IntegerField()),
+                    ],
+                    options={
+                        "index_together": [("age", "weight"), ("height", "rank")],
+                    },
+                ),
+                migrations.RenameIndex(
+                    "Pony", new_name="idx_pony_age_weight", old_fields=("age", "weight")
+                ),
+            ],
+            [
+                migrations.CreateModel(
+                    name="Pony",
+                    fields=[
+                        ("weight", models.IntegerField()),
+                        ("age", models.IntegerField()),
+                        ("height", models.IntegerField()),
+                        ("rank", models.IntegerField()),
+                    ],
+                    options={
+                        "index_together": {("height", "rank")},
+                        "indexes": [
+                            models.Index(
+                                fields=["age", "weight"], name="idx_pony_age_weight"
+                            ),
+                        ],
+                    },
+                ),
+            ],
+        )
+
+    def test_create_model_rename_index_no_old_fields(self):
+        self.assertOptimizesTo(
+            [
+                migrations.CreateModel(
+                    name="Pony",
+                    fields=[
+                        ("weight", models.IntegerField()),
+                        ("age", models.IntegerField()),
+                    ],
+                    options={
+                        "indexes": [models.Index(fields=["age"], name="idx_pony_age")],
+                    },
+                ),
+                migrations.RenameIndex(
+                    "Pony", new_name="idx_pony_age_new", old_name="idx_pony_age"
+                ),
+            ],
+            [
+                migrations.CreateModel(
+                    name="Pony",
+                    fields=[
+                        ("weight", models.IntegerField()),
+                        ("age", models.IntegerField()),
+                    ],
+                    options={
+                        "indexes": [models.Index(fields=["age"], name="idx_pony_age")],
+                    },
+                ),
+                migrations.RenameIndex(
+                    "Pony", new_name="idx_pony_age_new", old_name="idx_pony_age"
+                ),
+            ],
+        )

```

## Test Information

**Tests that should FAIL→PASS**: ["test_create_model_add_index (migrations.test_optimizer.OptimizerTests.test_create_model_add_index)", "test_create_model_index_together_rename_index (migrations.test_optimizer.OptimizerTests.test_create_model_index_together_rename_index)", "test_create_model_remove_index (migrations.test_optimizer.OptimizerTests.test_create_model_remove_index)", "test_create_model_remove_index_together_rename_index (migrations.test_optimizer.OptimizerTests.test_create_model_remove_index_together_rename_index)", "test_add_model_order_with_respect_to_index (migrations.test_autodetector.AutodetectorTests.test_add_model_order_with_respect_to_index)", "Test creation of new model with indexes already defined.", "#22275 - A migration with circular FK dependency does not try"]

**Tests that should PASS→PASS**: ["test_auto (migrations.test_autodetector.MigrationSuggestNameTests.test_auto)", "test_many_operations_suffix (migrations.test_autodetector.MigrationSuggestNameTests.test_many_operations_suffix)", "test_no_operations (migrations.test_autodetector.MigrationSuggestNameTests.test_no_operations)", "test_no_operations_initial (migrations.test_autodetector.MigrationSuggestNameTests.test_no_operations_initial)", "test_none_name (migrations.test_autodetector.MigrationSuggestNameTests.test_none_name)", "test_none_name_with_initial_true (migrations.test_autodetector.MigrationSuggestNameTests.test_none_name_with_initial_true)", "test_operation_with_invalid_chars_in_suggested_name (migrations.test_autodetector.MigrationSuggestNameTests.test_operation_with_invalid_chars_in_suggested_name)", "test_operation_with_no_suggested_name (migrations.test_autodetector.MigrationSuggestNameTests.test_operation_with_no_suggested_name)", "test_single_operation (migrations.test_autodetector.MigrationSuggestNameTests.test_single_operation)", "test_single_operation_long_name (migrations.test_autodetector.MigrationSuggestNameTests.test_single_operation_long_name)", "test_two_create_models (migrations.test_autodetector.MigrationSuggestNameTests.test_two_create_models)", "test_two_create_models_with_initial_true (migrations.test_autodetector.MigrationSuggestNameTests.test_two_create_models_with_initial_true)", "test_two_operations (migrations.test_autodetector.MigrationSuggestNameTests.test_two_operations)", "Added fields will be created before using them in index_together.", "test_add_index_together (migrations.test_autodetector.AutodetectorIndexTogetherTests.test_add_index_together)", "test_add_model_order_with_respect_to_index_together (migrations.test_autodetector.AutodetectorIndexTogetherTests.test_add_model_order_with_respect_to_index_together)", "Fields are altered after deleting some index_together.", "test_create_model_and_index_together (migrations.test_autodetector.AutodetectorIndexTogetherTests.test_create_model_and_index_together)", "Empty index_together shouldn't generate a migration.", "index_together doesn't generate a migration if no changes have been", "index_together triggers on ordering changes.", "test_index_together_remove_fk (migrations.test_autodetector.AutodetectorIndexTogetherTests.test_index_together_remove_fk)", "test_partly_alter_index_together_decrease (migrations.test_autodetector.AutodetectorIndexTogetherTests.test_partly_alter_index_together_decrease)", "test_partly_alter_index_together_increase (migrations.test_autodetector.AutodetectorIndexTogetherTests.test_partly_alter_index_together_increase)", "Removed fields will be removed after updating index_together.", "test_remove_index_together (migrations.test_autodetector.AutodetectorIndexTogetherTests.test_remove_index_together)", "Fields are renamed before updating index_together.", "test_rename_index_together_to_index (migrations.test_autodetector.AutodetectorIndexTogetherTests.test_rename_index_together_to_index)", "test_rename_index_together_to_index_extra_options (migrations.test_autodetector.AutodetectorIndexTogetherTests.test_rename_index_together_to_index_extra_options)", "test_rename_index_together_to_index_order_fields (migrations.test_autodetector.AutodetectorIndexTogetherTests.test_rename_index_together_to_index_order_fields)", "test_set_alter_order_with_respect_to_index_together (migrations.test_autodetector.AutodetectorIndexTogetherTests.test_set_alter_order_with_respect_to_index_together)", "AlterField should optimize into AddField.", "RemoveField should cancel AddField", "RenameField should optimize into AddField", "test_add_remove_index (migrations.test_optimizer.OptimizerTests.test_add_remove_index)", "test_alter_alter_field (migrations.test_optimizer.OptimizerTests.test_alter_alter_field)", "test_alter_alter_index_model (migrations.test_optimizer.OptimizerTests.test_alter_alter_index_model)", "test_alter_alter_owrt_model (migrations.test_optimizer.OptimizerTests.test_alter_alter_owrt_model)", "test_alter_alter_table_model (migrations.test_optimizer.OptimizerTests.test_alter_alter_table_model)", "test_alter_alter_unique_model (migrations.test_optimizer.OptimizerTests.test_alter_alter_unique_model)", "RemoveField should absorb AlterField", "RenameField should optimize to the other side of AlterField,", "test_create_alter_index_delete_model (migrations.test_optimizer.OptimizerTests.test_create_alter_index_delete_model)", "test_create_alter_index_field (migrations.test_optimizer.OptimizerTests.test_create_alter_index_field)", "test_create_alter_model_managers (migrations.test_optimizer.OptimizerTests.test_create_alter_model_managers)", "test_create_alter_model_options (migrations.test_optimizer.OptimizerTests.test_create_alter_model_options)", "test_create_alter_owrt_delete_model (migrations.test_optimizer.OptimizerTests.test_create_alter_owrt_delete_model)", "test_create_alter_owrt_field (migrations.test_optimizer.OptimizerTests.test_create_alter_owrt_field)", "test_create_alter_unique_delete_model (migrations.test_optimizer.OptimizerTests.test_create_alter_unique_delete_model)", "test_create_alter_unique_field (migrations.test_optimizer.OptimizerTests.test_create_alter_unique_field)", "CreateModel and DeleteModel should collapse into nothing.", "AddField should optimize into CreateModel.", "AddField should NOT optimize into CreateModel if it's an M2M using a", "AlterField should optimize into CreateModel.", "test_create_model_and_remove_model_options (migrations.test_optimizer.OptimizerTests.test_create_model_and_remove_model_options)", "CreateModel order remains unchanged if the later AddField operation", "A CreateModel that inherits from another isn't reordered to avoid", "RemoveField should optimize into CreateModel.", "RenameField should optimize into CreateModel.", "test_create_model_rename_index_no_old_fields (migrations.test_optimizer.OptimizerTests.test_create_model_rename_index_no_old_fields)", "AddField optimizes into CreateModel if it's a FK to a model that's", "CreateModel reordering behavior doesn't result in an infinite loop if", "CreateModel should absorb RenameModels.", "test_none_app_label (migrations.test_optimizer.OptimizerTests.test_none_app_label)", "test_optimize_elidable_operation (migrations.test_optimizer.OptimizerTests.test_optimize_elidable_operation)", "We should be able to optimize away create/delete through a create or", "field-level through checking is working. This should manage to collapse", "test_rename_index (migrations.test_optimizer.OptimizerTests.test_rename_index)", "RenameModels should absorb themselves.", "The optimizer does nothing on a single operation,", "test_swapping_fields_names (migrations.test_optimizer.OptimizerTests.test_swapping_fields_names)", "Setting order_with_respect_to when adding the FK too does", "#23405 - Adding a NOT NULL and blank `CharField` or `TextField`", "Test change detection of new constraints.", "test_add_constraints_with_new_model (migrations.test_autodetector.AutodetectorTests.test_add_constraints_with_new_model)", "test_add_custom_fk_with_hardcoded_to (migrations.test_autodetector.AutodetectorTests.test_add_custom_fk_with_hardcoded_to)", "test_add_date_fields_with_auto_now_add_asking_for_default (migrations.test_autodetector.AutodetectorTests.test_add_date_fields_with_auto_now_add_asking_for_default)", "test_add_date_fields_with_auto_now_add_not_asking_for_null_addition (migrations.test_autodetector.AutodetectorTests.test_add_date_fields_with_auto_now_add_not_asking_for_null_addition)", "test_add_date_fields_with_auto_now_not_asking_for_default (migrations.test_autodetector.AutodetectorTests.test_add_date_fields_with_auto_now_not_asking_for_default)", "Tests autodetection of new fields.", "Added fields will be created before using them in unique_together.", "#22030 - Adding a field with a default should work.", "test_add_index_with_new_model (migrations.test_autodetector.AutodetectorTests.test_add_index_with_new_model)", "Test change detection of new indexes.", "#22435 - Adding a ManyToManyField should not prompt for a default.", "Setting order_with_respect_to when adding the whole model", "test_add_model_order_with_respect_to_constraint (migrations.test_autodetector.AutodetectorTests.test_add_model_order_with_respect_to_constraint)", "test_add_model_order_with_respect_to_unique_together (migrations.test_autodetector.AutodetectorTests.test_add_model_order_with_respect_to_unique_together)", "Removing a base field takes place before adding a new inherited model", "#23405 - Adding a NOT NULL and non-blank `CharField` or `TextField`", "Tests unique_together detection.", "Tests detection for adding db_table in model's options.", "Tests detection for changing db_table in model's options'.", "test_alter_db_table_comment_add (migrations.test_autodetector.AutodetectorTests.test_alter_db_table_comment_add)", "test_alter_db_table_comment_change (migrations.test_autodetector.AutodetectorTests.test_alter_db_table_comment_change)", "test_alter_db_table_comment_no_changes (migrations.test_autodetector.AutodetectorTests.test_alter_db_table_comment_no_changes)", "test_alter_db_table_comment_remove (migrations.test_autodetector.AutodetectorTests.test_alter_db_table_comment_remove)", "Alter_db_table doesn't generate a migration if no changes have been made.", "Tests detection for removing db_table in model's options.", "Tests when model and db_table changes, autodetector must create two", "Fields are altered after deleting some unique_together.", "test_alter_field_to_fk_dependency_other_app (migrations.test_autodetector.AutodetectorTests.test_alter_field_to_fk_dependency_other_app)", "#23609 - Tests autodetection of nullable to non-nullable alterations.", "ForeignKeys are altered _before_ the model they used to", "test_alter_many_to_many (migrations.test_autodetector.AutodetectorTests.test_alter_many_to_many)", "Changing the model managers adds a new operation.", "Changing a model's options should make a change.", "Changing a proxy model's options should also make a change.", "test_alter_regex_string_to_compiled_regex (migrations.test_autodetector.AutodetectorTests.test_alter_regex_string_to_compiled_regex)", "test_alter_unique_together_fk_to_m2m (migrations.test_autodetector.AutodetectorTests.test_alter_unique_together_fk_to_m2m)", "Tests auto-naming of migrations for graph matching.", "test_arrange_for_graph_with_multiple_initial (migrations.test_autodetector.AutodetectorTests.test_arrange_for_graph_with_multiple_initial)", "Bases of other models come first.", "test_bases_first_mixed_case_app_label (migrations.test_autodetector.AutodetectorTests.test_bases_first_mixed_case_app_label)", "#23315 - The dependency resolver knows to put all CreateModel", "#23322 - The dependency resolver knows to explicitly resolve", "Having a circular ForeignKey dependency automatically", "#23938 - Changing a concrete field into a ManyToManyField", "test_create_model_and_unique_together (migrations.test_autodetector.AutodetectorTests.test_create_model_and_unique_together)", "Test creation of new model with constraints already defined.", "Adding a m2m with a through model and the models that use it should be", "test_create_with_through_model_separate_apps (migrations.test_autodetector.AutodetectorTests.test_create_with_through_model_separate_apps)", "Two instances which deconstruct to the same value aren't considered a", "Tests custom naming of migrations for graph matching.", "Field instances are handled correctly by nested deconstruction.", "#22951 -- Uninstantiated classes with deconstruct are correctly returned", "Nested deconstruction descends into dict values.", "Nested deconstruction descends into lists.", "Nested deconstruction descends into tuples.", "test_default_related_name_option (migrations.test_autodetector.AutodetectorTests.test_default_related_name_option)", "test_different_regex_does_alter (migrations.test_autodetector.AutodetectorTests.test_different_regex_does_alter)", "Empty unique_together shouldn't generate a migration.", "A dependency to an app with no migrations uses __first__.", "Having a ForeignKey automatically adds a dependency.", "#23100 - ForeignKeys correctly depend on other apps' models.", "Removing an FK and the model it targets in the same change must remove", "test_identical_regex_doesnt_alter (migrations.test_autodetector.AutodetectorTests.test_identical_regex_doesnt_alter)", "Tests when model changes but db_table stays as-is, autodetector must not", "A dependency to an app with existing migrations uses the", "A model with a m2m field that specifies a \"through\" model cannot be", "test_managed_to_unmanaged (migrations.test_autodetector.AutodetectorTests.test_managed_to_unmanaged)", "#23938 - Changing a ManyToManyField into a concrete field", "Removing a ManyToManyField and the \"through\" model in the same change", "Removing a model that contains a ManyToManyField and the \"through\" model", "test_mti_inheritance_model_removal (migrations.test_autodetector.AutodetectorTests.test_mti_inheritance_model_removal)", "Inheriting models doesn't move *_ptr fields into AddField operations.", "Nested deconstruction is applied recursively to the args/kwargs of", "Tests autodetection of new models.", "If two models with a ForeignKey from one to the other are removed at the", "Tests deletion of old models.", "Test change detection of reordering of fields in indexes.", "test_parse_number (migrations.test_autodetector.AutodetectorTests.test_parse_number)", "test_partly_alter_unique_together_decrease (migrations.test_autodetector.AutodetectorTests.test_partly_alter_unique_together_decrease)", "test_partly_alter_unique_together_increase (migrations.test_autodetector.AutodetectorTests.test_partly_alter_unique_together_increase)", "A relation used as the primary key is kept as part of CreateModel.", "The autodetector correctly deals with proxy models.", "Bases of proxies come first.", "#23415 - The autodetector must correctly deal with custom FK on proxy", "FK dependencies still work on proxy models.", "test_proxy_non_model_parent (migrations.test_autodetector.AutodetectorTests.test_proxy_non_model_parent)", "test_proxy_to_mti_with_fk_to_proxy (migrations.test_autodetector.AutodetectorTests.test_proxy_to_mti_with_fk_to_proxy)", "test_proxy_to_mti_with_fk_to_proxy_proxy (migrations.test_autodetector.AutodetectorTests.test_proxy_to_mti_with_fk_to_proxy_proxy)", "Removing order_with_respect_to when removing the FK too does", "Test change detection of removed constraints.", "Tests autodetection of removed fields.", "Removed fields will be removed after updating unique_together.", "Test change detection of removed indexes.", "Tests autodetection of renamed fields.", "Fields are renamed before updating unique_together.", "test_rename_field_foreign_key_to_field (migrations.test_autodetector.AutodetectorTests.test_rename_field_foreign_key_to_field)", "RenameField is used if a field is renamed and db_column equal to the", "test_rename_field_with_renamed_model (migrations.test_autodetector.AutodetectorTests.test_rename_field_with_renamed_model)", "test_rename_foreign_object_fields (migrations.test_autodetector.AutodetectorTests.test_rename_foreign_object_fields)", "test_rename_indexes (migrations.test_autodetector.AutodetectorTests.test_rename_indexes)", "Tests autodetection of renamed models that are used in M2M relations as", "Tests autodetection of renamed models.", "Model name is case-insensitive. Changing case doesn't lead to any", "The migration to rename a model pointed to by a foreign key in another", "#24537 - The order of fields in a model does not influence", "Tests autodetection of renamed models while simultaneously renaming one", "test_rename_referenced_primary_key (migrations.test_autodetector.AutodetectorTests.test_rename_referenced_primary_key)", "test_rename_related_field_preserved_db_column (migrations.test_autodetector.AutodetectorTests.test_rename_related_field_preserved_db_column)", "test_renamed_referenced_m2m_model_case (migrations.test_autodetector.AutodetectorTests.test_renamed_referenced_m2m_model_case)", "#22300 - Adding an FK in the same \"spot\" as a deleted CharField should", "A migration with a FK between two models of the same app does", "A migration with a FK between two models of the same app", "Setting order_with_respect_to adds a field.", "test_set_alter_order_with_respect_to_index_constraint_unique_together (migrations.test_autodetector.AutodetectorTests.test_set_alter_order_with_respect_to_index_constraint_unique_together)", "test_supports_functools_partial (migrations.test_autodetector.AutodetectorTests.test_supports_functools_partial)", "test_swappable (migrations.test_autodetector.AutodetectorTests.test_swappable)", "test_swappable_changed (migrations.test_autodetector.AutodetectorTests.test_swappable_changed)", "test_swappable_circular_multi_mti (migrations.test_autodetector.AutodetectorTests.test_swappable_circular_multi_mti)", "Swappable models get their CreateModel first.", "test_swappable_lowercase (migrations.test_autodetector.AutodetectorTests.test_swappable_lowercase)", "test_swappable_many_to_many_model_case (migrations.test_autodetector.AutodetectorTests.test_swappable_many_to_many_model_case)", "Trim does not remove dependencies but does remove unwanted apps.", "unique_together doesn't generate a migration if no", "unique_together also triggers on ordering changes.", "Tests unique_together and field removal detection & ordering", "The autodetector correctly deals with managed models.", "#23415 - The autodetector must correctly deal with custom FK on", "test_unmanaged_delete (migrations.test_autodetector.AutodetectorTests.test_unmanaged_delete)", "test_unmanaged_to_managed (migrations.test_autodetector.AutodetectorTests.test_unmanaged_to_managed)"]

**Base Commit**: c61219a7ae051d2baab53f041e00592011fc550c
**Environment Setup Commit**: 4a72da71001f154ea60906a2f74898d32b7322a7
