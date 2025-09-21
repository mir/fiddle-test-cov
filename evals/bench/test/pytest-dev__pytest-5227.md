# pytest-dev__pytest-5227

**Repository**: pytest-dev/pytest
**Created**: 2019-05-07T20:27:24Z
**Version**: 4.4

## Problem Statement

Improve default logging format
Currently it is:

> DEFAULT_LOG_FORMAT = "%(filename)-25s %(lineno)4d %(levelname)-8s %(message)s"

I think `name` (module name) would be very useful here, instead of just the base filename.

(It might also be good to have the relative path there (maybe at the end), but it is usually still very long (but e.g. `$VIRTUAL_ENV` could be substituted therein))

Currently it would look like this:
```
utils.py                   114 DEBUG    (0.000) SELECT "app_url"."id", "app_url"."created", "app_url"."url" FROM "app_url" WHERE "app_url"."id" = 2; args=(2,)
multipart.py               604 DEBUG    Calling on_field_start with no data
```


Using `DEFAULT_LOG_FORMAT = "%(levelname)-8s %(name)s:%(filename)s:%(lineno)d %(message)s"` instead:

```
DEBUG    django.db.backends:utils.py:114 (0.000) SELECT "app_url"."id", "app_url"."created", "app_url"."url" FROM "app_url" WHERE "app_url"."id" = 2; args=(2,)
DEBUG    multipart.multipart:multipart.py:604 Calling on_field_start with no data
```


## Patch

```diff

diff --git a/src/_pytest/logging.py b/src/_pytest/logging.py
--- a/src/_pytest/logging.py
+++ b/src/_pytest/logging.py
@@ -15,7 +15,7 @@
 from _pytest.config import create_terminal_writer
 from _pytest.pathlib import Path
 
-DEFAULT_LOG_FORMAT = "%(filename)-25s %(lineno)4d %(levelname)-8s %(message)s"
+DEFAULT_LOG_FORMAT = "%(levelname)-8s %(name)s:%(filename)s:%(lineno)d %(message)s"
 DEFAULT_LOG_DATE_FORMAT = "%H:%M:%S"
 
 


```

## Test Patch

```diff
diff --git a/testing/logging/test_reporting.py b/testing/logging/test_reporting.py
--- a/testing/logging/test_reporting.py
+++ b/testing/logging/test_reporting.py
@@ -248,7 +248,7 @@ def test_log_cli():
             [
                 "test_log_cli_enabled_disabled.py::test_log_cli ",
                 "*-- live log call --*",
-                "test_log_cli_enabled_disabled.py* CRITICAL critical message logged by test",
+                "CRITICAL *test_log_cli_enabled_disabled.py* critical message logged by test",
                 "PASSED*",
             ]
         )
@@ -282,7 +282,7 @@ def test_log_cli(request):
     result.stdout.fnmatch_lines(
         [
             "test_log_cli_default_level.py::test_log_cli ",
-            "test_log_cli_default_level.py*WARNING message will be shown*",
+            "WARNING*test_log_cli_default_level.py* message will be shown*",
         ]
     )
     assert "INFO message won't be shown" not in result.stdout.str()
@@ -523,7 +523,7 @@ def test_log_1(fix):
     )
     assert (
         re.search(
-            r"(.+)live log teardown(.+)\n(.+)WARNING(.+)\n(.+)WARNING(.+)",
+            r"(.+)live log teardown(.+)\nWARNING(.+)\nWARNING(.+)",
             result.stdout.str(),
             re.MULTILINE,
         )
@@ -531,7 +531,7 @@ def test_log_1(fix):
     )
     assert (
         re.search(
-            r"(.+)live log finish(.+)\n(.+)WARNING(.+)\n(.+)WARNING(.+)",
+            r"(.+)live log finish(.+)\nWARNING(.+)\nWARNING(.+)",
             result.stdout.str(),
             re.MULTILINE,
         )
@@ -565,7 +565,7 @@ def test_log_cli(request):
     # fnmatch_lines does an assertion internally
     result.stdout.fnmatch_lines(
         [
-            "test_log_cli_level.py*This log message will be shown",
+            "*test_log_cli_level.py*This log message will be shown",
             "PASSED",  # 'PASSED' on its own line because the log message prints a new line
         ]
     )
@@ -579,7 +579,7 @@ def test_log_cli(request):
     # fnmatch_lines does an assertion internally
     result.stdout.fnmatch_lines(
         [
-            "test_log_cli_level.py* This log message will be shown",
+            "*test_log_cli_level.py* This log message will be shown",
             "PASSED",  # 'PASSED' on its own line because the log message prints a new line
         ]
     )
@@ -615,7 +615,7 @@ def test_log_cli(request):
     # fnmatch_lines does an assertion internally
     result.stdout.fnmatch_lines(
         [
-            "test_log_cli_ini_level.py* This log message will be shown",
+            "*test_log_cli_ini_level.py* This log message will be shown",
             "PASSED",  # 'PASSED' on its own line because the log message prints a new line
         ]
     )

```

## Test Information

**Tests that should FAIL→PASS**: ["testing/logging/test_reporting.py::test_log_cli_enabled_disabled[True]", "testing/logging/test_reporting.py::test_log_cli_default_level", "testing/logging/test_reporting.py::test_sections_single_new_line_after_test_outcome"]

**Tests that should PASS→PASS**: ["[100%]", "[", "[100%]------------------------------", "testing/logging/test_reporting.py::test_live_logging_suspends_capture[True]", "testing/logging/test_reporting.py::test_live_logging_suspends_capture[False]", "testing/logging/test_reporting.py::test_nothing_logged", "testing/logging/test_reporting.py::test_messages_logged", "testing/logging/test_reporting.py::test_root_logger_affected", "testing/logging/test_reporting.py::test_log_cli_level_log_level_interaction", "testing/logging/test_reporting.py::test_setup_logging", "testing/logging/test_reporting.py::test_teardown_logging", "testing/logging/test_reporting.py::test_disable_log_capturing", "testing/logging/test_reporting.py::test_disable_log_capturing_ini", "testing/logging/test_reporting.py::test_log_cli_enabled_disabled[False]", "testing/logging/test_reporting.py::test_log_cli_default_level_multiple_tests", "testing/logging/test_reporting.py::test_log_cli_default_level_sections", "testing/logging/test_reporting.py::test_live_logs_unknown_sections", "testing/logging/test_reporting.py::test_log_cli_level", "testing/logging/test_reporting.py::test_log_cli_ini_level", "testing/logging/test_reporting.py::test_log_cli_auto_enable[]", "testing/logging/test_reporting.py::test_log_cli_auto_enable[--log-level=WARNING]", "testing/logging/test_reporting.py::test_log_cli_auto_enable[--log-file-level=WARNING]", "testing/logging/test_reporting.py::test_log_cli_auto_enable[--log-cli-level=WARNING]", "testing/logging/test_reporting.py::test_log_file_cli", "testing/logging/test_reporting.py::test_log_file_cli_level", "testing/logging/test_reporting.py::test_log_level_not_changed_by_default", "testing/logging/test_reporting.py::test_log_file_ini", "testing/logging/test_reporting.py::test_log_file_ini_level", "testing/logging/test_reporting.py::test_log_file_unicode", "testing/logging/test_reporting.py::test_collection_live_logging", "testing/logging/test_reporting.py::test_collection_logging_to_file", "testing/logging/test_reporting.py::test_log_in_hooks", "testing/logging/test_reporting.py::test_log_in_runtest_logreport", "testing/logging/test_reporting.py::test_log_set_path"]

**Base Commit**: 2051e30b9b596e944524ccb787ed20f9f5be93e3
**Environment Setup Commit**: 4ccaa987d47566e3907f2f74167c4ab7997f622f
