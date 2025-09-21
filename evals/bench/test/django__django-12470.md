# django__django-12470

**Repository**: django/django
**Created**: 2020-02-19T04:48:55Z
**Version**: 3.1

## Problem Statement

Inherited model doesn't correctly order by "-pk" when specified on Parent.Meta.ordering
Description
	
Given the following model definition:
from django.db import models
class Parent(models.Model):
	class Meta:
		ordering = ["-pk"]
class Child(Parent):
	pass
Querying the Child class results in the following:
>>> print(Child.objects.all().query)
SELECT "myapp_parent"."id", "myapp_child"."parent_ptr_id" FROM "myapp_child" INNER JOIN "myapp_parent" ON ("myapp_child"."parent_ptr_id" = "myapp_parent"."id") ORDER BY "myapp_parent"."id" ASC
The query is ordered ASC but I expect the order to be DESC.


## Patch

```diff

diff --git a/django/db/models/sql/compiler.py b/django/db/models/sql/compiler.py
--- a/django/db/models/sql/compiler.py
+++ b/django/db/models/sql/compiler.py
@@ -709,9 +709,9 @@ def find_ordering_name(self, name, opts, alias=None, default_order='ASC',
         field, targets, alias, joins, path, opts, transform_function = self._setup_joins(pieces, opts, alias)
 
         # If we get to this point and the field is a relation to another model,
-        # append the default ordering for that model unless the attribute name
-        # of the field is specified.
-        if field.is_relation and opts.ordering and getattr(field, 'attname', None) != name:
+        # append the default ordering for that model unless it is the pk
+        # shortcut or the attribute name of the field that is specified.
+        if field.is_relation and opts.ordering and getattr(field, 'attname', None) != name and name != 'pk':
             # Firstly, avoid infinite loops.
             already_seen = already_seen or set()
             join_tuple = tuple(getattr(self.query.alias_map[j], 'join_cols', None) for j in joins)


```

## Test Patch

```diff
diff --git a/tests/model_inheritance/models.py b/tests/model_inheritance/models.py
--- a/tests/model_inheritance/models.py
+++ b/tests/model_inheritance/models.py
@@ -181,6 +181,8 @@ class GrandParent(models.Model):
     place = models.ForeignKey(Place, models.CASCADE, null=True, related_name='+')
 
     class Meta:
+        # Ordering used by test_inherited_ordering_pk_desc.
+        ordering = ['-pk']
         unique_together = ('first_name', 'last_name')
 
 
diff --git a/tests/model_inheritance/tests.py b/tests/model_inheritance/tests.py
--- a/tests/model_inheritance/tests.py
+++ b/tests/model_inheritance/tests.py
@@ -7,7 +7,7 @@
 
 from .models import (
     Base, Chef, CommonInfo, GrandChild, GrandParent, ItalianRestaurant,
-    MixinModel, ParkingLot, Place, Post, Restaurant, Student, SubBase,
+    MixinModel, Parent, ParkingLot, Place, Post, Restaurant, Student, SubBase,
     Supplier, Title, Worker,
 )
 
@@ -204,6 +204,19 @@ class A(models.Model):
 
         self.assertEqual(A.attr.called, (A, 'attr'))
 
+    def test_inherited_ordering_pk_desc(self):
+        p1 = Parent.objects.create(first_name='Joe', email='joe@email.com')
+        p2 = Parent.objects.create(first_name='Jon', email='jon@email.com')
+        expected_order_by_sql = 'ORDER BY %s.%s DESC' % (
+            connection.ops.quote_name(Parent._meta.db_table),
+            connection.ops.quote_name(
+                Parent._meta.get_field('grandparent_ptr').column
+            ),
+        )
+        qs = Parent.objects.all()
+        self.assertSequenceEqual(qs, [p2, p1])
+        self.assertIn(expected_order_by_sql, str(qs.query))
+
 
 class ModelInheritanceDataTests(TestCase):
     @classmethod

```

## Test Information

**Tests that should FAIL→PASS**: ["test_inherited_ordering_pk_desc (model_inheritance.tests.ModelInheritanceTests)"]

**Tests that should PASS→PASS**: ["test_abstract_fk_related_name (model_inheritance.tests.InheritanceSameModelNameTests)", "test_unique (model_inheritance.tests.InheritanceUniqueTests)", "test_unique_together (model_inheritance.tests.InheritanceUniqueTests)", "test_abstract (model_inheritance.tests.ModelInheritanceTests)", "test_abstract_parent_link (model_inheritance.tests.ModelInheritanceTests)", "Creating a child with non-abstract parents only issues INSERTs.", "test_custompk_m2m (model_inheritance.tests.ModelInheritanceTests)", "test_eq (model_inheritance.tests.ModelInheritanceTests)", "test_init_subclass (model_inheritance.tests.ModelInheritanceTests)", "test_meta_fields_and_ordering (model_inheritance.tests.ModelInheritanceTests)", "test_mixin_init (model_inheritance.tests.ModelInheritanceTests)", "test_model_with_distinct_accessors (model_inheritance.tests.ModelInheritanceTests)", "test_model_with_distinct_related_query_name (model_inheritance.tests.ModelInheritanceTests)", "test_reverse_relation_for_different_hierarchy_tree (model_inheritance.tests.ModelInheritanceTests)", "test_set_name (model_inheritance.tests.ModelInheritanceTests)", "test_update_parent_filtering (model_inheritance.tests.ModelInheritanceTests)", "test_exclude_inherited_on_null (model_inheritance.tests.ModelInheritanceDataTests)", "test_filter_inherited_model (model_inheritance.tests.ModelInheritanceDataTests)", "test_filter_inherited_on_null (model_inheritance.tests.ModelInheritanceDataTests)", "test_filter_on_parent_returns_object_of_parent_type (model_inheritance.tests.ModelInheritanceDataTests)", "test_inherited_does_not_exist_exception (model_inheritance.tests.ModelInheritanceDataTests)", "test_inherited_multiple_objects_returned_exception (model_inheritance.tests.ModelInheritanceDataTests)", "test_parent_cache_reuse (model_inheritance.tests.ModelInheritanceDataTests)", "test_parent_child_one_to_one_link (model_inheritance.tests.ModelInheritanceDataTests)", "test_parent_child_one_to_one_link_on_nonrelated_objects (model_inheritance.tests.ModelInheritanceDataTests)", "test_parent_fields_available_for_filtering_in_child_model (model_inheritance.tests.ModelInheritanceDataTests)", "test_related_objects_for_inherited_models (model_inheritance.tests.ModelInheritanceDataTests)", "test_select_related_defer (model_inheritance.tests.ModelInheritanceDataTests)", "test_select_related_works_on_parent_model_fields (model_inheritance.tests.ModelInheritanceDataTests)", "test_update_inherited_model (model_inheritance.tests.ModelInheritanceDataTests)", "test_update_query_counts (model_inheritance.tests.ModelInheritanceDataTests)", "test_update_works_on_parent_and_child_models_at_once (model_inheritance.tests.ModelInheritanceDataTests)", "test_values_works_on_parent_model_fields (model_inheritance.tests.ModelInheritanceDataTests)"]

**Base Commit**: 142ab6846ac09d6d401e26fc8b6b988a583ac0f5
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
