# pytest-dev__pytest-9359

**Repository**: pytest-dev/pytest
**Created**: 2021-12-01T14:31:38Z
**Version**: 7.0

## Problem Statement

Error message prints extra code line when using assert in python3.9
<!--
Thanks for submitting an issue!

Quick check-list while reporting bugs:
-->

- [x] a detailed description of the bug or problem you are having
- [x] output of `pip list` from the virtual environment you are using
- [x] pytest and operating system versions
- [ ] minimal example if possible
### Description
I have a test like this:
```
from pytest import fixture


def t(foo):
    return foo


@fixture
def foo():
    return 1


def test_right_statement(foo):
    assert foo == (3 + 2) * (6 + 9)

    @t
    def inner():
        return 2

    assert 2 == inner


@t
def outer():
    return 2
```
The test "test_right_statement" fails at the first assertion,but print extra code (the "t" decorator) in error details, like this:

```
 ============================= test session starts =============================
platform win32 -- Python 3.9.6, pytest-6.2.5, py-1.10.0, pluggy-0.13.1 -- 
cachedir: .pytest_cache
rootdir: 
plugins: allure-pytest-2.9.45
collecting ... collected 1 item

test_statement.py::test_right_statement FAILED                           [100%]

================================== FAILURES ===================================
____________________________ test_right_statement _____________________________

foo = 1

    def test_right_statement(foo):
>       assert foo == (3 + 2) * (6 + 9)
    
        @t
E       assert 1 == 75
E         +1
E         -75

test_statement.py:14: AssertionError
=========================== short test summary info ===========================
FAILED test_statement.py::test_right_statement - assert 1 == 75
============================== 1 failed in 0.12s ==============================
```
And the same thing **did not** happen when using python3.7.10：
```
============================= test session starts =============================
platform win32 -- Python 3.7.10, pytest-6.2.5, py-1.11.0, pluggy-1.0.0 -- 
cachedir: .pytest_cache
rootdir: 
collecting ... collected 1 item

test_statement.py::test_right_statement FAILED                           [100%]

================================== FAILURES ===================================
____________________________ test_right_statement _____________________________

foo = 1

    def test_right_statement(foo):
>       assert foo == (3 + 2) * (6 + 9)
E       assert 1 == 75
E         +1
E         -75

test_statement.py:14: AssertionError
=========================== short test summary info ===========================
FAILED test_statement.py::test_right_statement - assert 1 == 75
============================== 1 failed in 0.03s ==============================
```
Is there some problems when calculate the statement lineno?

### pip list 
```
$ pip list
Package            Version
------------------ -------
atomicwrites       1.4.0
attrs              21.2.0
colorama           0.4.4
importlib-metadata 4.8.2
iniconfig          1.1.1
packaging          21.3
pip                21.3.1
pluggy             1.0.0
py                 1.11.0
pyparsing          3.0.6
pytest             6.2.5
setuptools         59.4.0
toml               0.10.2
typing_extensions  4.0.0
zipp               3.6.0

```
### pytest and operating system versions
pytest 6.2.5
Windows 10 
Seems to happen in python 3.9,not 3.7



## Patch

```diff

diff --git a/src/_pytest/_code/source.py b/src/_pytest/_code/source.py
--- a/src/_pytest/_code/source.py
+++ b/src/_pytest/_code/source.py
@@ -149,6 +149,11 @@ def get_statement_startend2(lineno: int, node: ast.AST) -> Tuple[int, Optional[i
     values: List[int] = []
     for x in ast.walk(node):
         if isinstance(x, (ast.stmt, ast.ExceptHandler)):
+            # Before Python 3.8, the lineno of a decorated class or function pointed at the decorator.
+            # Since Python 3.8, the lineno points to the class/def, so need to include the decorators.
+            if isinstance(x, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
+                for d in x.decorator_list:
+                    values.append(d.lineno - 1)
             values.append(x.lineno - 1)
             for name in ("finalbody", "orelse"):
                 val: Optional[List[ast.stmt]] = getattr(x, name, None)


```

## Test Patch

```diff
diff --git a/testing/code/test_source.py b/testing/code/test_source.py
--- a/testing/code/test_source.py
+++ b/testing/code/test_source.py
@@ -618,6 +618,19 @@ def something():
     assert str(source) == "def func(): raise ValueError(42)"
 
 
+def test_decorator() -> None:
+    s = """\
+def foo(f):
+    pass
+
+@foo
+def bar():
+    pass
+    """
+    source = getstatement(3, s)
+    assert "@foo" in str(source)
+
+
 def XXX_test_expression_multiline() -> None:
     source = """\
 something

```

## Test Information

**Tests that should FAIL→PASS**: ["testing/code/test_source.py::test_decorator"]

**Tests that should PASS→PASS**: ["testing/code/test_source.py::test_source_str_function", "testing/code/test_source.py::test_source_from_function", "testing/code/test_source.py::test_source_from_method", "testing/code/test_source.py::test_source_from_lines", "testing/code/test_source.py::test_source_from_inner_function", "testing/code/test_source.py::test_source_strips", "testing/code/test_source.py::test_source_strip_multiline", "testing/code/test_source.py::TestAccesses::test_getrange", "testing/code/test_source.py::TestAccesses::test_getrange_step_not_supported", "testing/code/test_source.py::TestAccesses::test_getline", "testing/code/test_source.py::TestAccesses::test_len", "testing/code/test_source.py::TestAccesses::test_iter", "testing/code/test_source.py::TestSourceParsing::test_getstatement", "testing/code/test_source.py::TestSourceParsing::test_getstatementrange_triple_quoted", "testing/code/test_source.py::TestSourceParsing::test_getstatementrange_within_constructs", "testing/code/test_source.py::TestSourceParsing::test_getstatementrange_bug", "testing/code/test_source.py::TestSourceParsing::test_getstatementrange_bug2", "testing/code/test_source.py::TestSourceParsing::test_getstatementrange_ast_issue58", "testing/code/test_source.py::TestSourceParsing::test_getstatementrange_out_of_bounds_py3", "testing/code/test_source.py::TestSourceParsing::test_getstatementrange_with_syntaxerror_issue7", "testing/code/test_source.py::test_getstartingblock_singleline", "testing/code/test_source.py::test_getline_finally", "testing/code/test_source.py::test_getfuncsource_dynamic", "testing/code/test_source.py::test_getfuncsource_with_multine_string", "testing/code/test_source.py::test_deindent", "testing/code/test_source.py::test_source_of_class_at_eof_without_newline", "testing/code/test_source.py::test_source_fallback", "testing/code/test_source.py::test_findsource_fallback", "testing/code/test_source.py::test_findsource", "testing/code/test_source.py::test_getfslineno", "testing/code/test_source.py::test_code_of_object_instance_with_call", "testing/code/test_source.py::test_oneline", "testing/code/test_source.py::test_comment_and_no_newline_at_end", "testing/code/test_source.py::test_oneline_and_comment", "testing/code/test_source.py::test_comments", "testing/code/test_source.py::test_comment_in_statement", "testing/code/test_source.py::test_source_with_decorator", "testing/code/test_source.py::test_single_line_else", "testing/code/test_source.py::test_single_line_finally", "testing/code/test_source.py::test_issue55", "testing/code/test_source.py::test_multiline", "testing/code/test_source.py::TestTry::test_body", "testing/code/test_source.py::TestTry::test_except_line", "testing/code/test_source.py::TestTry::test_except_body", "testing/code/test_source.py::TestTry::test_else", "testing/code/test_source.py::TestTryFinally::test_body", "testing/code/test_source.py::TestTryFinally::test_finally", "testing/code/test_source.py::TestIf::test_body", "testing/code/test_source.py::TestIf::test_elif_clause", "testing/code/test_source.py::TestIf::test_elif", "testing/code/test_source.py::TestIf::test_else", "testing/code/test_source.py::test_semicolon", "testing/code/test_source.py::test_def_online", "testing/code/test_source.py::test_getstartingblock_multiline"]

**Base Commit**: e2ee3144ed6e241dea8d96215fcdca18b3892551
**Environment Setup Commit**: e2ee3144ed6e241dea8d96215fcdca18b3892551
