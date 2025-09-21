# django__django-12747

**Repository**: django/django
**Created**: 2020-04-18T16:41:40Z
**Version**: 3.1

## Problem Statement

QuerySet.Delete - inconsistent result when zero objects deleted
Description
	
The result format of the QuerySet.Delete method is a tuple: (X, Y) 
X - is the total amount of deleted objects (including foreign key deleted objects)
Y - is a dictionary specifying counters of deleted objects for each specific model (the key is the _meta.label of the model and the value is counter of deleted objects of this model).
Example: <class 'tuple'>: (2, {'my_app.FileAccess': 1, 'my_app.File': 1})
When there are zero objects to delete in total - the result is inconsistent:
For models with foreign keys - the result will be: <class 'tuple'>: (0, {})
For "simple" models without foreign key - the result will be: <class 'tuple'>: (0, {'my_app.BlockLibrary': 0})
I would expect there will be no difference between the two cases: Either both will have the empty dictionary OR both will have dictionary with model-label keys and zero value.


## Hints

I guess we could adapt the code not to include any key if the count is zero in the second case.

## Patch

```diff

diff --git a/django/db/models/deletion.py b/django/db/models/deletion.py
--- a/django/db/models/deletion.py
+++ b/django/db/models/deletion.py
@@ -408,7 +408,8 @@ def delete(self):
             # fast deletes
             for qs in self.fast_deletes:
                 count = qs._raw_delete(using=self.using)
-                deleted_counter[qs.model._meta.label] += count
+                if count:
+                    deleted_counter[qs.model._meta.label] += count
 
             # update fields
             for model, instances_for_fieldvalues in self.field_updates.items():
@@ -426,7 +427,8 @@ def delete(self):
                 query = sql.DeleteQuery(model)
                 pk_list = [obj.pk for obj in instances]
                 count = query.delete_batch(pk_list, self.using)
-                deleted_counter[model._meta.label] += count
+                if count:
+                    deleted_counter[model._meta.label] += count
 
                 if not model._meta.auto_created:
                     for obj in instances:


```

## Test Patch

```diff
diff --git a/tests/delete/tests.py b/tests/delete/tests.py
--- a/tests/delete/tests.py
+++ b/tests/delete/tests.py
@@ -522,11 +522,10 @@ def test_queryset_delete_returns_num_rows(self):
         existed_objs = {
             R._meta.label: R.objects.count(),
             HiddenUser._meta.label: HiddenUser.objects.count(),
-            A._meta.label: A.objects.count(),
-            MR._meta.label: MR.objects.count(),
             HiddenUserProfile._meta.label: HiddenUserProfile.objects.count(),
         }
         deleted, deleted_objs = R.objects.all().delete()
+        self.assertCountEqual(deleted_objs.keys(), existed_objs.keys())
         for k, v in existed_objs.items():
             self.assertEqual(deleted_objs[k], v)
 
@@ -550,13 +549,13 @@ def test_model_delete_returns_num_rows(self):
         existed_objs = {
             R._meta.label: R.objects.count(),
             HiddenUser._meta.label: HiddenUser.objects.count(),
-            A._meta.label: A.objects.count(),
             MR._meta.label: MR.objects.count(),
             HiddenUserProfile._meta.label: HiddenUserProfile.objects.count(),
             M.m2m.through._meta.label: M.m2m.through.objects.count(),
         }
         deleted, deleted_objs = r.delete()
         self.assertEqual(deleted, sum(existed_objs.values()))
+        self.assertCountEqual(deleted_objs.keys(), existed_objs.keys())
         for k, v in existed_objs.items():
             self.assertEqual(deleted_objs[k], v)
 
@@ -694,7 +693,7 @@ def test_fast_delete_empty_no_update_can_self_select(self):
         with self.assertNumQueries(1):
             self.assertEqual(
                 User.objects.filter(avatar__desc='missing').delete(),
-                (0, {'delete.User': 0})
+                (0, {}),
             )
 
     def test_fast_delete_combined_relationships(self):

```

## Test Information

**Tests that should FAIL→PASS**: ["test_fast_delete_empty_no_update_can_self_select (delete.tests.FastDeleteTests)", "test_model_delete_returns_num_rows (delete.tests.DeletionTests)", "test_queryset_delete_returns_num_rows (delete.tests.DeletionTests)"]

**Tests that should PASS→PASS**: ["test_fast_delete_combined_relationships (delete.tests.FastDeleteTests)", "test_fast_delete_fk (delete.tests.FastDeleteTests)", "test_fast_delete_inheritance (delete.tests.FastDeleteTests)", "test_fast_delete_instance_set_pk_none (delete.tests.FastDeleteTests)", "test_fast_delete_joined_qs (delete.tests.FastDeleteTests)", "test_fast_delete_large_batch (delete.tests.FastDeleteTests)", "test_fast_delete_m2m (delete.tests.FastDeleteTests)", "test_fast_delete_qs (delete.tests.FastDeleteTests)", "test_fast_delete_revm2m (delete.tests.FastDeleteTests)", "test_auto (delete.tests.OnDeleteTests)", "test_auto_nullable (delete.tests.OnDeleteTests)", "test_cascade (delete.tests.OnDeleteTests)", "test_cascade_from_child (delete.tests.OnDeleteTests)", "test_cascade_from_parent (delete.tests.OnDeleteTests)", "test_cascade_nullable (delete.tests.OnDeleteTests)", "test_do_nothing (delete.tests.OnDeleteTests)", "test_do_nothing_qscount (delete.tests.OnDeleteTests)", "test_inheritance_cascade_down (delete.tests.OnDeleteTests)", "test_inheritance_cascade_up (delete.tests.OnDeleteTests)", "test_non_callable (delete.tests.OnDeleteTests)", "test_o2o_setnull (delete.tests.OnDeleteTests)", "test_protect (delete.tests.OnDeleteTests)", "test_protect_multiple (delete.tests.OnDeleteTests)", "test_protect_path (delete.tests.OnDeleteTests)", "test_restrict (delete.tests.OnDeleteTests)", "test_restrict_gfk_no_fast_delete (delete.tests.OnDeleteTests)", "test_restrict_multiple (delete.tests.OnDeleteTests)", "test_restrict_path_cascade_direct (delete.tests.OnDeleteTests)", "test_restrict_path_cascade_indirect (delete.tests.OnDeleteTests)", "test_restrict_path_cascade_indirect_diamond (delete.tests.OnDeleteTests)", "test_setdefault (delete.tests.OnDeleteTests)", "test_setdefault_none (delete.tests.OnDeleteTests)", "test_setnull (delete.tests.OnDeleteTests)", "test_setnull_from_child (delete.tests.OnDeleteTests)", "test_setnull_from_parent (delete.tests.OnDeleteTests)", "test_setvalue (delete.tests.OnDeleteTests)", "test_bulk (delete.tests.DeletionTests)", "test_can_defer_constraint_checks (delete.tests.DeletionTests)", "test_delete_with_keeping_parents (delete.tests.DeletionTests)", "test_delete_with_keeping_parents_relationships (delete.tests.DeletionTests)", "test_deletion_order (delete.tests.DeletionTests)", "test_hidden_related (delete.tests.DeletionTests)", "test_instance_update (delete.tests.DeletionTests)", "test_large_delete (delete.tests.DeletionTests)", "test_large_delete_related (delete.tests.DeletionTests)", "test_m2m (delete.tests.DeletionTests)", "test_only_referenced_fields_selected (delete.tests.DeletionTests)", "test_proxied_model_duplicate_queries (delete.tests.DeletionTests)", "test_relational_post_delete_signals_happen_before_parent_object (delete.tests.DeletionTests)"]

**Base Commit**: c86201b6ed4f8256b0a0520c08aa674f623d4127
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
