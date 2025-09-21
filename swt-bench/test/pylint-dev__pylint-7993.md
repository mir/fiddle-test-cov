# pylint-dev__pylint-7993

**Repository**: pylint-dev/pylint
**Created**: 2022-12-27T18:20:50Z
**Version**: 2.15

## Problem Statement

Using custom braces in message template does not work
### Bug description

Have any list of errors:

On pylint 1.7 w/ python3.6 - I am able to use this as my message template
```
$ pylint test.py --msg-template='{{ "Category": "{category}" }}'
No config file found, using default configuration
************* Module [redacted].test
{ "Category": "convention" }
{ "Category": "error" }
{ "Category": "error" }
{ "Category": "convention" }
{ "Category": "convention" }
{ "Category": "convention" }
{ "Category": "error" }
```

However, on Python3.9 with Pylint 2.12.2, I get the following:
```
$ pylint test.py --msg-template='{{ "Category": "{category}" }}'
[redacted]/site-packages/pylint/reporters/text.py:206: UserWarning: Don't recognize the argument '{ "Category"' in the --msg-template. Are you sure it is supported on the current version of pylint?
  warnings.warn(
************* Module [redacted].test
" }
" }
" }
" }
" }
" }
```

Is this intentional or a bug?

### Configuration

_No response_

### Command used

```shell
pylint test.py --msg-template='{{ "Category": "{category}" }}'
```


### Pylint output

```shell
[redacted]/site-packages/pylint/reporters/text.py:206: UserWarning: Don't recognize the argument '{ "Category"' in the --msg-template. Are you sure it is supported on the current version of pylint?
  warnings.warn(
************* Module [redacted].test
" }
" }
" }
" }
" }
" }
```


### Expected behavior

Expect the dictionary to print out with `"Category"` as the key.

### Pylint version

```shell
Affected Version:
pylint 2.12.2
astroid 2.9.2
Python 3.9.9+ (heads/3.9-dirty:a2295a4, Dec 21 2021, 22:32:52) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]


Previously working version:
No config file found, using default configuration
pylint 1.7.4, 
astroid 1.6.6
Python 3.6.8 (default, Nov 16 2020, 16:55:22) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
```


### OS / Environment

_No response_

### Additional dependencies

_No response_


## Hints

Subsequently, there is also this behavior with the quotes
```
$ pylint test.py --msg-template='"Category": "{category}"'
************* Module test
Category": "convention
Category": "error
Category": "error
Category": "convention
Category": "convention
Category": "error

$ pylint test.py --msg-template='""Category": "{category}""'
************* Module test
"Category": "convention"
"Category": "error"
"Category": "error"
"Category": "convention"
"Category": "convention"
"Category": "error"
```
Commit that changed the behavior was probably this one: https://github.com/PyCQA/pylint/commit/7c3533ca48e69394391945de1563ef7f639cd27d#diff-76025f0bc82e83cb406321006fbca12c61a10821834a3164620fc17c978f9b7e

And I tested on 2.11.1 that it is working as intended on that version.
Thanks for digging into this !

## Patch

```diff

diff --git a/pylint/reporters/text.py b/pylint/reporters/text.py
--- a/pylint/reporters/text.py
+++ b/pylint/reporters/text.py
@@ -175,7 +175,7 @@ def on_set_current_module(self, module: str, filepath: str | None) -> None:
         self._template = template
 
         # Check to see if all parameters in the template are attributes of the Message
-        arguments = re.findall(r"\{(.+?)(:.*)?\}", template)
+        arguments = re.findall(r"\{(\w+?)(:.*)?\}", template)
         for argument in arguments:
             if argument[0] not in MESSAGE_FIELDS:
                 warnings.warn(


```

## Test Patch

```diff
diff --git a/tests/reporters/unittest_reporting.py b/tests/reporters/unittest_reporting.py
--- a/tests/reporters/unittest_reporting.py
+++ b/tests/reporters/unittest_reporting.py
@@ -14,6 +14,7 @@
 from typing import TYPE_CHECKING
 
 import pytest
+from _pytest.recwarn import WarningsRecorder
 
 from pylint import checkers
 from pylint.interfaces import HIGH
@@ -88,16 +89,12 @@ def test_template_option_non_existing(linter) -> None:
     """
     output = StringIO()
     linter.reporter.out = output
-    linter.config.msg_template = (
-        "{path}:{line}:{a_new_option}:({a_second_new_option:03d})"
-    )
+    linter.config.msg_template = "{path}:{line}:{categ}:({a_second_new_option:03d})"
     linter.open()
     with pytest.warns(UserWarning) as records:
         linter.set_current_module("my_mod")
         assert len(records) == 2
-        assert (
-            "Don't recognize the argument 'a_new_option'" in records[0].message.args[0]
-        )
+        assert "Don't recognize the argument 'categ'" in records[0].message.args[0]
     assert (
         "Don't recognize the argument 'a_second_new_option'"
         in records[1].message.args[0]
@@ -113,7 +110,24 @@ def test_template_option_non_existing(linter) -> None:
     assert out_lines[2] == "my_mod:2::()"
 
 
-def test_deprecation_set_output(recwarn):
+def test_template_option_with_header(linter: PyLinter) -> None:
+    output = StringIO()
+    linter.reporter.out = output
+    linter.config.msg_template = '{{ "Category": "{category}" }}'
+    linter.open()
+    linter.set_current_module("my_mod")
+
+    linter.add_message("C0301", line=1, args=(1, 2))
+    linter.add_message(
+        "line-too-long", line=2, end_lineno=2, end_col_offset=4, args=(3, 4)
+    )
+
+    out_lines = output.getvalue().split("\n")
+    assert out_lines[1] == '{ "Category": "convention" }'
+    assert out_lines[2] == '{ "Category": "convention" }'
+
+
+def test_deprecation_set_output(recwarn: WarningsRecorder) -> None:
     """TODO remove in 3.0."""
     reporter = BaseReporter()
     # noinspection PyDeprecation

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/reporters/unittest_reporting.py::test_template_option_with_header"]

**Tests that should PASS→PASS**: ["tests/reporters/unittest_reporting.py::test_template_option", "tests/reporters/unittest_reporting.py::test_template_option_default", "tests/reporters/unittest_reporting.py::test_template_option_end_line", "tests/reporters/unittest_reporting.py::test_template_option_non_existing", "tests/reporters/unittest_reporting.py::test_deprecation_set_output", "tests/reporters/unittest_reporting.py::test_parseable_output_deprecated", "tests/reporters/unittest_reporting.py::test_parseable_output_regression", "tests/reporters/unittest_reporting.py::test_multi_format_output", "tests/reporters/unittest_reporting.py::test_multi_reporter_independant_messages", "tests/reporters/unittest_reporting.py::test_display_results_is_renamed"]

**Base Commit**: e90702074e68e20dc8e5df5013ee3ecf22139c3e
**Environment Setup Commit**: e90702074e68e20dc8e5df5013ee3ecf22139c3e
