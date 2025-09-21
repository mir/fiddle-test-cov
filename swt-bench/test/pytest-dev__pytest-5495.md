# pytest-dev__pytest-5495

**Repository**: pytest-dev/pytest
**Created**: 2019-06-25T23:41:16Z
**Version**: 4.6

## Problem Statement

Confusing assertion rewriting message with byte strings
The comparison with assertion rewriting for byte strings is confusing: 
```
    def test_b():
>       assert b"" == b"42"
E       AssertionError: assert b'' == b'42'
E         Right contains more items, first extra item: 52
E         Full diff:
E         - b''
E         + b'42'
E         ?   ++
```

52 is the ASCII ordinal of "4" here.

It became clear to me when using another example:

```
    def test_b():
>       assert b"" == b"1"
E       AssertionError: assert b'' == b'1'
E         Right contains more items, first extra item: 49
E         Full diff:
E         - b''
E         + b'1'
E         ?   +
```

Not sure what should/could be done here.


## Hints

hmmm yes, this ~kinda makes sense as `bytes` objects are sequences of integers -- we should maybe just omit the "contains more items" messaging for bytes objects?

## Patch

```diff

diff --git a/src/_pytest/assertion/util.py b/src/_pytest/assertion/util.py
--- a/src/_pytest/assertion/util.py
+++ b/src/_pytest/assertion/util.py
@@ -254,17 +254,38 @@ def _compare_eq_iterable(left, right, verbose=0):
 
 
 def _compare_eq_sequence(left, right, verbose=0):
+    comparing_bytes = isinstance(left, bytes) and isinstance(right, bytes)
     explanation = []
     len_left = len(left)
     len_right = len(right)
     for i in range(min(len_left, len_right)):
         if left[i] != right[i]:
+            if comparing_bytes:
+                # when comparing bytes, we want to see their ascii representation
+                # instead of their numeric values (#5260)
+                # using a slice gives us the ascii representation:
+                # >>> s = b'foo'
+                # >>> s[0]
+                # 102
+                # >>> s[0:1]
+                # b'f'
+                left_value = left[i : i + 1]
+                right_value = right[i : i + 1]
+            else:
+                left_value = left[i]
+                right_value = right[i]
+
             explanation += [
-                "At index {} diff: {!r} != {!r}".format(i, left[i], right[i])
+                "At index {} diff: {!r} != {!r}".format(i, left_value, right_value)
             ]
             break
-    len_diff = len_left - len_right
 
+    if comparing_bytes:
+        # when comparing bytes, it doesn't help to show the "sides contain one or more items"
+        # longer explanation, so skip it
+        return explanation
+
+    len_diff = len_left - len_right
     if len_diff:
         if len_diff > 0:
             dir_with_more = "Left"


```

## Test Patch

```diff
diff --git a/testing/test_assertion.py b/testing/test_assertion.py
--- a/testing/test_assertion.py
+++ b/testing/test_assertion.py
@@ -331,6 +331,27 @@ def test_multiline_text_diff(self):
         assert "- spam" in diff
         assert "+ eggs" in diff
 
+    def test_bytes_diff_normal(self):
+        """Check special handling for bytes diff (#5260)"""
+        diff = callequal(b"spam", b"eggs")
+
+        assert diff == [
+            "b'spam' == b'eggs'",
+            "At index 0 diff: b's' != b'e'",
+            "Use -v to get the full diff",
+        ]
+
+    def test_bytes_diff_verbose(self):
+        """Check special handling for bytes diff (#5260)"""
+        diff = callequal(b"spam", b"eggs", verbose=True)
+        assert diff == [
+            "b'spam' == b'eggs'",
+            "At index 0 diff: b's' != b'e'",
+            "Full diff:",
+            "- b'spam'",
+            "+ b'eggs'",
+        ]
+
     def test_list(self):
         expl = callequal([0, 1], [0, 2])
         assert len(expl) > 1

```

## Test Information

**Tests that should FAIL→PASS**: ["testing/test_assertion.py::TestAssert_reprcompare::test_bytes_diff_normal", "testing/test_assertion.py::TestAssert_reprcompare::test_bytes_diff_verbose"]

**Tests that should PASS→PASS**: ["testing/test_assertion.py::TestImportHookInstallation::test_register_assert_rewrite_checks_types", "testing/test_assertion.py::TestAssert_reprcompare::test_different_types", "testing/test_assertion.py::TestAssert_reprcompare::test_summary", "testing/test_assertion.py::TestAssert_reprcompare::test_text_diff", "testing/test_assertion.py::TestAssert_reprcompare::test_text_skipping", "testing/test_assertion.py::TestAssert_reprcompare::test_text_skipping_verbose", "testing/test_assertion.py::TestAssert_reprcompare::test_multiline_text_diff", "testing/test_assertion.py::TestAssert_reprcompare::test_list", "testing/test_assertion.py::TestAssert_reprcompare::test_iterable_full_diff[left0-right0-\\n", "testing/test_assertion.py::TestAssert_reprcompare::test_iterable_full_diff[left1-right1-\\n", "testing/test_assertion.py::TestAssert_reprcompare::test_iterable_full_diff[left2-right2-\\n", "testing/test_assertion.py::TestAssert_reprcompare::test_list_different_lengths", "testing/test_assertion.py::TestAssert_reprcompare::test_dict", "testing/test_assertion.py::TestAssert_reprcompare::test_dict_omitting", "testing/test_assertion.py::TestAssert_reprcompare::test_dict_omitting_with_verbosity_1", "testing/test_assertion.py::TestAssert_reprcompare::test_dict_omitting_with_verbosity_2", "testing/test_assertion.py::TestAssert_reprcompare::test_dict_different_items", "testing/test_assertion.py::TestAssert_reprcompare::test_sequence_different_items", "testing/test_assertion.py::TestAssert_reprcompare::test_set", "testing/test_assertion.py::TestAssert_reprcompare::test_frozenzet", "testing/test_assertion.py::TestAssert_reprcompare::test_Sequence", "testing/test_assertion.py::TestAssert_reprcompare::test_list_tuples", "testing/test_assertion.py::TestAssert_reprcompare::test_repr_verbose", "testing/test_assertion.py::TestAssert_reprcompare::test_list_bad_repr", "testing/test_assertion.py::TestAssert_reprcompare::test_one_repr_empty", "testing/test_assertion.py::TestAssert_reprcompare::test_repr_no_exc", "testing/test_assertion.py::TestAssert_reprcompare::test_unicode", "testing/test_assertion.py::TestAssert_reprcompare::test_nonascii_text", "testing/test_assertion.py::TestAssert_reprcompare::test_format_nonascii_explanation", "testing/test_assertion.py::TestAssert_reprcompare::test_mojibake", "testing/test_assertion.py::TestAssert_reprcompare_attrsclass::test_comparing_two_different_attrs_classes", "testing/test_assertion.py::TestFormatExplanation::test_fmt_simple", "testing/test_assertion.py::TestFormatExplanation::test_fmt_where", "testing/test_assertion.py::TestFormatExplanation::test_fmt_and", "testing/test_assertion.py::TestFormatExplanation::test_fmt_where_nested", "testing/test_assertion.py::TestFormatExplanation::test_fmt_newline", "testing/test_assertion.py::TestFormatExplanation::test_fmt_newline_escaped", "testing/test_assertion.py::TestFormatExplanation::test_fmt_newline_before_where", "testing/test_assertion.py::TestFormatExplanation::test_fmt_multi_newline_before_where", "testing/test_assertion.py::TestTruncateExplanation::test_doesnt_truncate_when_input_is_empty_list", "testing/test_assertion.py::TestTruncateExplanation::test_doesnt_truncate_at_when_input_is_5_lines_and_LT_max_chars", "testing/test_assertion.py::TestTruncateExplanation::test_truncates_at_8_lines_when_given_list_of_empty_strings", "testing/test_assertion.py::TestTruncateExplanation::test_truncates_at_8_lines_when_first_8_lines_are_LT_max_chars", "testing/test_assertion.py::TestTruncateExplanation::test_truncates_at_8_lines_when_first_8_lines_are_EQ_max_chars", "testing/test_assertion.py::TestTruncateExplanation::test_truncates_at_4_lines_when_first_4_lines_are_GT_max_chars", "testing/test_assertion.py::TestTruncateExplanation::test_truncates_at_1_line_when_first_line_is_GT_max_chars", "testing/test_assertion.py::test_reprcompare_notin", "testing/test_assertion.py::test_reprcompare_whitespaces", "testing/test_assertion.py::test_exit_from_assertrepr_compare", "testing/test_assertion.py::TestImportHookInstallation::test_conftest_assertion_rewrite[plain-True]", "testing/test_assertion.py::TestImportHookInstallation::test_conftest_assertion_rewrite[plain-False]", "testing/test_assertion.py::TestImportHookInstallation::test_conftest_assertion_rewrite[rewrite-True]", "testing/test_assertion.py::TestImportHookInstallation::test_conftest_assertion_rewrite[rewrite-False]", "testing/test_assertion.py::TestImportHookInstallation::test_rewrite_assertions_pytester_plugin", "testing/test_assertion.py::TestImportHookInstallation::test_pytest_plugins_rewrite[plain]", "testing/test_assertion.py::TestImportHookInstallation::test_pytest_plugins_rewrite[rewrite]", "testing/test_assertion.py::TestImportHookInstallation::test_pytest_plugins_rewrite_module_names[str]", "testing/test_assertion.py::TestImportHookInstallation::test_pytest_plugins_rewrite_module_names[list]", "testing/test_assertion.py::TestImportHookInstallation::test_pytest_plugins_rewrite_module_names_correctly", "testing/test_assertion.py::TestImportHookInstallation::test_rewrite_ast", "testing/test_assertion.py::TestBinReprIntegration::test_pytest_assertrepr_compare_called", "testing/test_assertion.py::TestAssert_reprcompare_dataclass::test_dataclasses", "testing/test_assertion.py::TestAssert_reprcompare_dataclass::test_dataclasses_verbose", "testing/test_assertion.py::TestAssert_reprcompare_dataclass::test_dataclasses_with_attribute_comparison_off", "testing/test_assertion.py::TestAssert_reprcompare_dataclass::test_comparing_two_different_data_classes", "testing/test_assertion.py::TestFormatExplanation::test_special_chars_full", "testing/test_assertion.py::TestTruncateExplanation::test_full_output_truncated", "testing/test_assertion.py::test_python25_compile_issue257", "testing/test_assertion.py::test_rewritten", "testing/test_assertion.py::test_pytest_assertrepr_compare_integration", "testing/test_assertion.py::test_sequence_comparison_uses_repr", "testing/test_assertion.py::test_assertrepr_loaded_per_dir", "testing/test_assertion.py::test_assertion_options", "testing/test_assertion.py::test_triple_quoted_string_issue113", "testing/test_assertion.py::test_traceback_failure", "testing/test_assertion.py::test_exception_handling_no_traceback", "testing/test_assertion.py::test_warn_missing", "testing/test_assertion.py::test_recursion_source_decode", "testing/test_assertion.py::test_AssertionError_message", "testing/test_assertion.py::test_diff_newline_at_end", "testing/test_assertion.py::test_assert_tuple_warning", "testing/test_assertion.py::test_assert_indirect_tuple_no_warning", "testing/test_assertion.py::test_assert_with_unicode", "testing/test_assertion.py::test_raise_unprintable_assertion_error", "testing/test_assertion.py::test_raise_assertion_error_raisin_repr", "testing/test_assertion.py::test_issue_1944"]

**Base Commit**: 1aefb24b37c30fba8fd79a744829ca16e252f340
**Environment Setup Commit**: d5843f89d3c008ddcb431adbc335b080a79e617e
