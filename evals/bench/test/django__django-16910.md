# django__django-16910

**Repository**: django/django
**Created**: 2023-05-31T22:28:10Z
**Version**: 5.0

## Problem Statement

QuerySet.only() doesn't work with select_related() on a reverse OneToOneField relation.
Description
	
On Django 4.2 calling only() with select_related() on a query using the reverse lookup for a OneToOne relation does not generate the correct query.
All the fields from the related model are still included in the generated SQL.
Sample models:
class Main(models.Model):
	main_field_1 = models.CharField(blank=True, max_length=45)
	main_field_2 = models.CharField(blank=True, max_length=45)
	main_field_3 = models.CharField(blank=True, max_length=45)
class Secondary(models.Model):
	main = models.OneToOneField(Main, primary_key=True, related_name='secondary', on_delete=models.CASCADE)
	secondary_field_1 = models.CharField(blank=True, max_length=45)
	secondary_field_2 = models.CharField(blank=True, max_length=45)
	secondary_field_3 = models.CharField(blank=True, max_length=45)
Sample code:
Main.objects.select_related('secondary').only('main_field_1', 'secondary__secondary_field_1')
Generated query on Django 4.2.1:
SELECT "bugtest_main"."id", "bugtest_main"."main_field_1", "bugtest_secondary"."main_id", "bugtest_secondary"."secondary_field_1", "bugtest_secondary"."secondary_field_2", "bugtest_secondary"."secondary_field_3" FROM "bugtest_main" LEFT OUTER JOIN "bugtest_secondary" ON ("bugtest_main"."id" = "bugtest_secondary"."main_id")
Generated query on Django 4.1.9:
SELECT "bugtest_main"."id", "bugtest_main"."main_field_1", "bugtest_secondary"."main_id", "bugtest_secondary"."secondary_field_1" FROM "bugtest_main" LEFT OUTER JOIN "bugtest_secondary" ON ("bugtest_main"."id" = "bugtest_secondary"."main_id")


## Hints

Thanks for the report! Regression in b3db6c8dcb5145f7d45eff517bcd96460475c879. Reproduced at 881cc139e2d53cc1d3ccea7f38faa960f9e56597.

## Patch

```diff

diff --git a/django/db/models/sql/query.py b/django/db/models/sql/query.py
--- a/django/db/models/sql/query.py
+++ b/django/db/models/sql/query.py
@@ -779,7 +779,13 @@ def _get_only_select_mask(self, opts, mask, select_mask=None):
         # Only include fields mentioned in the mask.
         for field_name, field_mask in mask.items():
             field = opts.get_field(field_name)
-            field_select_mask = select_mask.setdefault(field, {})
+            # Retrieve the actual field associated with reverse relationships
+            # as that's what is expected in the select mask.
+            if field in opts.related_objects:
+                field_key = field.field
+            else:
+                field_key = field
+            field_select_mask = select_mask.setdefault(field_key, {})
             if field_mask:
                 if not field.is_relation:
                     raise FieldError(next(iter(field_mask)))


```

## Test Patch

```diff
diff --git a/tests/defer_regress/tests.py b/tests/defer_regress/tests.py
--- a/tests/defer_regress/tests.py
+++ b/tests/defer_regress/tests.py
@@ -178,6 +178,16 @@ def test_reverse_one_to_one_relations(self):
             self.assertEqual(i.one_to_one_item.name, "second")
         with self.assertNumQueries(1):
             self.assertEqual(i.value, 42)
+        with self.assertNumQueries(1):
+            i = Item.objects.select_related("one_to_one_item").only(
+                "name", "one_to_one_item__item"
+            )[0]
+            self.assertEqual(i.one_to_one_item.pk, o2o.pk)
+            self.assertEqual(i.name, "first")
+        with self.assertNumQueries(1):
+            self.assertEqual(i.one_to_one_item.name, "second")
+        with self.assertNumQueries(1):
+            self.assertEqual(i.value, 42)
 
     def test_defer_with_select_related(self):
         item1 = Item.objects.create(name="first", value=47)
@@ -277,6 +287,28 @@ def test_defer_many_to_many_ignored(self):
         with self.assertNumQueries(1):
             self.assertEqual(Request.objects.defer("items").get(), request)
 
+    def test_only_many_to_many_ignored(self):
+        location = Location.objects.create()
+        request = Request.objects.create(location=location)
+        with self.assertNumQueries(1):
+            self.assertEqual(Request.objects.only("items").get(), request)
+
+    def test_defer_reverse_many_to_many_ignored(self):
+        location = Location.objects.create()
+        request = Request.objects.create(location=location)
+        item = Item.objects.create(value=1)
+        request.items.add(item)
+        with self.assertNumQueries(1):
+            self.assertEqual(Item.objects.defer("request").get(), item)
+
+    def test_only_reverse_many_to_many_ignored(self):
+        location = Location.objects.create()
+        request = Request.objects.create(location=location)
+        item = Item.objects.create(value=1)
+        request.items.add(item)
+        with self.assertNumQueries(1):
+            self.assertEqual(Item.objects.only("request").get(), item)
+
 
 class DeferDeletionSignalsTests(TestCase):
     senders = [Item, Proxy]
diff --git a/tests/select_related_onetoone/tests.py b/tests/select_related_onetoone/tests.py
--- a/tests/select_related_onetoone/tests.py
+++ b/tests/select_related_onetoone/tests.py
@@ -249,6 +249,9 @@ def test_inheritance_deferred2(self):
             self.assertEqual(p.child1.name2, "n2")
         p = qs.get(name2="n2")
         with self.assertNumQueries(0):
+            self.assertEqual(p.child1.value, 1)
+            self.assertEqual(p.child1.child4.value4, 4)
+        with self.assertNumQueries(2):
             self.assertEqual(p.child1.name1, "n1")
             self.assertEqual(p.child1.child4.name1, "n1")
 

```

## Test Information

**Tests that should FAIL→PASS**: ["test_inheritance_deferred2 (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_inheritance_deferred2)", "test_reverse_one_to_one_relations (defer_regress.tests.DeferRegressionTest.test_reverse_one_to_one_relations)"]

**Tests that should PASS→PASS**: ["test_reverse_related_validation (select_related_onetoone.tests.ReverseSelectRelatedValidationTests.test_reverse_related_validation)", "test_reverse_related_validation_with_filtered_relation (select_related_onetoone.tests.ReverseSelectRelatedValidationTests.test_reverse_related_validation_with_filtered_relation)", "test_delete_defered_model (defer_regress.tests.DeferDeletionSignalsTests.test_delete_defered_model)", "test_delete_defered_proxy_model (defer_regress.tests.DeferDeletionSignalsTests.test_delete_defered_proxy_model)", "test_back_and_forward (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_back_and_forward)", "test_basic (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_basic)", "test_follow_from_child_class (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_follow_from_child_class)", "test_follow_inheritance (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_follow_inheritance)", "test_follow_next_level (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_follow_next_level)", "test_follow_two (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_follow_two)", "test_follow_two_next_level (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_follow_two_next_level)", "test_forward_and_back (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_forward_and_back)", "test_inheritance_deferred (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_inheritance_deferred)", "Ticket #13839: select_related() should NOT cache None", "test_multiinheritance_two_subclasses (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_multiinheritance_two_subclasses)", "test_multiple_subclass (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_multiple_subclass)", "test_not_followed_by_default (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_not_followed_by_default)", "test_nullable_relation (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_nullable_relation)", "test_onetoone_with_subclass (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_onetoone_with_subclass)", "test_onetoone_with_two_subclasses (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_onetoone_with_two_subclasses)", "test_parent_only (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_parent_only)", "test_self_relation (select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_self_relation)", "test_basic (defer_regress.tests.DeferRegressionTest.test_basic)", "test_common_model_different_mask (defer_regress.tests.DeferRegressionTest.test_common_model_different_mask)", "test_defer_annotate_select_related (defer_regress.tests.DeferRegressionTest.test_defer_annotate_select_related)", "test_defer_many_to_many_ignored (defer_regress.tests.DeferRegressionTest.test_defer_many_to_many_ignored)", "test_defer_reverse_many_to_many_ignored (defer_regress.tests.DeferRegressionTest.test_defer_reverse_many_to_many_ignored)", "test_defer_with_select_related (defer_regress.tests.DeferRegressionTest.test_defer_with_select_related)", "test_only_and_defer_usage_on_proxy_models (defer_regress.tests.DeferRegressionTest.test_only_and_defer_usage_on_proxy_models)", "test_only_many_to_many_ignored (defer_regress.tests.DeferRegressionTest.test_only_many_to_many_ignored)", "test_only_reverse_many_to_many_ignored (defer_regress.tests.DeferRegressionTest.test_only_reverse_many_to_many_ignored)", "test_only_with_select_related (defer_regress.tests.DeferRegressionTest.test_only_with_select_related)", "test_proxy_model_defer_with_select_related (defer_regress.tests.DeferRegressionTest.test_proxy_model_defer_with_select_related)", "test_resolve_columns (defer_regress.tests.DeferRegressionTest.test_resolve_columns)", "test_ticket_16409 (defer_regress.tests.DeferRegressionTest.test_ticket_16409)", "test_ticket_23270 (defer_regress.tests.DeferRegressionTest.test_ticket_23270)"]

**Base Commit**: 4142739af1cda53581af4169dbe16d6cd5e26948
**Environment Setup Commit**: 4a72da71001f154ea60906a2f74898d32b7322a7
