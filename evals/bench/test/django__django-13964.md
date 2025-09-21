# django__django-13964

**Repository**: django/django
**Created**: 2021-02-02T17:07:43Z
**Version**: 4.0

## Problem Statement

Saving parent object after setting on child leads to data loss for parents with non-numeric primary key.
Description
	 
		(last modified by Charlie DeTar)
	 
Given a model with a foreign key relation to another model that has a non-auto CharField as its primary key:
class Product(models.Model):
	sku = models.CharField(primary_key=True, max_length=50)
class Order(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
If the relation is initialized on the parent with an empty instance that does not yet specify its primary key, and the primary key is subsequently defined, the parent does not "see" the primary key's change:
with transaction.atomic():
	order = Order()
	order.product = Product()
	order.product.sku = "foo"
	order.product.save()
	order.save()
	assert Order.objects.filter(product_id="").exists() # Succeeds, but shouldn't
	assert Order.objects.filter(product=order.product).exists() # Fails
Instead of product_id being populated with product.sku, it is set to emptystring. The foreign key constraint which would enforce the existence of a product with sku="" is deferred until the transaction commits. The transaction does correctly fail on commit with a ForeignKeyViolation due to the non-existence of a product with emptystring as its primary key.
On the other hand, if the related unsaved instance is initialized with its primary key before assignment to the parent, it is persisted correctly:
with transaction.atomic():
	order = Order()
	order.product = Product(sku="foo")
	order.product.save()
	order.save()
	assert Order.objects.filter(product=order.product).exists() # succeeds
Committing the transaction also succeeds.
This may have something to do with how the Order.product_id field is handled at assignment, together with something about handling fetching of auto vs non-auto primary keys from the related instance.


## Hints

Thanks for this report. product_id is an empty string in ​_prepare_related_fields_for_save() that's why pk from a related object is not used. We could use empty_values: diff --git a/django/db/models/base.py b/django/db/models/base.py index 822aad080d..8e7a8e3ae7 100644 --- a/django/db/models/base.py +++ b/django/db/models/base.py @@ -933,7 +933,7 @@ class Model(metaclass=ModelBase): "%s() prohibited to prevent data loss due to unsaved " "related object '%s'." % (operation_name, field.name) ) - elif getattr(self, field.attname) is None: + elif getattr(self, field.attname) in field.empty_values: # Use pk from related object if it has been saved after # an assignment. setattr(self, field.attname, obj.pk) but I'm not sure. Related with #28147.

## Patch

```diff

diff --git a/django/db/models/base.py b/django/db/models/base.py
--- a/django/db/models/base.py
+++ b/django/db/models/base.py
@@ -933,7 +933,7 @@ def _prepare_related_fields_for_save(self, operation_name):
                         "%s() prohibited to prevent data loss due to unsaved "
                         "related object '%s'." % (operation_name, field.name)
                     )
-                elif getattr(self, field.attname) is None:
+                elif getattr(self, field.attname) in field.empty_values:
                     # Use pk from related object if it has been saved after
                     # an assignment.
                     setattr(self, field.attname, obj.pk)


```

## Test Patch

```diff
diff --git a/tests/many_to_one/models.py b/tests/many_to_one/models.py
--- a/tests/many_to_one/models.py
+++ b/tests/many_to_one/models.py
@@ -68,6 +68,10 @@ class Parent(models.Model):
     bestchild = models.ForeignKey('Child', models.SET_NULL, null=True, related_name='favored_by')
 
 
+class ParentStringPrimaryKey(models.Model):
+    name = models.CharField(primary_key=True, max_length=15)
+
+
 class Child(models.Model):
     name = models.CharField(max_length=20)
     parent = models.ForeignKey(Parent, models.CASCADE)
@@ -77,6 +81,10 @@ class ChildNullableParent(models.Model):
     parent = models.ForeignKey(Parent, models.CASCADE, null=True)
 
 
+class ChildStringPrimaryKeyParent(models.Model):
+    parent = models.ForeignKey(ParentStringPrimaryKey, on_delete=models.CASCADE)
+
+
 class ToFieldChild(models.Model):
     parent = models.ForeignKey(Parent, models.CASCADE, to_field='name', related_name='to_field_children')
 
diff --git a/tests/many_to_one/tests.py b/tests/many_to_one/tests.py
--- a/tests/many_to_one/tests.py
+++ b/tests/many_to_one/tests.py
@@ -7,9 +7,9 @@
 from django.utils.translation import gettext_lazy
 
 from .models import (
-    Article, Category, Child, ChildNullableParent, City, Country, District,
-    First, Parent, Record, Relation, Reporter, School, Student, Third,
-    ToFieldChild,
+    Article, Category, Child, ChildNullableParent, ChildStringPrimaryKeyParent,
+    City, Country, District, First, Parent, ParentStringPrimaryKey, Record,
+    Relation, Reporter, School, Student, Third, ToFieldChild,
 )
 
 
@@ -549,6 +549,16 @@ def test_save_nullable_fk_after_parent_with_to_field(self):
         self.assertEqual(child.parent, parent)
         self.assertEqual(child.parent_id, parent.name)
 
+    def test_save_fk_after_parent_with_non_numeric_pk_set_on_child(self):
+        parent = ParentStringPrimaryKey()
+        child = ChildStringPrimaryKeyParent(parent=parent)
+        child.parent.name = 'jeff'
+        parent.save()
+        child.save()
+        child.refresh_from_db()
+        self.assertEqual(child.parent, parent)
+        self.assertEqual(child.parent_id, parent.name)
+
     def test_fk_to_bigautofield(self):
         ch = City.objects.create(name='Chicago')
         District.objects.create(city=ch, name='Far South')

```

## Test Information

**Tests that should FAIL→PASS**: ["test_save_fk_after_parent_with_non_numeric_pk_set_on_child (many_to_one.tests.ManyToOneTests)"]

**Tests that should PASS→PASS**: ["test_add (many_to_one.tests.ManyToOneTests)", "test_add_after_prefetch (many_to_one.tests.ManyToOneTests)", "test_add_remove_set_by_pk_raises (many_to_one.tests.ManyToOneTests)", "test_add_then_remove_after_prefetch (many_to_one.tests.ManyToOneTests)", "test_assign (many_to_one.tests.ManyToOneTests)", "test_assign_fk_id_none (many_to_one.tests.ManyToOneTests)", "test_assign_fk_id_value (many_to_one.tests.ManyToOneTests)", "test_cached_foreign_key_with_to_field_not_cleared_by_save (many_to_one.tests.ManyToOneTests)", "Model.save() invalidates stale ForeignKey relations after a primary key", "test_clear_after_prefetch (many_to_one.tests.ManyToOneTests)", "test_create (many_to_one.tests.ManyToOneTests)", "test_create_relation_with_gettext_lazy (many_to_one.tests.ManyToOneTests)", "test_deepcopy_and_circular_references (many_to_one.tests.ManyToOneTests)", "test_delete (many_to_one.tests.ManyToOneTests)", "test_explicit_fk (many_to_one.tests.ManyToOneTests)", "test_fk_assignment_and_related_object_cache (many_to_one.tests.ManyToOneTests)", "test_fk_instantiation_outside_model (many_to_one.tests.ManyToOneTests)", "test_fk_to_bigautofield (many_to_one.tests.ManyToOneTests)", "test_fk_to_smallautofield (many_to_one.tests.ManyToOneTests)", "test_get (many_to_one.tests.ManyToOneTests)", "test_hasattr_related_object (many_to_one.tests.ManyToOneTests)", "test_manager_class_caching (many_to_one.tests.ManyToOneTests)", "test_multiple_foreignkeys (many_to_one.tests.ManyToOneTests)", "test_related_object (many_to_one.tests.ManyToOneTests)", "test_relation_unsaved (many_to_one.tests.ManyToOneTests)", "test_remove_after_prefetch (many_to_one.tests.ManyToOneTests)", "test_reverse_assignment_deprecation (many_to_one.tests.ManyToOneTests)", "test_reverse_foreign_key_instance_to_field_caching (many_to_one.tests.ManyToOneTests)", "test_reverse_selects (many_to_one.tests.ManyToOneTests)", "test_save_nullable_fk_after_parent (many_to_one.tests.ManyToOneTests)", "test_save_nullable_fk_after_parent_with_to_field (many_to_one.tests.ManyToOneTests)", "test_select_related (many_to_one.tests.ManyToOneTests)", "test_selects (many_to_one.tests.ManyToOneTests)", "test_set (many_to_one.tests.ManyToOneTests)", "test_set_after_prefetch (many_to_one.tests.ManyToOneTests)", "test_values_list_exception (many_to_one.tests.ManyToOneTests)"]

**Base Commit**: f39634ff229887bf7790c069d0c411b38494ca38
**Environment Setup Commit**: 475cffd1d64c690cdad16ede4d5e81985738ceb4
