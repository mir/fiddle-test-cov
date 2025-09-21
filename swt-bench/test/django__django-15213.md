# django__django-15213

**Repository**: django/django
**Created**: 2021-12-19T10:48:23Z
**Version**: 4.1

## Problem Statement

ExpressionWrapper for ~Q(pk__in=[]) crashes.
Description
	 
		(last modified by Stefan Brand)
	 
Problem Description
I'm reducing some Q objects (similar to what is described in ticket:32554. Everything is fine for the case where the result is ExpressionWrapper(Q(pk__in=[])). However, when I reduce to ExpressionWrapper(~Q(pk__in=[])) the query breaks.
Symptoms
Working for ExpressionWrapper(Q(pk__in=[]))
print(queryset.annotate(foo=ExpressionWrapper(Q(pk__in=[]), output_field=BooleanField())).values("foo").query)
SELECT 0 AS "foo" FROM "table"
Not working for ExpressionWrapper(~Q(pk__in=[]))
print(queryset.annotate(foo=ExpressionWrapper(~Q(pk__in=[]), output_field=BooleanField())).values("foo").query)
SELECT AS "foo" FROM "table"


## Hints

Good catch! >>> books = Book.objects.annotate(selected=ExpressionWrapper(~Q(pk__in=[]), output_field=BooleanField())).values('selected') >>> list(books) Traceback (most recent call last): File "/django/django/db/backends/utils.py", line 85, in _execute return self.cursor.execute(sql, params) File "/django/django/db/backends/sqlite3/base.py", line 420, in execute return Database.Cursor.execute(self, query, params) sqlite3.OperationalError: near "AS": syntax error

## Patch

```diff

diff --git a/django/db/models/fields/__init__.py b/django/db/models/fields/__init__.py
--- a/django/db/models/fields/__init__.py
+++ b/django/db/models/fields/__init__.py
@@ -994,6 +994,15 @@ def formfield(self, **kwargs):
             defaults = {'form_class': form_class, 'required': False}
         return super().formfield(**{**defaults, **kwargs})
 
+    def select_format(self, compiler, sql, params):
+        sql, params = super().select_format(compiler, sql, params)
+        # Filters that match everything are handled as empty strings in the
+        # WHERE clause, but in SELECT or GROUP BY list they must use a
+        # predicate that's always True.
+        if sql == '':
+            sql = '1'
+        return sql, params
+
 
 class CharField(Field):
     description = _("String (up to %(max_length)s)")


```

## Test Patch

```diff
diff --git a/tests/annotations/tests.py b/tests/annotations/tests.py
--- a/tests/annotations/tests.py
+++ b/tests/annotations/tests.py
@@ -210,6 +210,26 @@ def test_empty_expression_annotation(self):
         self.assertEqual(len(books), Book.objects.count())
         self.assertTrue(all(not book.selected for book in books))
 
+    def test_full_expression_annotation(self):
+        books = Book.objects.annotate(
+            selected=ExpressionWrapper(~Q(pk__in=[]), output_field=BooleanField()),
+        )
+        self.assertEqual(len(books), Book.objects.count())
+        self.assertTrue(all(book.selected for book in books))
+
+    def test_full_expression_annotation_with_aggregation(self):
+        qs = Book.objects.filter(isbn='159059725').annotate(
+            selected=ExpressionWrapper(~Q(pk__in=[]), output_field=BooleanField()),
+            rating_count=Count('rating'),
+        )
+        self.assertEqual([book.rating_count for book in qs], [1])
+
+    def test_aggregate_over_full_expression_annotation(self):
+        qs = Book.objects.annotate(
+            selected=ExpressionWrapper(~Q(pk__in=[]), output_field=BooleanField()),
+        ).aggregate(Sum('selected'))
+        self.assertEqual(qs['selected__sum'], Book.objects.count())
+
     def test_empty_queryset_annotation(self):
         qs = Author.objects.annotate(
             empty=Subquery(Author.objects.values('id').none())

```

## Test Information

**Tests that should FAIL→PASS**: ["test_aggregate_over_full_expression_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_full_expression_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_full_expression_annotation_with_aggregation (annotations.tests.NonAggregateAnnotationTestCase)"]

**Tests that should PASS→PASS**: ["test_aggregate_alias (annotations.tests.AliasTests)", "test_alias_after_annotation (annotations.tests.AliasTests)", "test_alias_annotate_with_aggregation (annotations.tests.AliasTests)", "test_alias_annotation_expression (annotations.tests.AliasTests)", "test_alias_default_alias_expression (annotations.tests.AliasTests)", "test_basic_alias (annotations.tests.AliasTests)", "test_basic_alias_annotation (annotations.tests.AliasTests)", "test_basic_alias_f_annotation (annotations.tests.AliasTests)", "test_basic_alias_f_transform_annotation (annotations.tests.AliasTests)", "test_dates_alias (annotations.tests.AliasTests)", "test_datetimes_alias (annotations.tests.AliasTests)", "test_defer_only_alias (annotations.tests.AliasTests)", "test_filter_alias_agg_with_double_f (annotations.tests.AliasTests)", "test_filter_alias_with_double_f (annotations.tests.AliasTests)", "test_filter_alias_with_f (annotations.tests.AliasTests)", "test_joined_alias_annotation (annotations.tests.AliasTests)", "test_order_by_alias (annotations.tests.AliasTests)", "test_order_by_alias_aggregate (annotations.tests.AliasTests)", "test_overwrite_alias_with_annotation (annotations.tests.AliasTests)", "test_overwrite_annotation_with_alias (annotations.tests.AliasTests)", "test_update_with_alias (annotations.tests.AliasTests)", "test_values_alias (annotations.tests.AliasTests)", "test_aggregate_over_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_annotate_exists (annotations.tests.NonAggregateAnnotationTestCase)", "test_annotate_with_aggregation (annotations.tests.NonAggregateAnnotationTestCase)", "test_annotation_aggregate_with_m2o (annotations.tests.NonAggregateAnnotationTestCase)", "test_annotation_exists_aggregate_values_chaining (annotations.tests.NonAggregateAnnotationTestCase)", "test_annotation_filter_with_subquery (annotations.tests.NonAggregateAnnotationTestCase)", "test_annotation_in_f_grouped_by_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_annotation_reverse_m2m (annotations.tests.NonAggregateAnnotationTestCase)", "test_annotation_subquery_and_aggregate_values_chaining (annotations.tests.NonAggregateAnnotationTestCase)", "test_annotation_subquery_outerref_transform (annotations.tests.NonAggregateAnnotationTestCase)", "test_annotation_with_m2m (annotations.tests.NonAggregateAnnotationTestCase)", "test_arguments_must_be_expressions (annotations.tests.NonAggregateAnnotationTestCase)", "test_basic_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_basic_f_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_boolean_value_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_chaining_annotation_filter_with_m2m (annotations.tests.NonAggregateAnnotationTestCase)", "test_chaining_transforms (annotations.tests.NonAggregateAnnotationTestCase)", "Columns are aligned in the correct order for resolve_columns. This test", "test_column_field_ordering_with_deferred (annotations.tests.NonAggregateAnnotationTestCase)", "test_combined_annotation_commutative (annotations.tests.NonAggregateAnnotationTestCase)", "test_combined_expression_annotation_with_aggregation (annotations.tests.NonAggregateAnnotationTestCase)", "test_combined_f_expression_annotation_with_aggregation (annotations.tests.NonAggregateAnnotationTestCase)", "test_custom_functions (annotations.tests.NonAggregateAnnotationTestCase)", "test_custom_functions_can_ref_other_functions (annotations.tests.NonAggregateAnnotationTestCase)", "test_custom_transform_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_decimal_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "Deferred attributes can be referenced by an annotation,", "test_empty_expression_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_empty_queryset_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_filter_agg_with_double_f (annotations.tests.NonAggregateAnnotationTestCase)", "test_filter_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_filter_annotation_with_double_f (annotations.tests.NonAggregateAnnotationTestCase)", "test_filter_annotation_with_f (annotations.tests.NonAggregateAnnotationTestCase)", "test_filter_decimal_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_filter_wrong_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_grouping_by_q_expression_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_joined_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_joined_transformed_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_mixed_type_annotation_date_interval (annotations.tests.NonAggregateAnnotationTestCase)", "test_mixed_type_annotation_numbers (annotations.tests.NonAggregateAnnotationTestCase)", "Fields on an inherited model can be referenced by an", "Annotating None onto a model round-trips", "test_order_by_aggregate (annotations.tests.NonAggregateAnnotationTestCase)", "test_order_by_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "test_q_expression_annotation_with_aggregation (annotations.tests.NonAggregateAnnotationTestCase)", "test_raw_sql_with_inherited_field (annotations.tests.NonAggregateAnnotationTestCase)", "test_update_with_annotation (annotations.tests.NonAggregateAnnotationTestCase)", "Annotations can reference fields in a values clause,", "test_values_with_pk_annotation (annotations.tests.NonAggregateAnnotationTestCase)"]

**Base Commit**: 03cadb912c78b769d6bf4a943a2a35fc1d952960
**Environment Setup Commit**: 647480166bfe7532e8c471fef0146e3a17e6c0c9
