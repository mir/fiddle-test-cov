# django__django-12589

**Repository**: django/django
**Created**: 2020-03-19T19:04:17Z
**Version**: 3.1

## Problem Statement

Django 3.0: "GROUP BY" clauses error with tricky field annotation
Description
	
Let's pretend that we have next model structure with next model's relations:
class A(models.Model):
	bs = models.ManyToManyField('B',
								related_name="a",
								through="AB")
class B(models.Model):
	pass
class AB(models.Model):
	a = models.ForeignKey(A, on_delete=models.CASCADE, related_name="ab_a")
	b = models.ForeignKey(B, on_delete=models.CASCADE, related_name="ab_b")
	status = models.IntegerField()
class C(models.Model):
	a = models.ForeignKey(
		A,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="c",
		verbose_name=_("a")
	)
	status = models.IntegerField()
Let's try to evaluate next query
ab_query = AB.objects.filter(a=OuterRef("pk"), b=1)
filter_conditions = Q(pk=1) | Q(ab_a__b=1)
query = A.objects.\
	filter(filter_conditions).\
	annotate(
		status=Subquery(ab_query.values("status")),
		c_count=Count("c"),
)
answer = query.values("status").annotate(total_count=Count("status"))
print(answer.query)
print(answer)
On Django 3.0.4 we have an error
django.db.utils.ProgrammingError: column reference "status" is ambiguous
and query is next:
SELECT (SELECT U0."status" FROM "test_app_ab" U0 WHERE (U0."a_id" = "test_app_a"."id" AND U0."b_id" = 1)) AS "status", COUNT((SELECT U0."status" FROM "test_app_ab" U0 WHERE (U0."a_id" = "test_app_a"."id" AND U0."b_id" = 1))) AS "total_count" FROM "test_app_a" LEFT OUTER JOIN "test_app_ab" ON ("test_app_a"."id" = "test_app_ab"."a_id") LEFT OUTER JOIN "test_app_c" ON ("test_app_a"."id" = "test_app_c"."a_id") WHERE ("test_app_a"."id" = 1 OR "test_app_ab"."b_id" = 1) GROUP BY "status"
However, Django 2.2.11 processed this query properly with the next query:
SELECT (SELECT U0."status" FROM "test_app_ab" U0 WHERE (U0."a_id" = ("test_app_a"."id") AND U0."b_id" = 1)) AS "status", COUNT((SELECT U0."status" FROM "test_app_ab" U0 WHERE (U0."a_id" = ("test_app_a"."id") AND U0."b_id" = 1))) AS "total_count" FROM "test_app_a" LEFT OUTER JOIN "test_app_ab" ON ("test_app_a"."id" = "test_app_ab"."a_id") LEFT OUTER JOIN "test_app_c" ON ("test_app_a"."id" = "test_app_c"."a_id") WHERE ("test_app_a"."id" = 1 OR "test_app_ab"."b_id" = 1) GROUP BY (SELECT U0."status" FROM "test_app_ab" U0 WHERE (U0."a_id" = ("test_app_a"."id") AND U0."b_id" = 1))
so, the difference in "GROUP BY" clauses
(as DB provider uses "django.db.backends.postgresql", postgresql 11)


## Hints

This is due to a collision of AB.status and the status annotation. The easiest way to solve this issue is to disable group by alias when a collision is detected with involved table columns. This can be easily worked around by avoiding to use an annotation name that conflicts with involved table column names.
@Simon I think we have the ​check for collision in annotation alias and model fields . How can we find the involved tables columns? Thanks
Hasan this is another kind of collision, these fields are not selected and part of join tables so they won't be part of names. We can't change the behavior at the annotate() level as it would be backward incompatible and require extra checks every time an additional table is joined. What needs to be adjust is sql.Query.set_group_by to set alias=None if alias is not None and alias in {... set of all column names of tables in alias_map ...} before calling annotation.get_group_by_cols ​https://github.com/django/django/blob/fc0fa72ff4cdbf5861a366e31cb8bbacd44da22d/django/db/models/sql/query.py#L1943-L1945

## Patch

```diff

diff --git a/django/db/models/sql/query.py b/django/db/models/sql/query.py
--- a/django/db/models/sql/query.py
+++ b/django/db/models/sql/query.py
@@ -1927,6 +1927,19 @@ def set_group_by(self, allow_aliases=True):
         primary key, and the query would be equivalent, the optimization
         will be made automatically.
         """
+        # Column names from JOINs to check collisions with aliases.
+        if allow_aliases:
+            column_names = set()
+            seen_models = set()
+            for join in list(self.alias_map.values())[1:]:  # Skip base table.
+                model = join.join_field.related_model
+                if model not in seen_models:
+                    column_names.update({
+                        field.column
+                        for field in model._meta.local_concrete_fields
+                    })
+                    seen_models.add(model)
+
         group_by = list(self.select)
         if self.annotation_select:
             for alias, annotation in self.annotation_select.items():
@@ -1940,7 +1953,7 @@ def set_group_by(self, allow_aliases=True):
                     warnings.warn(msg, category=RemovedInDjango40Warning)
                     group_by_cols = annotation.get_group_by_cols()
                 else:
-                    if not allow_aliases:
+                    if not allow_aliases or alias in column_names:
                         alias = None
                     group_by_cols = annotation.get_group_by_cols(alias=alias)
                 group_by.extend(group_by_cols)


```

## Test Patch

```diff
diff --git a/tests/aggregation/models.py b/tests/aggregation/models.py
--- a/tests/aggregation/models.py
+++ b/tests/aggregation/models.py
@@ -5,6 +5,7 @@ class Author(models.Model):
     name = models.CharField(max_length=100)
     age = models.IntegerField()
     friends = models.ManyToManyField('self', blank=True)
+    rating = models.FloatField(null=True)
 
     def __str__(self):
         return self.name
diff --git a/tests/aggregation/tests.py b/tests/aggregation/tests.py
--- a/tests/aggregation/tests.py
+++ b/tests/aggregation/tests.py
@@ -1191,6 +1191,22 @@ def test_aggregation_subquery_annotation_values(self):
             },
         ])
 
+    def test_aggregation_subquery_annotation_values_collision(self):
+        books_rating_qs = Book.objects.filter(
+            publisher=OuterRef('pk'),
+            price=Decimal('29.69'),
+        ).values('rating')
+        publisher_qs = Publisher.objects.filter(
+            book__contact__age__gt=20,
+            name=self.p1.name,
+        ).annotate(
+            rating=Subquery(books_rating_qs),
+            contacts_count=Count('book__contact'),
+        ).values('rating').annotate(total_count=Count('rating'))
+        self.assertEqual(list(publisher_qs), [
+            {'rating': 4.0, 'total_count': 2},
+        ])
+
     @skipUnlessDBFeature('supports_subqueries_in_group_by')
     @skipIf(
         connection.vendor == 'mysql' and 'ONLY_FULL_GROUP_BY' in connection.sql_mode,

```

## Test Information

**Tests that should FAIL→PASS**: ["test_aggregation_subquery_annotation_values_collision (aggregation.tests.AggregateTestCase)"]

**Tests that should PASS→PASS**: ["test_add_implementation (aggregation.tests.AggregateTestCase)", "test_aggregate_alias (aggregation.tests.AggregateTestCase)", "test_aggregate_annotation (aggregation.tests.AggregateTestCase)", "test_aggregate_in_order_by (aggregation.tests.AggregateTestCase)", "test_aggregate_multi_join (aggregation.tests.AggregateTestCase)", "test_aggregate_over_complex_annotation (aggregation.tests.AggregateTestCase)", "test_aggregation_exists_annotation (aggregation.tests.AggregateTestCase)", "test_aggregation_expressions (aggregation.tests.AggregateTestCase)", "test_aggregation_order_by_not_selected_annotation_values (aggregation.tests.AggregateTestCase)", "Subquery annotations are excluded from the GROUP BY if they are", "test_aggregation_subquery_annotation_exists (aggregation.tests.AggregateTestCase)", "test_aggregation_subquery_annotation_multivalued (aggregation.tests.AggregateTestCase)", "test_aggregation_subquery_annotation_related_field (aggregation.tests.AggregateTestCase)", "test_aggregation_subquery_annotation_values (aggregation.tests.AggregateTestCase)", "test_annotate_basic (aggregation.tests.AggregateTestCase)", "test_annotate_defer (aggregation.tests.AggregateTestCase)", "test_annotate_defer_select_related (aggregation.tests.AggregateTestCase)", "test_annotate_m2m (aggregation.tests.AggregateTestCase)", "test_annotate_ordering (aggregation.tests.AggregateTestCase)", "test_annotate_over_annotate (aggregation.tests.AggregateTestCase)", "test_annotate_values (aggregation.tests.AggregateTestCase)", "test_annotate_values_aggregate (aggregation.tests.AggregateTestCase)", "test_annotate_values_list (aggregation.tests.AggregateTestCase)", "test_annotated_aggregate_over_annotated_aggregate (aggregation.tests.AggregateTestCase)", "test_annotation (aggregation.tests.AggregateTestCase)", "test_annotation_expressions (aggregation.tests.AggregateTestCase)", "test_arguments_must_be_expressions (aggregation.tests.AggregateTestCase)", "test_avg_decimal_field (aggregation.tests.AggregateTestCase)", "test_avg_duration_field (aggregation.tests.AggregateTestCase)", "test_backwards_m2m_annotate (aggregation.tests.AggregateTestCase)", "test_combine_different_types (aggregation.tests.AggregateTestCase)", "test_complex_aggregations_require_kwarg (aggregation.tests.AggregateTestCase)", "test_complex_values_aggregation (aggregation.tests.AggregateTestCase)", "test_count (aggregation.tests.AggregateTestCase)", "test_count_distinct_expression (aggregation.tests.AggregateTestCase)", "test_count_star (aggregation.tests.AggregateTestCase)", "test_dates_with_aggregation (aggregation.tests.AggregateTestCase)", "test_decimal_max_digits_has_no_effect (aggregation.tests.AggregateTestCase)", "test_distinct_on_aggregate (aggregation.tests.AggregateTestCase)", "test_empty_aggregate (aggregation.tests.AggregateTestCase)", "test_even_more_aggregate (aggregation.tests.AggregateTestCase)", "test_expression_on_aggregation (aggregation.tests.AggregateTestCase)", "test_filter_aggregate (aggregation.tests.AggregateTestCase)", "test_filtering (aggregation.tests.AggregateTestCase)", "test_fkey_aggregate (aggregation.tests.AggregateTestCase)", "test_group_by_exists_annotation (aggregation.tests.AggregateTestCase)", "test_group_by_subquery_annotation (aggregation.tests.AggregateTestCase)", "test_grouped_annotation_in_group_by (aggregation.tests.AggregateTestCase)", "test_missing_output_field_raises_error (aggregation.tests.AggregateTestCase)", "test_more_aggregation (aggregation.tests.AggregateTestCase)", "test_multi_arg_aggregate (aggregation.tests.AggregateTestCase)", "test_multiple_aggregates (aggregation.tests.AggregateTestCase)", "test_non_grouped_annotation_not_in_group_by (aggregation.tests.AggregateTestCase)", "test_nonaggregate_aggregation_throws (aggregation.tests.AggregateTestCase)", "test_nonfield_annotation (aggregation.tests.AggregateTestCase)", "test_order_of_precedence (aggregation.tests.AggregateTestCase)", "test_related_aggregate (aggregation.tests.AggregateTestCase)", "test_reverse_fkey_annotate (aggregation.tests.AggregateTestCase)", "test_single_aggregate (aggregation.tests.AggregateTestCase)", "test_sum_distinct_aggregate (aggregation.tests.AggregateTestCase)", "test_sum_duration_field (aggregation.tests.AggregateTestCase)", "test_ticket11881 (aggregation.tests.AggregateTestCase)", "test_ticket12886 (aggregation.tests.AggregateTestCase)", "test_ticket17424 (aggregation.tests.AggregateTestCase)", "test_values_aggregation (aggregation.tests.AggregateTestCase)", "test_values_annotation_with_expression (aggregation.tests.AggregateTestCase)"]

**Base Commit**: 895f28f9cbed817c00ab68770433170d83132d90
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
