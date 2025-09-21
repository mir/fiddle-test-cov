# pylint-dev__pylint-6506

**Repository**: pylint-dev/pylint
**Created**: 2022-05-05T13:01:41Z
**Version**: 2.14

## Problem Statement

Traceback printed for unrecognized option
### Bug description

A traceback is printed when an unrecognized option is passed to pylint.

### Configuration

_No response_

### Command used

```shell
pylint -Q
```


### Pylint output

```shell
************* Module Command line
Command line:1:0: E0015: Unrecognized option found: Q (unrecognized-option)
Traceback (most recent call last):
  File "/Users/markbyrne/venv310/bin/pylint", line 33, in <module>
    sys.exit(load_entry_point('pylint', 'console_scripts', 'pylint')())
  File "/Users/markbyrne/programming/pylint/pylint/__init__.py", line 24, in run_pylint
    PylintRun(argv or sys.argv[1:])
  File "/Users/markbyrne/programming/pylint/pylint/lint/run.py", line 135, in __init__
    args = _config_initialization(
  File "/Users/markbyrne/programming/pylint/pylint/config/config_initialization.py", line 85, in _config_initialization
    raise _UnrecognizedOptionError(options=unrecognized_options)
pylint.config.exceptions._UnrecognizedOptionError
```


### Expected behavior

The top part of the current output is handy:
`Command line:1:0: E0015: Unrecognized option found: Q (unrecognized-option)`

The traceback I don't think is expected & not user-friendly.
A usage tip, for example:
```python
mypy -Q
usage: mypy [-h] [-v] [-V] [more options; see below]
            [-m MODULE] [-p PACKAGE] [-c PROGRAM_TEXT] [files ...]
mypy: error: unrecognized arguments: -Q
```

### Pylint version

```shell
pylint 2.14.0-dev0
astroid 2.11.3
Python 3.10.0b2 (v3.10.0b2:317314165a, May 31 2021, 10:02:22) [Clang 12.0.5 (clang-1205.0.22.9)]
```


### OS / Environment

_No response_

### Additional dependencies

_No response_


## Hints

@Pierre-Sassoulas Agreed that this is a blocker for `2.14` but not necessarily for the beta. This is just a "nice-to-have".

Thanks @mbyrnepr2 for reporting though!
👍 the blocker are for the final release only. We could add a 'beta-blocker' label, that would be very humorous !

## Patch

```diff

diff --git a/pylint/config/config_initialization.py b/pylint/config/config_initialization.py
--- a/pylint/config/config_initialization.py
+++ b/pylint/config/config_initialization.py
@@ -81,8 +81,7 @@ def _config_initialization(
             unrecognized_options.append(opt[1:])
     if unrecognized_options:
         msg = ", ".join(unrecognized_options)
-        linter.add_message("unrecognized-option", line=0, args=msg)
-        raise _UnrecognizedOptionError(options=unrecognized_options)
+        linter._arg_parser.error(f"Unrecognized option found: {msg}")
 
     # Set the current module to configuration as we don't know where
     # the --load-plugins key is coming from


```

## Test Patch

```diff
diff --git a/tests/config/test_config.py b/tests/config/test_config.py
--- a/tests/config/test_config.py
+++ b/tests/config/test_config.py
@@ -10,7 +10,6 @@
 import pytest
 from pytest import CaptureFixture
 
-from pylint.config.exceptions import _UnrecognizedOptionError
 from pylint.lint import Run as LintRun
 from pylint.testutils._run import _Run as Run
 from pylint.testutils.configuration_test import run_using_a_configuration_file
@@ -65,18 +64,20 @@ def test_unknown_message_id(capsys: CaptureFixture) -> None:
 
 def test_unknown_option_name(capsys: CaptureFixture) -> None:
     """Check that we correctly raise a message on an unknown option."""
-    with pytest.raises(_UnrecognizedOptionError):
+    with pytest.raises(SystemExit):
         Run([str(EMPTY_MODULE), "--unknown-option=yes"], exit=False)
     output = capsys.readouterr()
-    assert "E0015: Unrecognized option found: unknown-option=yes" in output.out
+    assert "usage: pylint" in output.err
+    assert "Unrecognized option" in output.err
 
 
 def test_unknown_short_option_name(capsys: CaptureFixture) -> None:
     """Check that we correctly raise a message on an unknown short option."""
-    with pytest.raises(_UnrecognizedOptionError):
+    with pytest.raises(SystemExit):
         Run([str(EMPTY_MODULE), "-Q"], exit=False)
     output = capsys.readouterr()
-    assert "E0015: Unrecognized option found: Q" in output.out
+    assert "usage: pylint" in output.err
+    assert "Unrecognized option" in output.err
 
 
 def test_unknown_confidence(capsys: CaptureFixture) -> None:

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/config/test_config.py::test_unknown_option_name", "tests/config/test_config.py::test_unknown_short_option_name"]

**Tests that should PASS→PASS**: ["tests/config/test_config.py::test_can_read_toml_env_variable", "tests/config/test_config.py::test_unknown_message_id", "tests/config/test_config.py::test_unknown_confidence", "tests/config/test_config.py::test_unknown_yes_no", "tests/config/test_config.py::test_unknown_py_version", "tests/config/test_config.py::test_short_verbose"]

**Base Commit**: 0a4204fd7555cfedd43f43017c94d24ef48244a5
**Environment Setup Commit**: 680edebc686cad664bbed934a490aeafa775f163
