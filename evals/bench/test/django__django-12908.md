# django__django-12908

**Repository**: django/django
**Created**: 2020-05-13T11:36:48Z
**Version**: 3.2

## Problem Statement

Union queryset should raise on distinct().
Description
	 
		(last modified by Sielc Technologies)
	 
After using
.annotate() on 2 different querysets
and then .union()
.distinct() will not affect the queryset
	def setUp(self) -> None:
		user = self.get_or_create_admin_user()
		Sample.h.create(user, name="Sam1")
		Sample.h.create(user, name="Sam2 acid")
		Sample.h.create(user, name="Sam3")
		Sample.h.create(user, name="Sam4 acid")
		Sample.h.create(user, name="Dub")
		Sample.h.create(user, name="Dub")
		Sample.h.create(user, name="Dub")
		self.user = user
	def test_union_annotated_diff_distinct(self):
		qs = Sample.objects.filter(user=self.user)
		qs1 = qs.filter(name='Dub').annotate(rank=Value(0, IntegerField()))
		qs2 = qs.filter(name='Sam1').annotate(rank=Value(1, IntegerField()))
		qs = qs1.union(qs2)
		qs = qs.order_by('name').distinct('name') # THIS DISTINCT DOESN'T WORK
		self.assertEqual(qs.count(), 2)
expected to get wrapped union
	SELECT DISTINCT ON (siebox_sample.name) * FROM (SELECT ... UNION SELECT ...) AS siebox_sample


## Hints

distinct() is not supported but doesn't raise an error yet. As ​​per the documentation, "only LIMIT, OFFSET, COUNT(*), ORDER BY, and specifying columns (i.e. slicing, count(), order_by(), and values()/values_list()) are allowed on the resulting QuerySet.". Follow up to #27995.

## Patch

```diff

diff --git a/django/db/models/query.py b/django/db/models/query.py
--- a/django/db/models/query.py
+++ b/django/db/models/query.py
@@ -1138,6 +1138,7 @@ def distinct(self, *field_names):
         """
         Return a new QuerySet instance that will select only distinct results.
         """
+        self._not_support_combined_queries('distinct')
         assert not self.query.is_sliced, \
             "Cannot create distinct fields once a slice has been taken."
         obj = self._chain()


```

## Test Patch

```diff
diff --git a/tests/queries/test_qs_combinators.py b/tests/queries/test_qs_combinators.py
--- a/tests/queries/test_qs_combinators.py
+++ b/tests/queries/test_qs_combinators.py
@@ -272,6 +272,7 @@ def test_unsupported_operations_on_combined_qs(self):
                 'annotate',
                 'defer',
                 'delete',
+                'distinct',
                 'exclude',
                 'extra',
                 'filter',

```

## Test Information

**Tests that should FAIL→PASS**: ["test_unsupported_operations_on_combined_qs (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_unsupported_ordering_slicing_raises_db_error (queries.test_qs_combinators.QuerySetSetOperationTests)"]

**Tests that should PASS→PASS**: ["test_combining_multiple_models (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_count_difference (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_count_intersection (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_count_union (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_count_union_empty_result (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_difference_with_empty_qs (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_difference_with_values (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_intersection_with_empty_qs (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_intersection_with_values (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_limits (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_order_by_same_type (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_order_raises_on_non_selected_column (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_ordering (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_ordering_by_f_expression (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_qs_with_subcompound_qs (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_simple_difference (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_simple_intersection (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_simple_union (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_union_distinct (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_union_with_empty_qs (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_union_with_extra_and_values_list (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_union_with_two_annotated_values_list (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_union_with_values (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_union_with_values_list_and_order (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_union_with_values_list_on_annotated_and_unannotated (queries.test_qs_combinators.QuerySetSetOperationTests)"]

**Base Commit**: 49ae7ce50a874f8a04cd910882fb9571ff3a0d7a
**Environment Setup Commit**: 65dfb06a1ab56c238cc80f5e1c31f61210c4577d
