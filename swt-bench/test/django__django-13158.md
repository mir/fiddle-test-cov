# django__django-13158

**Repository**: django/django
**Created**: 2020-07-06T19:18:11Z
**Version**: 3.2

## Problem Statement

QuerySet.none() on combined queries returns all results.
Description
	
I came across this issue on Stack Overflow. I'm not 100% sure it's a bug, but it does seem strange. With this code (excuse the bizarre example filtering):
class Publication(models.Model):
	pass
class Article(models.Model):
	publications = models.ManyToManyField(to=Publication, blank=True, null=True)
class ArticleForm(forms.ModelForm):
	publications = forms.ModelMultipleChoiceField(
		Publication.objects.filter(id__lt=2) | Publication.objects.filter(id__gt=5),
		required=False,
	)
	class Meta:
		model = Article
		fields = ["publications"]
class ArticleAdmin(admin.ModelAdmin):
	form = ArticleForm
This works well. However, changing the ModelMultipleChoiceField queryset to use union() breaks things.
publications = forms.ModelMultipleChoiceField(
	Publication.objects.filter(id__lt=2).union(
		Publication.objects.filter(id__gt=5)
	),
	required=False,
)
The form correctly shows only the matching objects. However, if you submit this form while empty (i.e. you didn't select any publications), ALL objects matching the queryset will be added. Using the OR query, NO objects are added, as I'd expect.


## Hints

Thanks for the report. QuerySet.none() doesn't work properly on combined querysets, it returns all results instead of an empty queryset.

## Patch

```diff

diff --git a/django/db/models/sql/query.py b/django/db/models/sql/query.py
--- a/django/db/models/sql/query.py
+++ b/django/db/models/sql/query.py
@@ -305,6 +305,7 @@ def clone(self):
             obj.annotation_select_mask = None
         else:
             obj.annotation_select_mask = self.annotation_select_mask.copy()
+        obj.combined_queries = tuple(query.clone() for query in self.combined_queries)
         # _annotation_select_cache cannot be copied, as doing so breaks the
         # (necessary) state in which both annotations and
         # _annotation_select_cache point to the same underlying objects.
@@ -1777,6 +1778,8 @@ def split_exclude(self, filter_expr, can_reuse, names_with_path):
 
     def set_empty(self):
         self.where.add(NothingNode(), AND)
+        for query in self.combined_queries:
+            query.set_empty()
 
     def is_empty(self):
         return any(isinstance(c, NothingNode) for c in self.where.children)


```

## Test Patch

```diff
diff --git a/tests/queries/test_qs_combinators.py b/tests/queries/test_qs_combinators.py
--- a/tests/queries/test_qs_combinators.py
+++ b/tests/queries/test_qs_combinators.py
@@ -51,6 +51,13 @@ def test_union_distinct(self):
         self.assertEqual(len(list(qs1.union(qs2, all=True))), 20)
         self.assertEqual(len(list(qs1.union(qs2))), 10)
 
+    def test_union_none(self):
+        qs1 = Number.objects.filter(num__lte=1)
+        qs2 = Number.objects.filter(num__gte=8)
+        qs3 = qs1.union(qs2)
+        self.assertSequenceEqual(qs3.none(), [])
+        self.assertNumbersEqual(qs3, [0, 1, 8, 9], ordered=False)
+
     @skipUnlessDBFeature('supports_select_intersection')
     def test_intersection_with_empty_qs(self):
         qs1 = Number.objects.all()

```

## Test Information

**Tests that should FAIL→PASS**: ["test_union_none (queries.test_qs_combinators.QuerySetSetOperationTests)"]

**Tests that should PASS→PASS**: ["test_combining_multiple_models (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_count_difference (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_count_intersection (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_count_union (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_count_union_empty_result (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_difference_with_empty_qs (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_difference_with_values (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_intersection_with_empty_qs (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_intersection_with_values (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_limits (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_order_by_same_type (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_order_raises_on_non_selected_column (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_ordering (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_ordering_by_alias (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_ordering_by_f_expression (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_ordering_by_f_expression_and_alias (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_qs_with_subcompound_qs (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_simple_difference (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_simple_intersection (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_simple_union (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_union_distinct (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_union_with_empty_qs (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_union_with_extra_and_values_list (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_union_with_two_annotated_values_list (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_union_with_values (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_union_with_values_list_and_order (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_union_with_values_list_on_annotated_and_unannotated (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_unsupported_operations_on_combined_qs (queries.test_qs_combinators.QuerySetSetOperationTests)", "test_unsupported_ordering_slicing_raises_db_error (queries.test_qs_combinators.QuerySetSetOperationTests)"]

**Base Commit**: 7af8f4127397279d19ef7c7899e93018274e2f9b
**Environment Setup Commit**: 65dfb06a1ab56c238cc80f5e1c31f61210c4577d
