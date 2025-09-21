# pytest-dev__pytest-7373

**Repository**: pytest-dev/pytest
**Created**: 2020-06-15T17:12:08Z
**Version**: 5.4

## Problem Statement

Incorrect caching of skipif/xfail string condition evaluation
Version: pytest 5.4.3, current master

pytest caches the evaluation of the string in e.g. `@pytest.mark.skipif("sys.platform == 'win32'")`. The caching key is only the string itself (see `cached_eval` in `_pytest/mark/evaluate.py`). However, the evaluation also depends on the item's globals, so the caching can lead to incorrect results. Example:

```py
# test_module_1.py
import pytest

skip = True

@pytest.mark.skipif("skip")
def test_should_skip():
    assert False
```

```py
# test_module_2.py
import pytest

skip = False

@pytest.mark.skipif("skip")
def test_should_not_skip():
    assert False
```

Running `pytest test_module_1.py test_module_2.py`.

Expected: `test_should_skip` is skipped, `test_should_not_skip` is not skipped.

Actual: both are skipped.

---

I think the most appropriate fix is to simply remove the caching, which I don't think is necessary really, and inline `cached_eval` into `MarkEvaluator._istrue`.


## Hints

> I think the most appropriate fix is to simply remove the caching, which I don't think is necessary really, and inline cached_eval into MarkEvaluator._istrue.

I agree:

* While it might have some performance impact with very large test suites which use marks with eval, the simple workaround is to not use the eval feature on those, which is more predictable anyway.
* I don't see a clean way to turn "globals" in some kind of cache key without having some performance impact and/or adverse effects.

So 👍 from me to simply removing this caching. 
As globals are dynamic, i would propose to drop the cache as well, we should investigate reinstating a cache later on 

## Patch

```diff

diff --git a/src/_pytest/mark/evaluate.py b/src/_pytest/mark/evaluate.py
--- a/src/_pytest/mark/evaluate.py
+++ b/src/_pytest/mark/evaluate.py
@@ -10,25 +10,14 @@
 from ..outcomes import fail
 from ..outcomes import TEST_OUTCOME
 from .structures import Mark
-from _pytest.config import Config
 from _pytest.nodes import Item
-from _pytest.store import StoreKey
 
 
-evalcache_key = StoreKey[Dict[str, Any]]()
+def compiled_eval(expr: str, d: Dict[str, object]) -> Any:
+    import _pytest._code
 
-
-def cached_eval(config: Config, expr: str, d: Dict[str, object]) -> Any:
-    default = {}  # type: Dict[str, object]
-    evalcache = config._store.setdefault(evalcache_key, default)
-    try:
-        return evalcache[expr]
-    except KeyError:
-        import _pytest._code
-
-        exprcode = _pytest._code.compile(expr, mode="eval")
-        evalcache[expr] = x = eval(exprcode, d)
-        return x
+    exprcode = _pytest._code.compile(expr, mode="eval")
+    return eval(exprcode, d)
 
 
 class MarkEvaluator:
@@ -98,7 +87,7 @@ def _istrue(self) -> bool:
                     self.expr = expr
                     if isinstance(expr, str):
                         d = self._getglobals()
-                        result = cached_eval(self.item.config, expr, d)
+                        result = compiled_eval(expr, d)
                     else:
                         if "reason" not in mark.kwargs:
                             # XXX better be checked at collection time


```

## Test Patch

```diff
diff --git a/testing/test_mark.py b/testing/test_mark.py
--- a/testing/test_mark.py
+++ b/testing/test_mark.py
@@ -706,6 +706,36 @@ def test_1(parameter):
         reprec = testdir.inline_run()
         reprec.assertoutcome(skipped=1)
 
+    def test_reevaluate_dynamic_expr(self, testdir):
+        """#7360"""
+        py_file1 = testdir.makepyfile(
+            test_reevaluate_dynamic_expr1="""
+            import pytest
+
+            skip = True
+
+            @pytest.mark.skipif("skip")
+            def test_should_skip():
+                assert True
+        """
+        )
+        py_file2 = testdir.makepyfile(
+            test_reevaluate_dynamic_expr2="""
+            import pytest
+
+            skip = False
+
+            @pytest.mark.skipif("skip")
+            def test_should_not_skip():
+                assert True
+        """
+        )
+
+        file_name1 = os.path.basename(py_file1.strpath)
+        file_name2 = os.path.basename(py_file2.strpath)
+        reprec = testdir.inline_run(file_name1, file_name2)
+        reprec.assertoutcome(passed=1, skipped=1)
+
 
 class TestKeywordSelection:
     def test_select_simple(self, testdir):

```

## Test Information

**Tests that should FAIL→PASS**: ["testing/test_mark.py::TestFunctional::test_reevaluate_dynamic_expr"]

**Tests that should PASS→PASS**: ["testing/test_mark.py::TestMark::test_pytest_exists_in_namespace_all[py.test-mark]", "testing/test_mark.py::TestMark::test_pytest_exists_in_namespace_all[py.test-param]", "testing/test_mark.py::TestMark::test_pytest_exists_in_namespace_all[pytest-mark]", "testing/test_mark.py::TestMark::test_pytest_exists_in_namespace_all[pytest-param]", "testing/test_mark.py::TestMark::test_pytest_mark_notcallable", "testing/test_mark.py::TestMark::test_mark_with_param", "testing/test_mark.py::TestMark::test_pytest_mark_name_starts_with_underscore", "testing/test_mark.py::TestMarkDecorator::test__eq__[lhs0-rhs0-True]", "testing/test_mark.py::TestMarkDecorator::test__eq__[lhs1-rhs1-False]", "testing/test_mark.py::TestMarkDecorator::test__eq__[lhs2-bar-False]", "testing/test_mark.py::TestMarkDecorator::test__eq__[foo-rhs3-False]", "testing/test_mark.py::TestMarkDecorator::test_aliases", "testing/test_mark.py::test_addmarker_order", "testing/test_mark.py::test_pytest_param_id_requires_string", "testing/test_mark.py::test_pytest_param_id_allows_none_or_string[None]", "testing/test_mark.py::test_pytest_param_id_allows_none_or_string[hello", "testing/test_mark.py::test_marked_class_run_twice", "testing/test_mark.py::test_ini_markers", "testing/test_mark.py::test_markers_option", "testing/test_mark.py::test_ini_markers_whitespace", "testing/test_mark.py::test_marker_without_description", "testing/test_mark.py::test_markers_option_with_plugin_in_current_dir", "testing/test_mark.py::test_mark_on_pseudo_function", "testing/test_mark.py::test_strict_prohibits_unregistered_markers[--strict-markers]", "testing/test_mark.py::test_strict_prohibits_unregistered_markers[--strict]", "testing/test_mark.py::test_mark_option[xyz-expected_passed0]", "testing/test_mark.py::test_mark_option[(((", "testing/test_mark.py::test_mark_option[not", "testing/test_mark.py::test_mark_option[xyz", "testing/test_mark.py::test_mark_option[xyz2-expected_passed4]", "testing/test_mark.py::test_mark_option_custom[interface-expected_passed0]", "testing/test_mark.py::test_mark_option_custom[not", "testing/test_mark.py::test_keyword_option_custom[interface-expected_passed0]", "testing/test_mark.py::test_keyword_option_custom[not", "testing/test_mark.py::test_keyword_option_custom[pass-expected_passed2]", "testing/test_mark.py::test_keyword_option_custom[1", "testing/test_mark.py::test_keyword_option_considers_mark", "testing/test_mark.py::test_keyword_option_parametrize[None-expected_passed0]", "testing/test_mark.py::test_keyword_option_parametrize[[1.3]-expected_passed1]", "testing/test_mark.py::test_keyword_option_parametrize[2-3-expected_passed2]", "testing/test_mark.py::test_parametrize_with_module", "testing/test_mark.py::test_keyword_option_wrong_arguments[foo", "testing/test_mark.py::test_keyword_option_wrong_arguments[(foo-at", "testing/test_mark.py::test_keyword_option_wrong_arguments[or", "testing/test_mark.py::test_keyword_option_wrong_arguments[not", "testing/test_mark.py::test_parametrized_collected_from_command_line", "testing/test_mark.py::test_parametrized_collect_with_wrong_args", "testing/test_mark.py::test_parametrized_with_kwargs", "testing/test_mark.py::test_parametrize_iterator", "testing/test_mark.py::TestFunctional::test_merging_markers_deep", "testing/test_mark.py::TestFunctional::test_mark_decorator_subclass_does_not_propagate_to_base", "testing/test_mark.py::TestFunctional::test_mark_should_not_pass_to_siebling_class", "testing/test_mark.py::TestFunctional::test_mark_decorator_baseclasses_merged", "testing/test_mark.py::TestFunctional::test_mark_closest", "testing/test_mark.py::TestFunctional::test_mark_with_wrong_marker", "testing/test_mark.py::TestFunctional::test_mark_dynamically_in_funcarg", "testing/test_mark.py::TestFunctional::test_no_marker_match_on_unmarked_names", "testing/test_mark.py::TestFunctional::test_keywords_at_node_level", "testing/test_mark.py::TestFunctional::test_keyword_added_for_session", "testing/test_mark.py::TestFunctional::test_mark_from_parameters", "testing/test_mark.py::TestKeywordSelection::test_select_simple", "testing/test_mark.py::TestKeywordSelection::test_select_extra_keywords[xxx]", "testing/test_mark.py::TestKeywordSelection::test_select_extra_keywords[xxx", "testing/test_mark.py::TestKeywordSelection::test_select_extra_keywords[TestClass]", "testing/test_mark.py::TestKeywordSelection::test_select_extra_keywords[TestClass", "testing/test_mark.py::TestKeywordSelection::test_select_starton", "testing/test_mark.py::TestKeywordSelection::test_keyword_extra", "testing/test_mark.py::TestKeywordSelection::test_no_magic_values[__]", "testing/test_mark.py::TestKeywordSelection::test_no_magic_values[+]", "testing/test_mark.py::TestKeywordSelection::test_no_magic_values[..]", "testing/test_mark.py::TestKeywordSelection::test_no_match_directories_outside_the_suite", "testing/test_mark.py::test_parameterset_for_parametrize_marks[None]", "testing/test_mark.py::test_parameterset_for_parametrize_marks[]", "testing/test_mark.py::test_parameterset_for_parametrize_marks[skip]", "testing/test_mark.py::test_parameterset_for_parametrize_marks[xfail]", "testing/test_mark.py::test_parameterset_for_fail_at_collect", "testing/test_mark.py::test_parameterset_for_parametrize_bad_markname", "testing/test_mark.py::test_mark_expressions_no_smear", "testing/test_mark.py::test_markers_from_parametrize", "testing/test_mark.py::test_marker_expr_eval_failure_handling[NOT", "testing/test_mark.py::test_marker_expr_eval_failure_handling[bogus/]"]

**Base Commit**: 7b77fc086aab8b3a8ebc890200371884555eea1e
**Environment Setup Commit**: 678c1a0745f1cf175c442c719906a1f13e496910
