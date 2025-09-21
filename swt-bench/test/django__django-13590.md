# django__django-13590

**Repository**: django/django
**Created**: 2020-10-23T09:34:55Z
**Version**: 3.2

## Problem Statement

Upgrading 2.2>3.0 causes named tuples used as arguments to __range to error.
Description
	
I noticed this while upgrading a project from 2.2 to 3.0.
This project passes named 2-tuples as arguments to range queryset filters. This works fine on 2.2. On 3.0 it causes the following error: TypeError: __new__() missing 1 required positional argument: 'far'.
This happens because django.db.models.sql.query.Query.resolve_lookup_value goes into the tuple elements to resolve lookups and then attempts to reconstitute the tuple with the resolved elements.
When it attempts to construct the new tuple it preserves the type (the named tuple) but it passes a iterator to it's constructor.
NamedTuples don't have the code path for copying an iterator, and so it errors on insufficient arguments.
The fix is to * expand the contents of the iterator into the constructor.


## Patch

```diff

diff --git a/django/db/models/sql/query.py b/django/db/models/sql/query.py
--- a/django/db/models/sql/query.py
+++ b/django/db/models/sql/query.py
@@ -1077,10 +1077,14 @@ def resolve_lookup_value(self, value, can_reuse, allow_joins):
         elif isinstance(value, (list, tuple)):
             # The items of the iterable may be expressions and therefore need
             # to be resolved independently.
-            return type(value)(
+            values = (
                 self.resolve_lookup_value(sub_value, can_reuse, allow_joins)
                 for sub_value in value
             )
+            type_ = type(value)
+            if hasattr(type_, '_make'):  # namedtuple
+                return type_(*values)
+            return type_(values)
         return value
 
     def solve_lookup_type(self, lookup):


```

## Test Patch

```diff
diff --git a/tests/expressions/tests.py b/tests/expressions/tests.py
--- a/tests/expressions/tests.py
+++ b/tests/expressions/tests.py
@@ -2,6 +2,7 @@
 import pickle
 import unittest
 import uuid
+from collections import namedtuple
 from copy import deepcopy
 from decimal import Decimal
 from unittest import mock
@@ -813,7 +814,7 @@ def setUpTestData(cls):
         Company.objects.create(name='5040 Ltd', num_employees=50, num_chairs=40, ceo=ceo)
         Company.objects.create(name='5050 Ltd', num_employees=50, num_chairs=50, ceo=ceo)
         Company.objects.create(name='5060 Ltd', num_employees=50, num_chairs=60, ceo=ceo)
-        Company.objects.create(name='99300 Ltd', num_employees=99, num_chairs=300, ceo=ceo)
+        cls.c5 = Company.objects.create(name='99300 Ltd', num_employees=99, num_chairs=300, ceo=ceo)
 
     def test_in_lookup_allows_F_expressions_and_expressions_for_integers(self):
         # __in lookups can use F() expressions for integers.
@@ -884,6 +885,13 @@ def test_range_lookup_allows_F_expressions_and_expressions_for_integers(self):
             ordered=False
         )
 
+    def test_range_lookup_namedtuple(self):
+        EmployeeRange = namedtuple('EmployeeRange', ['minimum', 'maximum'])
+        qs = Company.objects.filter(
+            num_employees__range=EmployeeRange(minimum=51, maximum=100),
+        )
+        self.assertSequenceEqual(qs, [self.c5])
+
     @unittest.skipUnless(connection.vendor == 'sqlite',
                          "This defensive test only works on databases that don't validate parameter types")
     def test_complex_expressions_do_not_introduce_sql_injection_via_untrusted_string_inclusion(self):

```

## Test Information

**Tests that should FAIL→PASS**: ["test_range_lookup_namedtuple (expressions.tests.IterableLookupInnerExpressionsTests)"]

**Tests that should PASS→PASS**: ["test_empty_group_by (expressions.tests.ExpressionWrapperTests)", "test_non_empty_group_by (expressions.tests.ExpressionWrapperTests)", "test_deconstruct (expressions.tests.FTests)", "test_deepcopy (expressions.tests.FTests)", "test_equal (expressions.tests.FTests)", "test_hash (expressions.tests.FTests)", "test_not_equal_Value (expressions.tests.FTests)", "test_optimizations (expressions.tests.ExistsTests)", "test_and (expressions.tests.CombinableTests)", "test_negation (expressions.tests.CombinableTests)", "test_or (expressions.tests.CombinableTests)", "test_reversed_and (expressions.tests.CombinableTests)", "test_reversed_or (expressions.tests.CombinableTests)", "test_aggregates (expressions.tests.ReprTests)", "test_distinct_aggregates (expressions.tests.ReprTests)", "test_expressions (expressions.tests.ReprTests)", "test_filtered_aggregates (expressions.tests.ReprTests)", "test_functions (expressions.tests.ReprTests)", "test_resolve_output_field (expressions.tests.CombinedExpressionTests)", "test_month_aggregation (expressions.tests.FieldTransformTests)", "test_multiple_transforms_in_values (expressions.tests.FieldTransformTests)", "test_transform_in_values (expressions.tests.FieldTransformTests)", "test_equal (expressions.tests.SimpleExpressionTests)", "test_hash (expressions.tests.SimpleExpressionTests)", "test_F_reuse (expressions.tests.ExpressionsTests)", "test_insensitive_patterns_escape (expressions.tests.ExpressionsTests)", "test_patterns_escape (expressions.tests.ExpressionsTests)", "test_complex_expressions (expressions.tests.ExpressionsNumericTests)", "test_fill_with_value_from_same_object (expressions.tests.ExpressionsNumericTests)", "test_filter_not_equals_other_field (expressions.tests.ExpressionsNumericTests)", "test_increment_value (expressions.tests.ExpressionsNumericTests)", "test_compile_unresolved (expressions.tests.ValueTests)", "test_deconstruct (expressions.tests.ValueTests)", "test_deconstruct_output_field (expressions.tests.ValueTests)", "test_equal (expressions.tests.ValueTests)", "test_equal_output_field (expressions.tests.ValueTests)", "test_hash (expressions.tests.ValueTests)", "test_raise_empty_expressionlist (expressions.tests.ValueTests)", "test_resolve_output_field (expressions.tests.ValueTests)", "test_resolve_output_field_failure (expressions.tests.ValueTests)", "test_update_TimeField_using_Value (expressions.tests.ValueTests)", "test_update_UUIDField_using_Value (expressions.tests.ValueTests)", "test_complex_expressions_do_not_introduce_sql_injection_via_untrusted_string_inclusion (expressions.tests.IterableLookupInnerExpressionsTests)", "test_expressions_in_lookups_join_choice (expressions.tests.IterableLookupInnerExpressionsTests)", "test_in_lookup_allows_F_expressions_and_expressions_for_datetimes (expressions.tests.IterableLookupInnerExpressionsTests)", "test_in_lookup_allows_F_expressions_and_expressions_for_integers (expressions.tests.IterableLookupInnerExpressionsTests)", "test_range_lookup_allows_F_expressions_and_expressions_for_integers (expressions.tests.IterableLookupInnerExpressionsTests)", "test_lefthand_addition (expressions.tests.ExpressionOperatorTests)", "test_lefthand_bitwise_and (expressions.tests.ExpressionOperatorTests)", "test_lefthand_bitwise_left_shift_operator (expressions.tests.ExpressionOperatorTests)", "test_lefthand_bitwise_or (expressions.tests.ExpressionOperatorTests)", "test_lefthand_bitwise_right_shift_operator (expressions.tests.ExpressionOperatorTests)", "test_lefthand_bitwise_xor (expressions.tests.ExpressionOperatorTests)", "test_lefthand_bitwise_xor_null (expressions.tests.ExpressionOperatorTests)", "test_lefthand_division (expressions.tests.ExpressionOperatorTests)", "test_lefthand_modulo (expressions.tests.ExpressionOperatorTests)", "test_lefthand_multiplication (expressions.tests.ExpressionOperatorTests)", "test_lefthand_power (expressions.tests.ExpressionOperatorTests)", "test_lefthand_subtraction (expressions.tests.ExpressionOperatorTests)", "test_right_hand_addition (expressions.tests.ExpressionOperatorTests)", "test_right_hand_division (expressions.tests.ExpressionOperatorTests)", "test_right_hand_modulo (expressions.tests.ExpressionOperatorTests)", "test_right_hand_multiplication (expressions.tests.ExpressionOperatorTests)", "test_right_hand_subtraction (expressions.tests.ExpressionOperatorTests)", "test_righthand_power (expressions.tests.ExpressionOperatorTests)", "test_date_case_subtraction (expressions.tests.FTimeDeltaTests)", "test_date_comparison (expressions.tests.FTimeDeltaTests)", "test_date_minus_duration (expressions.tests.FTimeDeltaTests)", "test_date_subquery_subtraction (expressions.tests.FTimeDeltaTests)", "test_date_subtraction (expressions.tests.FTimeDeltaTests)", "test_datetime_subquery_subtraction (expressions.tests.FTimeDeltaTests)", "test_datetime_subtraction (expressions.tests.FTimeDeltaTests)", "test_datetime_subtraction_microseconds (expressions.tests.FTimeDeltaTests)", "test_delta_add (expressions.tests.FTimeDeltaTests)", "test_delta_subtract (expressions.tests.FTimeDeltaTests)", "test_delta_update (expressions.tests.FTimeDeltaTests)", "test_duration_expressions (expressions.tests.FTimeDeltaTests)", "test_duration_with_datetime (expressions.tests.FTimeDeltaTests)", "test_duration_with_datetime_microseconds (expressions.tests.FTimeDeltaTests)", "test_durationfield_add (expressions.tests.FTimeDeltaTests)", "test_exclude (expressions.tests.FTimeDeltaTests)", "test_invalid_operator (expressions.tests.FTimeDeltaTests)", "test_mixed_comparisons2 (expressions.tests.FTimeDeltaTests)", "test_multiple_query_compilation (expressions.tests.FTimeDeltaTests)", "test_negative_timedelta_update (expressions.tests.FTimeDeltaTests)", "test_query_clone (expressions.tests.FTimeDeltaTests)", "test_time_subquery_subtraction (expressions.tests.FTimeDeltaTests)", "test_time_subtraction (expressions.tests.FTimeDeltaTests)", "test_aggregate_subquery_annotation (expressions.tests.BasicExpressionsTests)", "test_annotate_values_aggregate (expressions.tests.BasicExpressionsTests)", "test_annotate_values_count (expressions.tests.BasicExpressionsTests)", "test_annotate_values_filter (expressions.tests.BasicExpressionsTests)", "test_annotation_with_nested_outerref (expressions.tests.BasicExpressionsTests)", "test_annotation_with_outerref (expressions.tests.BasicExpressionsTests)", "test_annotations_within_subquery (expressions.tests.BasicExpressionsTests)", "test_arithmetic (expressions.tests.BasicExpressionsTests)", "test_boolean_expression_combined (expressions.tests.BasicExpressionsTests)", "test_case_in_filter_if_boolean_output_field (expressions.tests.BasicExpressionsTests)", "test_exist_single_field_output_field (expressions.tests.BasicExpressionsTests)", "test_exists_in_filter (expressions.tests.BasicExpressionsTests)", "test_explicit_output_field (expressions.tests.BasicExpressionsTests)", "test_filter_inter_attribute (expressions.tests.BasicExpressionsTests)", "test_filter_with_join (expressions.tests.BasicExpressionsTests)", "test_filtering_on_annotate_that_uses_q (expressions.tests.BasicExpressionsTests)", "test_filtering_on_q_that_is_boolean (expressions.tests.BasicExpressionsTests)", "test_filtering_on_rawsql_that_is_boolean (expressions.tests.BasicExpressionsTests)", "test_in_subquery (expressions.tests.BasicExpressionsTests)", "test_incorrect_field_in_F_expression (expressions.tests.BasicExpressionsTests)", "test_incorrect_joined_field_in_F_expression (expressions.tests.BasicExpressionsTests)", "test_nested_outerref_with_function (expressions.tests.BasicExpressionsTests)", "test_nested_subquery (expressions.tests.BasicExpressionsTests)", "test_nested_subquery_join_outer_ref (expressions.tests.BasicExpressionsTests)", "test_nested_subquery_outer_ref_2 (expressions.tests.BasicExpressionsTests)", "test_nested_subquery_outer_ref_with_autofield (expressions.tests.BasicExpressionsTests)", "test_new_object_create (expressions.tests.BasicExpressionsTests)", "test_new_object_save (expressions.tests.BasicExpressionsTests)", "test_object_create_with_aggregate (expressions.tests.BasicExpressionsTests)", "test_object_update (expressions.tests.BasicExpressionsTests)", "test_object_update_fk (expressions.tests.BasicExpressionsTests)", "test_object_update_unsaved_objects (expressions.tests.BasicExpressionsTests)", "test_order_by_exists (expressions.tests.BasicExpressionsTests)", "test_order_by_multiline_sql (expressions.tests.BasicExpressionsTests)", "test_order_of_operations (expressions.tests.BasicExpressionsTests)", "test_outerref (expressions.tests.BasicExpressionsTests)", "test_outerref_mixed_case_table_name (expressions.tests.BasicExpressionsTests)", "test_outerref_with_operator (expressions.tests.BasicExpressionsTests)", "test_parenthesis_priority (expressions.tests.BasicExpressionsTests)", "test_pickle_expression (expressions.tests.BasicExpressionsTests)", "test_subquery (expressions.tests.BasicExpressionsTests)", "test_subquery_eq (expressions.tests.BasicExpressionsTests)", "test_subquery_filter_by_aggregate (expressions.tests.BasicExpressionsTests)", "test_subquery_filter_by_lazy (expressions.tests.BasicExpressionsTests)", "test_subquery_group_by_outerref_in_filter (expressions.tests.BasicExpressionsTests)", "test_subquery_in_filter (expressions.tests.BasicExpressionsTests)", "test_subquery_references_joined_table_twice (expressions.tests.BasicExpressionsTests)", "test_ticket_11722_iexact_lookup (expressions.tests.BasicExpressionsTests)", "test_ticket_16731_startswith_lookup (expressions.tests.BasicExpressionsTests)", "test_ticket_18375_chained_filters (expressions.tests.BasicExpressionsTests)", "test_ticket_18375_join_reuse (expressions.tests.BasicExpressionsTests)", "test_ticket_18375_kwarg_ordering (expressions.tests.BasicExpressionsTests)", "test_ticket_18375_kwarg_ordering_2 (expressions.tests.BasicExpressionsTests)", "test_update (expressions.tests.BasicExpressionsTests)", "test_update_inherited_field_value (expressions.tests.BasicExpressionsTests)", "test_update_with_fk (expressions.tests.BasicExpressionsTests)", "test_update_with_none (expressions.tests.BasicExpressionsTests)", "test_uuid_pk_subquery (expressions.tests.BasicExpressionsTests)"]

**Base Commit**: 755dbf39fcdc491fe9b588358303e259c7750be4
**Environment Setup Commit**: 65dfb06a1ab56c238cc80f5e1c31f61210c4577d
