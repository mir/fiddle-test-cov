# pytest-dev__pytest-8906

**Repository**: pytest-dev/pytest
**Created**: 2021-07-14T08:00:50Z
**Version**: 7.0

## Problem Statement

Improve handling of skip for module level
This is potentially about updating docs, updating error messages or introducing a new API.

Consider the following scenario:

`pos_only.py` is using Python 3,8 syntax:
```python
def foo(a, /, b):
    return a + b
```

It should not be tested under Python 3.6 and 3.7.
This is a proper way to skip the test in Python older than 3.8:
```python
from pytest import raises, skip
import sys
if sys.version_info < (3, 8):
    skip(msg="Requires Python >= 3.8", allow_module_level=True)

# import must be after the module level skip:
from pos_only import *

def test_foo():
    assert foo(10, 20) == 30
    assert foo(10, b=20) == 30
    with raises(TypeError):
        assert foo(a=10, b=20)
```

My actual test involves parameterize and a 3.8 only class, so skipping the test itself is not sufficient because the 3.8 class was used in the parameterization.

A naive user will try to initially skip the module like:

```python
if sys.version_info < (3, 8):
    skip(msg="Requires Python >= 3.8")
```
This issues this error:

>Using pytest.skip outside of a test is not allowed. To decorate a test function, use the @pytest.mark.skip or @pytest.mark.skipif decorators instead, and to skip a module use `pytestmark = pytest.mark.{skip,skipif}.

The proposed solution `pytestmark = pytest.mark.{skip,skipif}`, does not work  in my case: pytest continues to process the file and fail when it hits the 3.8 syntax (when running with an older version of Python).

The correct solution, to use skip as a function is actively discouraged by the error message.

This area feels a bit unpolished.
A few ideas to improve:

1. Explain skip with  `allow_module_level` in the error message. this seems in conflict with the spirit of the message.
2. Create an alternative API to skip a module to make things easier: `skip_module("reason")`, which can call `_skip(msg=msg, allow_module_level=True)`.




## Hints

SyntaxErrors are thrown before execution, so how would the skip call stop the interpreter from parsing the 'incorrect' syntax?
unless we hook the interpreter that is.
A solution could be to ignore syntax errors based on some parameter
if needed we can extend this to have some functionality to evaluate conditions in which syntax errors should be ignored
please note what i suggest will not fix other compatibility issues, just syntax errors

> SyntaxErrors are thrown before execution, so how would the skip call stop the interpreter from parsing the 'incorrect' syntax?

The Python 3.8 code is included by an import. the idea is that the import should not happen if we are skipping the module.
```python
if sys.version_info < (3, 8):
    skip(msg="Requires Python >= 3.8", allow_module_level=True)

# import must be after the module level skip:
from pos_only import *
```
Hi @omry,

Thanks for raising this.

Definitely we should improve that message. 

> Explain skip with allow_module_level in the error message. this seems in conflict with the spirit of the message.

I'm 👍 on this. 2 is also good, but because `allow_module_level` already exists and is part of the public API, I don't think introducing a new API will really help, better to improve the docs of what we already have.

Perhaps improve the message to something like this:

```
Using pytest.skip outside of a test will skip the entire module, if that's your intention pass `allow_module_level=True`. 
If you want to skip a specific test or entire class, use the @pytest.mark.skip or @pytest.mark.skipif decorators.
```

I think we can drop the `pytestmark` remark from there, it is not skip-specific and passing `allow_module_level` already accomplishes the same.

Thanks @nicoddemus.

> Using pytest.skip outside of a test will skip the entire module, if that's your intention pass `allow_module_level=True`. 
If you want to skip a specific test or entire class, use the @pytest.mark.skip or @pytest.mark.skipif decorators.

This sounds clearer.
Can you give a bit of context of why the message is there in the first place?
It sounds like we should be able to automatically detect if this is skipping a test or skipping the entire module (based on the fact that we can issue the warning).

Maybe this is addressing some past confusion, or we want to push people toward `pytest.mark.skip[if]`, but if we can detect it automatically - we can also deprecate allow_module_level and make `skip()` do the right thing based on the context it's used in.
> Maybe this is addressing some past confusion

That's exactly it, people would use `@pytest.skip` instead of `@pytest.mark.skip` and skip the whole module:

https://github.com/pytest-dev/pytest/issues/2338#issuecomment-290324255

For that reason we don't really want to automatically detect things, but want users to explicitly pass that flag which proves they are not doing it by accident.

Original issue: https://github.com/pytest-dev/pytest/issues/607
Having looked at the links, I think the alternative API to skip a module is more appealing.
Here is a proposed end state:

1. pytest.skip_module is introduced, can be used to skip a module.
2. pytest.skip() is only legal inside of a test. If called outside of a test, an error message is issues.
Example:

> pytest.skip should only be used inside tests. To skip a module use pytest.skip_module. To completely skip a test function or a test class, use the @pytest.mark.skip or @pytest.mark.skipif decorators.

Getting to this end state would include deprecating allow_module_level first, directing people using pytest.skip(allow_module_level=True) to use pytest.skip_module().

I am also fine with just changing the message as you initially proposed but I feel this proposal will result in an healthier state.

-0.5 from my side - I think this is too minor to warrant another deprecation and change.
I agree it would be healthier, but -1 from me for the same reasons as @The-Compiler: we already had a deprecation/change period in order to introduce `allow_module_level`, having yet another one is frustrating/confusing to users, in comparison to the small gains.
Hi, I see that this is still open. If available, I'd like to take this up.

## Patch

```diff

diff --git a/src/_pytest/python.py b/src/_pytest/python.py
--- a/src/_pytest/python.py
+++ b/src/_pytest/python.py
@@ -608,10 +608,10 @@ def _importtestmodule(self):
             if e.allow_module_level:
                 raise
             raise self.CollectError(
-                "Using pytest.skip outside of a test is not allowed. "
-                "To decorate a test function, use the @pytest.mark.skip "
-                "or @pytest.mark.skipif decorators instead, and to skip a "
-                "module use `pytestmark = pytest.mark.{skip,skipif}."
+                "Using pytest.skip outside of a test will skip the entire module. "
+                "If that's your intention, pass `allow_module_level=True`. "
+                "If you want to skip a specific test or an entire class, "
+                "use the @pytest.mark.skip or @pytest.mark.skipif decorators."
             ) from e
         self.config.pluginmanager.consider_module(mod)
         return mod


```

## Test Patch

```diff
diff --git a/testing/test_skipping.py b/testing/test_skipping.py
--- a/testing/test_skipping.py
+++ b/testing/test_skipping.py
@@ -1341,7 +1341,7 @@ def test_func():
     )
     result = pytester.runpytest()
     result.stdout.fnmatch_lines(
-        ["*Using pytest.skip outside of a test is not allowed*"]
+        ["*Using pytest.skip outside of a test will skip the entire module*"]
     )
 
 

```

## Test Information

**Tests that should FAIL→PASS**: ["testing/test_skipping.py::test_module_level_skip_error"]

**Tests that should PASS→PASS**: ["testing/test_skipping.py::test_importorskip", "testing/test_skipping.py::TestEvaluation::test_no_marker", "testing/test_skipping.py::TestEvaluation::test_marked_xfail_no_args", "testing/test_skipping.py::TestEvaluation::test_marked_skipif_no_args", "testing/test_skipping.py::TestEvaluation::test_marked_one_arg", "testing/test_skipping.py::TestEvaluation::test_marked_one_arg_with_reason", "testing/test_skipping.py::TestEvaluation::test_marked_one_arg_twice", "testing/test_skipping.py::TestEvaluation::test_marked_one_arg_twice2", "testing/test_skipping.py::TestEvaluation::test_marked_skipif_with_boolean_without_reason", "testing/test_skipping.py::TestEvaluation::test_marked_skipif_with_invalid_boolean", "testing/test_skipping.py::TestEvaluation::test_skipif_class", "testing/test_skipping.py::TestEvaluation::test_skipif_markeval_namespace", "testing/test_skipping.py::TestEvaluation::test_skipif_markeval_namespace_multiple", "testing/test_skipping.py::TestEvaluation::test_skipif_markeval_namespace_ValueError", "testing/test_skipping.py::TestXFail::test_xfail_simple[True]", "testing/test_skipping.py::TestXFail::test_xfail_simple[False]", "testing/test_skipping.py::TestXFail::test_xfail_xpassed", "testing/test_skipping.py::TestXFail::test_xfail_using_platform", "testing/test_skipping.py::TestXFail::test_xfail_xpassed_strict", "testing/test_skipping.py::TestXFail::test_xfail_run_anyway", "testing/test_skipping.py::TestXFail::test_xfail_run_with_skip_mark[test_input0-expected0]", "testing/test_skipping.py::TestXFail::test_xfail_run_with_skip_mark[test_input1-expected1]", "testing/test_skipping.py::TestXFail::test_xfail_evalfalse_but_fails", "testing/test_skipping.py::TestXFail::test_xfail_not_report_default", "testing/test_skipping.py::TestXFail::test_xfail_not_run_xfail_reporting", "testing/test_skipping.py::TestXFail::test_xfail_not_run_no_setup_run", "testing/test_skipping.py::TestXFail::test_xfail_xpass", "testing/test_skipping.py::TestXFail::test_xfail_imperative", "testing/test_skipping.py::TestXFail::test_xfail_imperative_in_setup_function", "testing/test_skipping.py::TestXFail::test_dynamic_xfail_no_run", "testing/test_skipping.py::TestXFail::test_dynamic_xfail_set_during_funcarg_setup", "testing/test_skipping.py::TestXFail::test_dynamic_xfail_set_during_runtest_failed", "testing/test_skipping.py::TestXFail::test_dynamic_xfail_set_during_runtest_passed_strict", "testing/test_skipping.py::TestXFail::test_xfail_raises[TypeError-TypeError-*1", "testing/test_skipping.py::TestXFail::test_xfail_raises[(AttributeError,", "testing/test_skipping.py::TestXFail::test_xfail_raises[TypeError-IndexError-*1", "testing/test_skipping.py::TestXFail::test_strict_sanity", "testing/test_skipping.py::TestXFail::test_strict_xfail[True]", "testing/test_skipping.py::TestXFail::test_strict_xfail[False]", "testing/test_skipping.py::TestXFail::test_strict_xfail_condition[True]", "testing/test_skipping.py::TestXFail::test_strict_xfail_condition[False]", "testing/test_skipping.py::TestXFail::test_xfail_condition_keyword[True]", "testing/test_skipping.py::TestXFail::test_xfail_condition_keyword[False]", "testing/test_skipping.py::TestXFail::test_strict_xfail_default_from_file[true]", "testing/test_skipping.py::TestXFail::test_strict_xfail_default_from_file[false]", "testing/test_skipping.py::TestXFail::test_xfail_markeval_namespace", "testing/test_skipping.py::TestXFailwithSetupTeardown::test_failing_setup_issue9", "testing/test_skipping.py::TestXFailwithSetupTeardown::test_failing_teardown_issue9", "testing/test_skipping.py::TestSkip::test_skip_class", "testing/test_skipping.py::TestSkip::test_skips_on_false_string", "testing/test_skipping.py::TestSkip::test_arg_as_reason", "testing/test_skipping.py::TestSkip::test_skip_no_reason", "testing/test_skipping.py::TestSkip::test_skip_with_reason", "testing/test_skipping.py::TestSkip::test_only_skips_marked_test", "testing/test_skipping.py::TestSkip::test_strict_and_skip", "testing/test_skipping.py::TestSkip::test_wrong_skip_usage", "testing/test_skipping.py::TestSkipif::test_skipif_conditional", "testing/test_skipping.py::TestSkipif::test_skipif_reporting[\"hasattr(sys,", "testing/test_skipping.py::TestSkipif::test_skipif_reporting[True,", "testing/test_skipping.py::TestSkipif::test_skipif_using_platform", "testing/test_skipping.py::TestSkipif::test_skipif_reporting_multiple[skipif-SKIP-skipped]", "testing/test_skipping.py::TestSkipif::test_skipif_reporting_multiple[xfail-XPASS-xpassed]", "testing/test_skipping.py::test_skip_not_report_default", "testing/test_skipping.py::test_skipif_class", "testing/test_skipping.py::test_skipped_reasons_functional", "testing/test_skipping.py::test_skipped_folding", "testing/test_skipping.py::test_reportchars", "testing/test_skipping.py::test_reportchars_error", "testing/test_skipping.py::test_reportchars_all", "testing/test_skipping.py::test_reportchars_all_error", "testing/test_skipping.py::test_errors_in_xfail_skip_expressions", "testing/test_skipping.py::test_xfail_skipif_with_globals", "testing/test_skipping.py::test_default_markers", "testing/test_skipping.py::test_xfail_test_setup_exception", "testing/test_skipping.py::test_imperativeskip_on_xfail_test", "testing/test_skipping.py::TestBooleanCondition::test_skipif", "testing/test_skipping.py::TestBooleanCondition::test_skipif_noreason", "testing/test_skipping.py::TestBooleanCondition::test_xfail", "testing/test_skipping.py::test_xfail_item", "testing/test_skipping.py::test_module_level_skip_with_allow_module_level", "testing/test_skipping.py::test_invalid_skip_keyword_parameter", "testing/test_skipping.py::test_mark_xfail_item", "testing/test_skipping.py::test_summary_list_after_errors", "testing/test_skipping.py::test_relpath_rootdir"]

**Base Commit**: 69356d20cfee9a81972dcbf93d8caf9eabe113e8
**Environment Setup Commit**: e2ee3144ed6e241dea8d96215fcdca18b3892551
