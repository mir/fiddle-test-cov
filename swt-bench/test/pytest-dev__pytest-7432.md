# pytest-dev__pytest-7432

**Repository**: pytest-dev/pytest
**Created**: 2020-06-29T21:51:15Z
**Version**: 5.4

## Problem Statement

skipping: --runxfail breaks pytest.mark.skip location reporting
pytest versions: 5.4.x, current master

When `@pytest.mark.skip`/`skipif` marks are used to skip a test, for example

```py
import pytest
@pytest.mark.skip
def test_skip_location() -> None:
    assert 0
```

the expected skip location reported should point to the item itself, and this is indeed what happens when running with `pytest -rs`:

```
SKIPPED [1] test_it.py:3: unconditional skip
```

However, adding `pytest -rs --runxfail` breaks this:

```
SKIPPED [1] src/_pytest/skipping.py:238: unconditional skip
```

The `--runxfail` is only about xfail and should not affect this at all.

---

Hint: the bug is in `src/_pytest/skipping.py`, the `pytest_runtest_makereport` hook.


## Hints

Can I look into this one?
@debugduck Sure!
Awesome! I'll get started on it and open up a PR when I find it. I'm a bit new, so I'm still learning about the code base.

## Patch

```diff

diff --git a/src/_pytest/skipping.py b/src/_pytest/skipping.py
--- a/src/_pytest/skipping.py
+++ b/src/_pytest/skipping.py
@@ -291,7 +291,8 @@ def pytest_runtest_makereport(item: Item, call: CallInfo[None]):
             else:
                 rep.outcome = "passed"
                 rep.wasxfail = xfailed.reason
-    elif (
+
+    if (
         item._store.get(skipped_by_mark_key, True)
         and rep.skipped
         and type(rep.longrepr) is tuple


```

## Test Patch

```diff
diff --git a/testing/test_skipping.py b/testing/test_skipping.py
--- a/testing/test_skipping.py
+++ b/testing/test_skipping.py
@@ -235,6 +235,31 @@ def test_func2():
             ["*def test_func():*", "*assert 0*", "*1 failed*1 pass*"]
         )
 
+    @pytest.mark.parametrize(
+        "test_input,expected",
+        [
+            (
+                ["-rs"],
+                ["SKIPPED [1] test_sample.py:2: unconditional skip", "*1 skipped*"],
+            ),
+            (
+                ["-rs", "--runxfail"],
+                ["SKIPPED [1] test_sample.py:2: unconditional skip", "*1 skipped*"],
+            ),
+        ],
+    )
+    def test_xfail_run_with_skip_mark(self, testdir, test_input, expected):
+        testdir.makepyfile(
+            test_sample="""
+            import pytest
+            @pytest.mark.skip
+            def test_skip_location() -> None:
+                assert 0
+        """
+        )
+        result = testdir.runpytest(*test_input)
+        result.stdout.fnmatch_lines(expected)
+
     def test_xfail_evalfalse_but_fails(self, testdir):
         item = testdir.getitem(
             """

```

## Test Information

**Tests that should FAIL→PASS**: ["testing/test_skipping.py::TestXFail::test_xfail_run_with_skip_mark[test_input1-expected1]"]

**Tests that should PASS→PASS**: ["testing/test_skipping.py::test_importorskip", "testing/test_skipping.py::TestEvaluation::test_no_marker", "testing/test_skipping.py::TestEvaluation::test_marked_xfail_no_args", "testing/test_skipping.py::TestEvaluation::test_marked_skipif_no_args", "testing/test_skipping.py::TestEvaluation::test_marked_one_arg", "testing/test_skipping.py::TestEvaluation::test_marked_one_arg_with_reason", "testing/test_skipping.py::TestEvaluation::test_marked_one_arg_twice", "testing/test_skipping.py::TestEvaluation::test_marked_one_arg_twice2", "testing/test_skipping.py::TestEvaluation::test_marked_skipif_with_boolean_without_reason", "testing/test_skipping.py::TestEvaluation::test_marked_skipif_with_invalid_boolean", "testing/test_skipping.py::TestEvaluation::test_skipif_class", "testing/test_skipping.py::TestXFail::test_xfail_simple[True]", "testing/test_skipping.py::TestXFail::test_xfail_simple[False]", "testing/test_skipping.py::TestXFail::test_xfail_xpassed", "testing/test_skipping.py::TestXFail::test_xfail_using_platform", "testing/test_skipping.py::TestXFail::test_xfail_xpassed_strict", "testing/test_skipping.py::TestXFail::test_xfail_run_anyway", "testing/test_skipping.py::TestXFail::test_xfail_run_with_skip_mark[test_input0-expected0]", "testing/test_skipping.py::TestXFail::test_xfail_evalfalse_but_fails", "testing/test_skipping.py::TestXFail::test_xfail_not_report_default", "testing/test_skipping.py::TestXFail::test_xfail_not_run_xfail_reporting", "testing/test_skipping.py::TestXFail::test_xfail_not_run_no_setup_run", "testing/test_skipping.py::TestXFail::test_xfail_xpass", "testing/test_skipping.py::TestXFail::test_xfail_imperative", "testing/test_skipping.py::TestXFail::test_xfail_imperative_in_setup_function", "testing/test_skipping.py::TestXFail::test_dynamic_xfail_no_run", "testing/test_skipping.py::TestXFail::test_dynamic_xfail_set_during_funcarg_setup", "testing/test_skipping.py::TestXFail::test_xfail_raises[TypeError-TypeError-*1", "testing/test_skipping.py::TestXFail::test_xfail_raises[(AttributeError,", "testing/test_skipping.py::TestXFail::test_xfail_raises[TypeError-IndexError-*1", "testing/test_skipping.py::TestXFail::test_strict_sanity", "testing/test_skipping.py::TestXFail::test_strict_xfail[True]", "testing/test_skipping.py::TestXFail::test_strict_xfail[False]", "testing/test_skipping.py::TestXFail::test_strict_xfail_condition[True]", "testing/test_skipping.py::TestXFail::test_strict_xfail_condition[False]", "testing/test_skipping.py::TestXFail::test_xfail_condition_keyword[True]", "testing/test_skipping.py::TestXFail::test_xfail_condition_keyword[False]", "testing/test_skipping.py::TestXFail::test_strict_xfail_default_from_file[true]", "testing/test_skipping.py::TestXFail::test_strict_xfail_default_from_file[false]", "testing/test_skipping.py::TestXFailwithSetupTeardown::test_failing_setup_issue9", "testing/test_skipping.py::TestXFailwithSetupTeardown::test_failing_teardown_issue9", "testing/test_skipping.py::TestSkip::test_skip_class", "testing/test_skipping.py::TestSkip::test_skips_on_false_string", "testing/test_skipping.py::TestSkip::test_arg_as_reason", "testing/test_skipping.py::TestSkip::test_skip_no_reason", "testing/test_skipping.py::TestSkip::test_skip_with_reason", "testing/test_skipping.py::TestSkip::test_only_skips_marked_test", "testing/test_skipping.py::TestSkip::test_strict_and_skip", "testing/test_skipping.py::TestSkipif::test_skipif_conditional", "testing/test_skipping.py::TestSkipif::test_skipif_reporting[\"hasattr(sys,", "testing/test_skipping.py::TestSkipif::test_skipif_reporting[True,", "testing/test_skipping.py::TestSkipif::test_skipif_using_platform", "testing/test_skipping.py::TestSkipif::test_skipif_reporting_multiple[skipif-SKIP-skipped]", "testing/test_skipping.py::TestSkipif::test_skipif_reporting_multiple[xfail-XPASS-xpassed]", "testing/test_skipping.py::test_skip_not_report_default", "testing/test_skipping.py::test_skipif_class", "testing/test_skipping.py::test_skipped_reasons_functional", "testing/test_skipping.py::test_skipped_folding", "testing/test_skipping.py::test_reportchars", "testing/test_skipping.py::test_reportchars_error", "testing/test_skipping.py::test_reportchars_all", "testing/test_skipping.py::test_reportchars_all_error", "testing/test_skipping.py::test_errors_in_xfail_skip_expressions", "testing/test_skipping.py::test_xfail_skipif_with_globals", "testing/test_skipping.py::test_default_markers", "testing/test_skipping.py::test_xfail_test_setup_exception", "testing/test_skipping.py::test_imperativeskip_on_xfail_test", "testing/test_skipping.py::TestBooleanCondition::test_skipif", "testing/test_skipping.py::TestBooleanCondition::test_skipif_noreason", "testing/test_skipping.py::TestBooleanCondition::test_xfail", "testing/test_skipping.py::test_xfail_item", "testing/test_skipping.py::test_module_level_skip_error", "testing/test_skipping.py::test_module_level_skip_with_allow_module_level", "testing/test_skipping.py::test_invalid_skip_keyword_parameter", "testing/test_skipping.py::test_mark_xfail_item", "testing/test_skipping.py::test_summary_list_after_errors", "testing/test_skipping.py::test_relpath_rootdir"]

**Base Commit**: e6e300e729dd33956e5448d8be9a0b1540b4e53a
**Environment Setup Commit**: 678c1a0745f1cf175c442c719906a1f13e496910
