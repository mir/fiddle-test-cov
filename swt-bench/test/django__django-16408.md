# django__django-16408

**Repository**: django/django
**Created**: 2022-12-29T02:08:29Z
**Version**: 5.0

## Problem Statement

Multi-level FilteredRelation with select_related() may set wrong related object.
Description
	
test case:
# add to known_related_objects.tests.ExistingRelatedInstancesTests
	def test_wrong_select_related(self):
		with self.assertNumQueries(3):
			p = list(PoolStyle.objects.annotate(
				tournament_pool=FilteredRelation('pool__tournament__pool'),
				).select_related('tournament_pool'))
			self.assertEqual(p[0].pool.tournament, p[0].tournament_pool.tournament)
result:
======================================================================
FAIL: test_wrong_select_related (known_related_objects.tests.ExistingRelatedInstancesTests.test_wrong_select_related)
----------------------------------------------------------------------
Traceback (most recent call last):
 File "D:\Work\django\tests\known_related_objects\tests.py", line 171, in test_wrong_select_related
	self.assertEqual(p[0].pool.tournament, p[0].tournament_pool.tournament)
AssertionError: <Tournament: Tournament object (1)> != <PoolStyle: PoolStyle object (1)>
----------------------------------------------------------------------


## Hints

Seems this bug can be fixed by: M django/db/models/sql/compiler.py @@ -1270,6 +1270,9 @@ class SQLCompiler: if from_obj: final_field.remote_field.set_cached_value(from_obj, obj) + def no_local_setter(obj, from_obj): + pass + def remote_setter(name, obj, from_obj): setattr(from_obj, name, obj) @@ -1291,7 +1294,7 @@ class SQLCompiler: "model": model, "field": final_field, "reverse": True, - "local_setter": partial(local_setter, final_field), + "local_setter": partial(local_setter, final_field) if len(joins) <= 2 else no_local_setter, "remote_setter": partial(remote_setter, name), "from_parent": from_parent, }
"cyclic" is not the case. Try the test below: def test_wrong_select_related2(self): with self.assertNumQueries(3): p = list( Tournament.objects.filter(id=self.t2.id).annotate( style=FilteredRelation('pool__another_style'), ).select_related('style') ) self.assertEqual(self.ps3, p[0].style) self.assertEqual(self.p1, p[0].style.pool) self.assertEqual(self.p3, p[0].style.another_pool) result: ====================================================================== FAIL: test_wrong_select_related2 (known_related_objects.tests.ExistingRelatedInstancesTests.test_wrong_select_related2) ---------------------------------------------------------------------- Traceback (most recent call last): File "/repos/django/tests/known_related_objects/tests.py", line 186, in test_wrong_select_related2 self.assertEqual(self.p3, p[0].style.another_pool) AssertionError: <Pool: Pool object (3)> != <Tournament: Tournament object (2)> ---------------------------------------------------------------------- The query fetch t2 and ps3, then call remote_setter('style', ps3, t2) and local_setter(t2, ps3). The joins is ['known_related_objects_tournament', 'known_related_objects_pool', 'style']. The type of the first argument of the local_setter should be joins[-2], but query do not fetch that object, so no available local_setter when len(joins) > 2.
​https://github.com/django/django/pull/16408

## Patch

```diff

diff --git a/django/db/models/sql/compiler.py b/django/db/models/sql/compiler.py
--- a/django/db/models/sql/compiler.py
+++ b/django/db/models/sql/compiler.py
@@ -1274,6 +1274,9 @@ def local_setter(final_field, obj, from_obj):
                 if from_obj:
                     final_field.remote_field.set_cached_value(from_obj, obj)
 
+            def local_setter_noop(obj, from_obj):
+                pass
+
             def remote_setter(name, obj, from_obj):
                 setattr(from_obj, name, obj)
 
@@ -1295,7 +1298,11 @@ def remote_setter(name, obj, from_obj):
                         "model": model,
                         "field": final_field,
                         "reverse": True,
-                        "local_setter": partial(local_setter, final_field),
+                        "local_setter": (
+                            partial(local_setter, final_field)
+                            if len(joins) <= 2
+                            else local_setter_noop
+                        ),
                         "remote_setter": partial(remote_setter, name),
                         "from_parent": from_parent,
                     }


```

## Test Patch

```diff
diff --git a/tests/known_related_objects/tests.py b/tests/known_related_objects/tests.py
--- a/tests/known_related_objects/tests.py
+++ b/tests/known_related_objects/tests.py
@@ -164,3 +164,23 @@ def test_reverse_fk_select_related_multiple(self):
             )
             self.assertIs(ps[0], ps[0].pool_1.poolstyle)
             self.assertIs(ps[0], ps[0].pool_2.another_style)
+
+    def test_multilevel_reverse_fk_cyclic_select_related(self):
+        with self.assertNumQueries(3):
+            p = list(
+                PoolStyle.objects.annotate(
+                    tournament_pool=FilteredRelation("pool__tournament__pool"),
+                ).select_related("tournament_pool", "tournament_pool__tournament")
+            )
+            self.assertEqual(p[0].tournament_pool.tournament, p[0].pool.tournament)
+
+    def test_multilevel_reverse_fk_select_related(self):
+        with self.assertNumQueries(2):
+            p = list(
+                Tournament.objects.filter(id=self.t2.id)
+                .annotate(
+                    style=FilteredRelation("pool__another_style"),
+                )
+                .select_related("style")
+            )
+            self.assertEqual(p[0].style.another_pool, self.p3)

```

## Test Information

**Tests that should FAIL→PASS**: ["test_multilevel_reverse_fk_cyclic_select_related (known_related_objects.tests.ExistingRelatedInstancesTests.test_multilevel_reverse_fk_cyclic_select_related)", "test_multilevel_reverse_fk_select_related (known_related_objects.tests.ExistingRelatedInstancesTests.test_multilevel_reverse_fk_select_related)"]

**Tests that should PASS→PASS**: ["test_foreign_key (known_related_objects.tests.ExistingRelatedInstancesTests.test_foreign_key)", "test_foreign_key_multiple_prefetch (known_related_objects.tests.ExistingRelatedInstancesTests.test_foreign_key_multiple_prefetch)", "test_foreign_key_prefetch_related (known_related_objects.tests.ExistingRelatedInstancesTests.test_foreign_key_prefetch_related)", "test_one_to_one (known_related_objects.tests.ExistingRelatedInstancesTests.test_one_to_one)", "test_one_to_one_multi_prefetch_related (known_related_objects.tests.ExistingRelatedInstancesTests.test_one_to_one_multi_prefetch_related)", "test_one_to_one_multi_select_related (known_related_objects.tests.ExistingRelatedInstancesTests.test_one_to_one_multi_select_related)", "test_one_to_one_prefetch_related (known_related_objects.tests.ExistingRelatedInstancesTests.test_one_to_one_prefetch_related)", "test_one_to_one_select_related (known_related_objects.tests.ExistingRelatedInstancesTests.test_one_to_one_select_related)", "test_queryset_and (known_related_objects.tests.ExistingRelatedInstancesTests.test_queryset_and)", "test_queryset_or (known_related_objects.tests.ExistingRelatedInstancesTests.test_queryset_or)", "test_queryset_or_different_cached_items (known_related_objects.tests.ExistingRelatedInstancesTests.test_queryset_or_different_cached_items)", "test_queryset_or_only_one_with_precache (known_related_objects.tests.ExistingRelatedInstancesTests.test_queryset_or_only_one_with_precache)", "test_reverse_fk_select_related_multiple (known_related_objects.tests.ExistingRelatedInstancesTests.test_reverse_fk_select_related_multiple)", "test_reverse_one_to_one (known_related_objects.tests.ExistingRelatedInstancesTests.test_reverse_one_to_one)", "test_reverse_one_to_one_multi_prefetch_related (known_related_objects.tests.ExistingRelatedInstancesTests.test_reverse_one_to_one_multi_prefetch_related)", "test_reverse_one_to_one_multi_select_related (known_related_objects.tests.ExistingRelatedInstancesTests.test_reverse_one_to_one_multi_select_related)", "test_reverse_one_to_one_prefetch_related (known_related_objects.tests.ExistingRelatedInstancesTests.test_reverse_one_to_one_prefetch_related)", "test_reverse_one_to_one_select_related (known_related_objects.tests.ExistingRelatedInstancesTests.test_reverse_one_to_one_select_related)"]

**Base Commit**: ef85b6bf0bc5a8b194f0724cf5bbedbcee402b96
**Environment Setup Commit**: 4a72da71001f154ea60906a2f74898d32b7322a7
