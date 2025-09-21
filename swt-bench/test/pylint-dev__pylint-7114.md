# pylint-dev__pylint-7114

**Repository**: pylint-dev/pylint
**Created**: 2022-07-03T04:36:40Z
**Version**: 2.15

## Problem Statement

Linting fails if module contains module of the same name
### Steps to reproduce

Given multiple files:
```
.
`-- a/
    |-- a.py
    `-- b.py
```
Which are all empty, running `pylint a` fails:

```
$ pylint a
************* Module a
a/__init__.py:1:0: F0010: error while code parsing: Unable to load file a/__init__.py:
[Errno 2] No such file or directory: 'a/__init__.py' (parse-error)
$
```

However, if I rename `a.py`, `pylint a` succeeds:

```
$ mv a/a.py a/c.py
$ pylint a
$
```
Alternatively, I can also `touch a/__init__.py`, but that shouldn't be necessary anymore.

### Current behavior

Running `pylint a` if `a/a.py` is present fails while searching for an `__init__.py` file.

### Expected behavior

Running `pylint a` if `a/a.py` is present should succeed.

### pylint --version output

Result of `pylint --version` output:

```
pylint 3.0.0a3
astroid 2.5.6
Python 3.8.5 (default, Jan 27 2021, 15:41:15) 
[GCC 9.3.0]
```

### Additional info

This also has some side-effects in module resolution. For example, if I create another file `r.py`:

```
.
|-- a
|   |-- a.py
|   `-- b.py
`-- r.py
```

With the content:

```
from a import b
```

Running `pylint -E r` will run fine, but `pylint -E r a` will fail. Not just for module a, but for module r as well.

```
************* Module r
r.py:1:0: E0611: No name 'b' in module 'a' (no-name-in-module)
************* Module a
a/__init__.py:1:0: F0010: error while code parsing: Unable to load file a/__init__.py:
[Errno 2] No such file or directory: 'a/__init__.py' (parse-error)
```

Again, if I rename `a.py` to `c.py`, `pylint -E r a` will work perfectly.


## Hints

@iFreilicht thanks for your report.
#4909 was a duplicate.

## Patch

```diff

diff --git a/pylint/lint/expand_modules.py b/pylint/lint/expand_modules.py
--- a/pylint/lint/expand_modules.py
+++ b/pylint/lint/expand_modules.py
@@ -82,8 +82,10 @@ def expand_modules(
             continue
         module_path = get_python_path(something)
         additional_search_path = [".", module_path] + path
-        if os.path.exists(something):
-            # this is a file or a directory
+        if os.path.isfile(something) or os.path.exists(
+            os.path.join(something, "__init__.py")
+        ):
+            # this is a file or a directory with an explicit __init__.py
             try:
                 modname = ".".join(
                     modutils.modpath_from_file(something, path=additional_search_path)
@@ -103,9 +105,7 @@ def expand_modules(
                 )
                 if filepath is None:
                     continue
-            except (ImportError, SyntaxError) as ex:
-                # The SyntaxError is a Python bug and should be
-                # removed once we move away from imp.find_module: https://bugs.python.org/issue10588
+            except ImportError as ex:
                 errors.append({"key": "fatal", "mod": modname, "ex": ex})
                 continue
         filepath = os.path.normpath(filepath)


```

## Test Patch

```diff
diff --git a/tests/checkers/unittest_imports.py b/tests/checkers/unittest_imports.py
--- a/tests/checkers/unittest_imports.py
+++ b/tests/checkers/unittest_imports.py
@@ -7,6 +7,7 @@
 import os
 
 import astroid
+import pytest
 
 from pylint import epylint as lint
 from pylint.checkers import imports
@@ -40,6 +41,9 @@ def test_relative_beyond_top_level(self) -> None:
             self.checker.visit_importfrom(module.body[2].body[0])
 
     @staticmethod
+    @pytest.mark.xfail(
+        reason="epylint manipulates cwd; these tests should not be using epylint"
+    )
     def test_relative_beyond_top_level_two() -> None:
         output, errors = lint.py_run(
             f"{os.path.join(REGR_DATA, 'beyond_top_two')} -d all -e relative-beyond-top-level",
diff --git a/tests/lint/unittest_lint.py b/tests/lint/unittest_lint.py
--- a/tests/lint/unittest_lint.py
+++ b/tests/lint/unittest_lint.py
@@ -942,3 +942,12 @@ def test_lint_namespace_package_under_dir(initialized_linter: PyLinter) -> None:
         create_files(["outer/namespace/__init__.py", "outer/namespace/module.py"])
         linter.check(["outer.namespace"])
     assert not linter.stats.by_msg
+
+
+def test_identically_named_nested_module(initialized_linter: PyLinter) -> None:
+    with tempdir():
+        create_files(["identical/identical.py"])
+        with open("identical/identical.py", "w", encoding="utf-8") as f:
+            f.write("import imp")
+        initialized_linter.check(["identical"])
+    assert initialized_linter.stats.by_msg["deprecated-module"] == 1

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/lint/unittest_lint.py::test_identically_named_nested_module"]

**Tests that should PASS→PASS**: ["tests/checkers/unittest_imports.py::TestImportsChecker::test_relative_beyond_top_level", "tests/checkers/unittest_imports.py::TestImportsChecker::test_relative_beyond_top_level_three", "tests/checkers/unittest_imports.py::TestImportsChecker::test_relative_beyond_top_level_four", "tests/lint/unittest_lint.py::test_no_args", "tests/lint/unittest_lint.py::test_one_arg[case0]", "tests/lint/unittest_lint.py::test_one_arg[case1]", "tests/lint/unittest_lint.py::test_one_arg[case2]", "tests/lint/unittest_lint.py::test_one_arg[case3]", "tests/lint/unittest_lint.py::test_one_arg[case4]", "tests/lint/unittest_lint.py::test_two_similar_args[case0]", "tests/lint/unittest_lint.py::test_two_similar_args[case1]", "tests/lint/unittest_lint.py::test_two_similar_args[case2]", "tests/lint/unittest_lint.py::test_two_similar_args[case3]", "tests/lint/unittest_lint.py::test_more_args[case0]", "tests/lint/unittest_lint.py::test_more_args[case1]", "tests/lint/unittest_lint.py::test_more_args[case2]", "tests/lint/unittest_lint.py::test_pylint_visit_method_taken_in_account", "tests/lint/unittest_lint.py::test_enable_message", "tests/lint/unittest_lint.py::test_enable_message_category", "tests/lint/unittest_lint.py::test_message_state_scope", "tests/lint/unittest_lint.py::test_enable_message_block", "tests/lint/unittest_lint.py::test_enable_by_symbol", "tests/lint/unittest_lint.py::test_enable_report", "tests/lint/unittest_lint.py::test_report_output_format_aliased", "tests/lint/unittest_lint.py::test_set_unsupported_reporter", "tests/lint/unittest_lint.py::test_set_option_1", "tests/lint/unittest_lint.py::test_set_option_2", "tests/lint/unittest_lint.py::test_enable_checkers", "tests/lint/unittest_lint.py::test_errors_only", "tests/lint/unittest_lint.py::test_disable_similar", "tests/lint/unittest_lint.py::test_disable_alot", "tests/lint/unittest_lint.py::test_addmessage", "tests/lint/unittest_lint.py::test_addmessage_invalid", "tests/lint/unittest_lint.py::test_load_plugin_command_line", "tests/lint/unittest_lint.py::test_load_plugin_config_file", "tests/lint/unittest_lint.py::test_load_plugin_configuration", "tests/lint/unittest_lint.py::test_init_hooks_called_before_load_plugins", "tests/lint/unittest_lint.py::test_analyze_explicit_script", "tests/lint/unittest_lint.py::test_full_documentation", "tests/lint/unittest_lint.py::test_list_msgs_enabled", "tests/lint/unittest_lint.py::test_pylint_home", "tests/lint/unittest_lint.py::test_pylint_home_from_environ", "tests/lint/unittest_lint.py::test_warn_about_old_home", "tests/lint/unittest_lint.py::test_pylintrc", "tests/lint/unittest_lint.py::test_pylintrc_parentdir", "tests/lint/unittest_lint.py::test_pylintrc_parentdir_no_package", "tests/lint/unittest_lint.py::test_custom_should_analyze_file", "tests/lint/unittest_lint.py::test_multiprocessing[1]", "tests/lint/unittest_lint.py::test_multiprocessing[2]", "tests/lint/unittest_lint.py::test_filename_with__init__", "tests/lint/unittest_lint.py::test_by_module_statement_value", "tests/lint/unittest_lint.py::test_recursive_ignore[--ignore-failing.py]", "tests/lint/unittest_lint.py::test_recursive_ignore[--ignore-ignored_subdirectory]", "tests/lint/unittest_lint.py::test_recursive_ignore[--ignore-patterns-failing.*]", "tests/lint/unittest_lint.py::test_recursive_ignore[--ignore-patterns-ignored_*]", "tests/lint/unittest_lint.py::test_recursive_ignore[--ignore-paths-.*directory/ignored.*]", "tests/lint/unittest_lint.py::test_recursive_ignore[--ignore-paths-.*ignored.*/failing.*]", "tests/lint/unittest_lint.py::test_import_sibling_module_from_namespace", "tests/lint/unittest_lint.py::test_lint_namespace_package_under_dir"]

**Base Commit**: 397c1703e8ae6349d33f7b99f45b2ccaf581e666
**Environment Setup Commit**: e90702074e68e20dc8e5df5013ee3ecf22139c3e
