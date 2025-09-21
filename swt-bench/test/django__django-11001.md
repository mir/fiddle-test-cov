# django__django-11001

**Repository**: django/django
**Created**: 2019-02-17T13:02:09Z
**Version**: 3.0

## Problem Statement

Incorrect removal of order_by clause created as multiline RawSQL
Description
	
Hi.
The SQLCompiler is ripping off one of my "order by" clause, because he "thinks" the clause was already "seen" (in SQLCompiler.get_order_by()). I'm using expressions written as multiline RawSQLs, which are similar but not the same. 
The bug is located in SQLCompiler.get_order_by(), somewhere around line computing part of SQL query without ordering:
without_ordering = self.ordering_parts.search(sql).group(1)
The sql variable contains multiline sql. As a result, the self.ordering_parts regular expression is returning just a line containing ASC or DESC words. This line is added to seen set, and because my raw queries have identical last lines, only the first clasue is returing from SQLCompiler.get_order_by().
As a quick/temporal fix I can suggest making sql variable clean of newline characters, like this:
sql_oneline = ' '.join(sql.split('\n'))
without_ordering = self.ordering_parts.search(sql_oneline).group(1)
Note: beware of unicode (Py2.x u'') and EOL dragons (\r).
Example of my query:
	return MyModel.objects.all().order_by(
		RawSQL('''
			case when status in ('accepted', 'verification')
				 then 2 else 1 end''', []).desc(),
		RawSQL('''
			case when status in ('accepted', 'verification')
				 then (accepted_datetime, preferred_datetime)
				 else null end''', []).asc(),
		RawSQL('''
			case when status not in ('accepted', 'verification')
				 then (accepted_datetime, preferred_datetime, created_at)
				 else null end''', []).desc())
The ordering_parts.search is returing accordingly:
'				 then 2 else 1 end)'
'				 else null end'
'				 else null end'
Second RawSQL with a				 else null end part is removed from query.
The fun thing is that the issue can be solved by workaround by adding a space or any other char to the last line. 
So in case of RawSQL I can just say, that current implementation of avoiding duplicates in order by clause works only for special/rare cases (or does not work in all cases). 
The bug filed here is about wrong identification of duplicates (because it compares only last line of SQL passed to order by clause).
Hope my notes will help you fixing the issue. Sorry for my english.


## Hints

Is there a reason you can't use ​conditional expressions, e.g. something like: MyModel.objects.annotate( custom_order=Case( When(...), ) ).order_by('custom_order') I'm thinking that would avoid fiddly ordering_parts regular expression. If there's some shortcoming to that approach, it might be easier to address that. Allowing the ordering optimization stuff to handle arbitrary RawSQL may be difficult.
Is there a reason you can't use ​conditional expressions No, but I didn't knew about the issue, and writing raw sqls is sometimes faster (not in this case ;) I'm really happy having possibility to mix raw sqls with object queries. Next time I'll use expressions, for sure. Allowing the ordering optimization stuff to handle arbitrary RawSQL may be difficult. Personally I'd like to skip RawSQL clauses in the block which is responsible for finding duplicates. If someone is using raw sqls, he knows the best what he is doing, IMO. And it is quite strange if Django removes silently part of your SQL. This is very confusing. And please note that printing a Query instance was generating incomplete sql, but while checking Query.order_by manually, the return value was containing all clauses. I thought that just printing was affected, but our QA dept told me the truth ;) I know there is no effective way to compare similarity of two raw clauses. This may be hard for expression objects, too, but you have a possibility to implement some __eq__ magic (instead of comparation of generated sqls). Unfortunately I don't know why duplicates detection was implemented, so it's hard to tell how to improve this part.
Patches welcome, I suppose.
​PR
Is there a reason why you didn't add tests?
I was waiting for confirmation, I've added a test. Is it enough?
Some additional test coverage needed.

## Patch

```diff

diff --git a/django/db/models/sql/compiler.py b/django/db/models/sql/compiler.py
--- a/django/db/models/sql/compiler.py
+++ b/django/db/models/sql/compiler.py
@@ -32,7 +32,8 @@ def __init__(self, query, connection, using):
         self.select = None
         self.annotation_col_map = None
         self.klass_info = None
-        self.ordering_parts = re.compile(r'(.*)\s(ASC|DESC)(.*)')
+        # Multiline ordering SQL clause may appear from RawSQL.
+        self.ordering_parts = re.compile(r'^(.*)\s(ASC|DESC)(.*)', re.MULTILINE | re.DOTALL)
         self._meta_ordering = None
 
     def setup_query(self):


```

## Test Patch

```diff
diff --git a/tests/expressions/tests.py b/tests/expressions/tests.py
--- a/tests/expressions/tests.py
+++ b/tests/expressions/tests.py
@@ -384,6 +384,29 @@ def test_order_by_exists(self):
         )
         self.assertSequenceEqual(mustermanns_by_seniority, [self.max, mary])
 
+    def test_order_by_multiline_sql(self):
+        raw_order_by = (
+            RawSQL('''
+                CASE WHEN num_employees > 1000
+                     THEN num_chairs
+                     ELSE 0 END
+            ''', []).desc(),
+            RawSQL('''
+                CASE WHEN num_chairs > 1
+                     THEN 1
+                     ELSE 0 END
+            ''', []).asc()
+        )
+        for qs in (
+            Company.objects.all(),
+            Company.objects.distinct(),
+        ):
+            with self.subTest(qs=qs):
+                self.assertSequenceEqual(
+                    qs.order_by(*raw_order_by),
+                    [self.example_inc, self.gmbh, self.foobar_ltd],
+                )
+
     def test_outerref(self):
         inner = Company.objects.filter(point_of_contact=OuterRef('pk'))
         msg = (

```

## Test Information

**Tests that should FAIL→PASS**: ["test_order_by_multiline_sql (expressions.tests.BasicExpressionsTests)", "test_order_of_operations (expressions.tests.BasicExpressionsTests)"]

**Tests that should PASS→PASS**: ["test_deconstruct (expressions.tests.FTests)", "test_deepcopy (expressions.tests.FTests)", "test_equal (expressions.tests.FTests)", "test_hash (expressions.tests.FTests)", "test_not_equal_Value (expressions.tests.FTests)", "test_and (expressions.tests.CombinableTests)", "test_negation (expressions.tests.CombinableTests)", "test_or (expressions.tests.CombinableTests)", "test_reversed_and (expressions.tests.CombinableTests)", "test_reversed_or (expressions.tests.CombinableTests)", "test_aggregates (expressions.tests.ReprTests)", "test_distinct_aggregates (expressions.tests.ReprTests)", "test_expressions (expressions.tests.ReprTests)", "test_filtered_aggregates (expressions.tests.ReprTests)", "test_functions (expressions.tests.ReprTests)", "test_equal (expressions.tests.SimpleExpressionTests)", "test_hash (expressions.tests.SimpleExpressionTests)", "test_month_aggregation (expressions.tests.FieldTransformTests)", "test_multiple_transforms_in_values (expressions.tests.FieldTransformTests)", "test_transform_in_values (expressions.tests.FieldTransformTests)", "test_deconstruct (expressions.tests.ValueTests)", "test_deconstruct_output_field (expressions.tests.ValueTests)", "test_equal (expressions.tests.ValueTests)", "test_equal_output_field (expressions.tests.ValueTests)", "test_hash (expressions.tests.ValueTests)", "test_raise_empty_expressionlist (expressions.tests.ValueTests)", "test_update_TimeField_using_Value (expressions.tests.ValueTests)", "test_update_UUIDField_using_Value (expressions.tests.ValueTests)", "test_complex_expressions (expressions.tests.ExpressionsNumericTests)", "test_fill_with_value_from_same_object (expressions.tests.ExpressionsNumericTests)", "test_filter_not_equals_other_field (expressions.tests.ExpressionsNumericTests)", "test_increment_value (expressions.tests.ExpressionsNumericTests)", "test_F_reuse (expressions.tests.ExpressionsTests)", "test_insensitive_patterns_escape (expressions.tests.ExpressionsTests)", "test_patterns_escape (expressions.tests.ExpressionsTests)", "test_complex_expressions_do_not_introduce_sql_injection_via_untrusted_string_inclusion (expressions.tests.IterableLookupInnerExpressionsTests)", "test_expressions_in_lookups_join_choice (expressions.tests.IterableLookupInnerExpressionsTests)", "test_in_lookup_allows_F_expressions_and_expressions_for_datetimes (expressions.tests.IterableLookupInnerExpressionsTests)", "test_in_lookup_allows_F_expressions_and_expressions_for_integers (expressions.tests.IterableLookupInnerExpressionsTests)", "test_range_lookup_allows_F_expressions_and_expressions_for_integers (expressions.tests.IterableLookupInnerExpressionsTests)", "test_lefthand_addition (expressions.tests.ExpressionOperatorTests)", "test_lefthand_bitwise_and (expressions.tests.ExpressionOperatorTests)", "test_lefthand_bitwise_left_shift_operator (expressions.tests.ExpressionOperatorTests)", "test_lefthand_bitwise_or (expressions.tests.ExpressionOperatorTests)", "test_lefthand_bitwise_right_shift_operator (expressions.tests.ExpressionOperatorTests)", "test_lefthand_division (expressions.tests.ExpressionOperatorTests)", "test_lefthand_modulo (expressions.tests.ExpressionOperatorTests)", "test_lefthand_multiplication (expressions.tests.ExpressionOperatorTests)", "test_lefthand_power (expressions.tests.ExpressionOperatorTests)", "test_lefthand_subtraction (expressions.tests.ExpressionOperatorTests)", "test_right_hand_addition (expressions.tests.ExpressionOperatorTests)", "test_right_hand_division (expressions.tests.ExpressionOperatorTests)", "test_right_hand_modulo (expressions.tests.ExpressionOperatorTests)", "test_right_hand_multiplication (expressions.tests.ExpressionOperatorTests)", "test_right_hand_subtraction (expressions.tests.ExpressionOperatorTests)", "test_righthand_power (expressions.tests.ExpressionOperatorTests)", "test_aggregate_subquery_annotation (expressions.tests.BasicExpressionsTests)", "test_annotate_values_aggregate (expressions.tests.BasicExpressionsTests)", "test_annotate_values_count (expressions.tests.BasicExpressionsTests)", "test_annotate_values_filter (expressions.tests.BasicExpressionsTests)", "test_annotation_with_outerref (expressions.tests.BasicExpressionsTests)", "test_annotations_within_subquery (expressions.tests.BasicExpressionsTests)", "test_arithmetic (expressions.tests.BasicExpressionsTests)", "test_exist_single_field_output_field (expressions.tests.BasicExpressionsTests)", "test_explicit_output_field (expressions.tests.BasicExpressionsTests)", "test_filter_inter_attribute (expressions.tests.BasicExpressionsTests)", "test_filter_with_join (expressions.tests.BasicExpressionsTests)", "test_filtering_on_annotate_that_uses_q (expressions.tests.BasicExpressionsTests)", "test_in_subquery (expressions.tests.BasicExpressionsTests)", "test_incorrect_field_in_F_expression (expressions.tests.BasicExpressionsTests)", "test_incorrect_joined_field_in_F_expression (expressions.tests.BasicExpressionsTests)", "test_nested_subquery (expressions.tests.BasicExpressionsTests)", "test_nested_subquery_outer_ref_2 (expressions.tests.BasicExpressionsTests)", "test_nested_subquery_outer_ref_with_autofield (expressions.tests.BasicExpressionsTests)", "test_new_object_create (expressions.tests.BasicExpressionsTests)", "test_new_object_save (expressions.tests.BasicExpressionsTests)", "test_object_create_with_aggregate (expressions.tests.BasicExpressionsTests)", "test_object_update (expressions.tests.BasicExpressionsTests)", "test_object_update_fk (expressions.tests.BasicExpressionsTests)", "test_object_update_unsaved_objects (expressions.tests.BasicExpressionsTests)", "test_order_by_exists (expressions.tests.BasicExpressionsTests)", "test_outerref (expressions.tests.BasicExpressionsTests)", "test_outerref_mixed_case_table_name (expressions.tests.BasicExpressionsTests)", "test_outerref_with_operator (expressions.tests.BasicExpressionsTests)", "test_parenthesis_priority (expressions.tests.BasicExpressionsTests)", "test_pickle_expression (expressions.tests.BasicExpressionsTests)", "test_subquery (expressions.tests.BasicExpressionsTests)", "test_subquery_filter_by_aggregate (expressions.tests.BasicExpressionsTests)", "test_subquery_references_joined_table_twice (expressions.tests.BasicExpressionsTests)", "test_ticket_11722_iexact_lookup (expressions.tests.BasicExpressionsTests)", "test_ticket_16731_startswith_lookup (expressions.tests.BasicExpressionsTests)", "test_ticket_18375_chained_filters (expressions.tests.BasicExpressionsTests)", "test_ticket_18375_join_reuse (expressions.tests.BasicExpressionsTests)", "test_ticket_18375_kwarg_ordering (expressions.tests.BasicExpressionsTests)", "test_ticket_18375_kwarg_ordering_2 (expressions.tests.BasicExpressionsTests)", "test_update (expressions.tests.BasicExpressionsTests)", "test_update_inherited_field_value (expressions.tests.BasicExpressionsTests)", "test_update_with_fk (expressions.tests.BasicExpressionsTests)", "test_update_with_none (expressions.tests.BasicExpressionsTests)", "test_uuid_pk_subquery (expressions.tests.BasicExpressionsTests)", "test_date_comparison (expressions.tests.FTimeDeltaTests)", "test_date_minus_duration (expressions.tests.FTimeDeltaTests)", "test_date_subtraction (expressions.tests.FTimeDeltaTests)", "test_datetime_subtraction (expressions.tests.FTimeDeltaTests)", "test_datetime_subtraction_microseconds (expressions.tests.FTimeDeltaTests)", "test_delta_add (expressions.tests.FTimeDeltaTests)", "test_delta_subtract (expressions.tests.FTimeDeltaTests)", "test_delta_update (expressions.tests.FTimeDeltaTests)", "test_duration_with_datetime (expressions.tests.FTimeDeltaTests)", "test_duration_with_datetime_microseconds (expressions.tests.FTimeDeltaTests)", "test_durationfield_add (expressions.tests.FTimeDeltaTests)", "test_exclude (expressions.tests.FTimeDeltaTests)", "test_invalid_operator (expressions.tests.FTimeDeltaTests)", "test_mixed_comparisons2 (expressions.tests.FTimeDeltaTests)", "test_multiple_query_compilation (expressions.tests.FTimeDeltaTests)", "test_negative_timedelta_update (expressions.tests.FTimeDeltaTests)", "test_query_clone (expressions.tests.FTimeDeltaTests)", "test_time_subtraction (expressions.tests.FTimeDeltaTests)"]

**Base Commit**: ef082ebb84f00e38af4e8880d04e8365c2766d34
**Environment Setup Commit**: 419a78300f7cd27611196e1e464d50fd0385ff27
