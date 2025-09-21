# pytest-dev__pytest-5692

**Repository**: pytest-dev/pytest
**Created**: 2019-08-03T14:15:04Z
**Version**: 5.0

## Problem Statement

Hostname and timestamp properties in generated JUnit XML reports
Pytest enables generating JUnit XML reports of the tests.

However, there are some properties missing, specifically `hostname` and `timestamp` from the `testsuite` XML element. Is there an option to include them?

Example of a pytest XML report:
```xml
<?xml version="1.0" encoding="utf-8"?>
<testsuite errors="0" failures="2" name="check" skipped="0" tests="4" time="0.049">
	<testcase classname="test_sample.TestClass" file="test_sample.py" line="3" name="test_addOne_normal" time="0.001"></testcase>
	<testcase classname="test_sample.TestClass" file="test_sample.py" line="6" name="test_addOne_edge" time="0.001"></testcase>
</testsuite>
```

Example of a junit XML report:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="location.GeoLocationTest" tests="2" skipped="0" failures="0" errors="0" timestamp="2019-04-22T10:32:27" hostname="Anass-MacBook-Pro.local" time="0.048">
  <properties/>
  <testcase name="testIoException()" classname="location.GeoLocationTest" time="0.044"/>
  <testcase name="testJsonDeserialization()" classname="location.GeoLocationTest" time="0.003"/>
  <system-out><![CDATA[]]></system-out>
  <system-err><![CDATA[]]></system-err>
</testsuite>
```


## Patch

```diff

diff --git a/src/_pytest/junitxml.py b/src/_pytest/junitxml.py
--- a/src/_pytest/junitxml.py
+++ b/src/_pytest/junitxml.py
@@ -10,9 +10,11 @@
 """
 import functools
 import os
+import platform
 import re
 import sys
 import time
+from datetime import datetime
 
 import py
 
@@ -666,6 +668,8 @@ def pytest_sessionfinish(self):
             skipped=self.stats["skipped"],
             tests=numtests,
             time="%.3f" % suite_time_delta,
+            timestamp=datetime.fromtimestamp(self.suite_start_time).isoformat(),
+            hostname=platform.node(),
         )
         logfile.write(Junit.testsuites([suite_node]).unicode(indent=0))
         logfile.close()


```

## Test Patch

```diff
diff --git a/testing/test_junitxml.py b/testing/test_junitxml.py
--- a/testing/test_junitxml.py
+++ b/testing/test_junitxml.py
@@ -1,4 +1,6 @@
 import os
+import platform
+from datetime import datetime
 from xml.dom import minidom
 
 import py
@@ -139,6 +141,30 @@ def test_xpass():
         node = dom.find_first_by_tag("testsuite")
         node.assert_attr(name="pytest", errors=1, failures=2, skipped=1, tests=5)
 
+    def test_hostname_in_xml(self, testdir):
+        testdir.makepyfile(
+            """
+            def test_pass():
+                pass
+        """
+        )
+        result, dom = runandparse(testdir)
+        node = dom.find_first_by_tag("testsuite")
+        node.assert_attr(hostname=platform.node())
+
+    def test_timestamp_in_xml(self, testdir):
+        testdir.makepyfile(
+            """
+            def test_pass():
+                pass
+        """
+        )
+        start_time = datetime.now()
+        result, dom = runandparse(testdir)
+        node = dom.find_first_by_tag("testsuite")
+        timestamp = datetime.strptime(node["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")
+        assert start_time <= timestamp < datetime.now()
+
     def test_timing_function(self, testdir):
         testdir.makepyfile(
             """

```

## Test Information

**Tests that should FAIL→PASS**: ["testing/test_junitxml.py::TestPython::test_hostname_in_xml", "testing/test_junitxml.py::TestPython::test_timestamp_in_xml"]

**Tests that should PASS→PASS**: ["testing/test_junitxml.py::test_mangle_test_address", "testing/test_junitxml.py::test_dont_configure_on_slaves", "testing/test_junitxml.py::test_invalid_xml_escape", "testing/test_junitxml.py::test_logxml_path_expansion", "testing/test_junitxml.py::TestPython::test_summing_simple", "testing/test_junitxml.py::TestPython::test_summing_simple_with_errors", "testing/test_junitxml.py::TestPython::test_timing_function", "testing/test_junitxml.py::TestPython::test_junit_duration_report[call]", "testing/test_junitxml.py::TestPython::test_junit_duration_report[total]", "testing/test_junitxml.py::TestPython::test_setup_error", "testing/test_junitxml.py::TestPython::test_teardown_error", "testing/test_junitxml.py::TestPython::test_call_failure_teardown_error", "testing/test_junitxml.py::TestPython::test_skip_contains_name_reason", "testing/test_junitxml.py::TestPython::test_mark_skip_contains_name_reason", "testing/test_junitxml.py::TestPython::test_mark_skipif_contains_name_reason", "testing/test_junitxml.py::TestPython::test_mark_skip_doesnt_capture_output", "testing/test_junitxml.py::TestPython::test_classname_instance", "testing/test_junitxml.py::TestPython::test_classname_nested_dir", "testing/test_junitxml.py::TestPython::test_internal_error", "testing/test_junitxml.py::TestPython::test_failure_function[no]", "testing/test_junitxml.py::TestPython::test_failure_function[system-out]", "testing/test_junitxml.py::TestPython::test_failure_function[system-err]", "testing/test_junitxml.py::TestPython::test_failure_verbose_message", "testing/test_junitxml.py::TestPython::test_failure_escape", "testing/test_junitxml.py::TestPython::test_junit_prefixing", "testing/test_junitxml.py::TestPython::test_xfailure_function", "testing/test_junitxml.py::TestPython::test_xfailure_marker", "testing/test_junitxml.py::TestPython::test_xfail_captures_output_once", "testing/test_junitxml.py::TestPython::test_xfailure_xpass", "testing/test_junitxml.py::TestPython::test_xfailure_xpass_strict", "testing/test_junitxml.py::TestPython::test_collect_error", "testing/test_junitxml.py::TestPython::test_unicode", "testing/test_junitxml.py::TestPython::test_assertion_binchars", "testing/test_junitxml.py::TestPython::test_pass_captures_stdout", "testing/test_junitxml.py::TestPython::test_pass_captures_stderr", "testing/test_junitxml.py::TestPython::test_setup_error_captures_stdout", "testing/test_junitxml.py::TestPython::test_setup_error_captures_stderr", "testing/test_junitxml.py::TestPython::test_avoid_double_stdout", "testing/test_junitxml.py::TestNonPython::test_summing_simple", "testing/test_junitxml.py::test_nullbyte", "testing/test_junitxml.py::test_nullbyte_replace", "testing/test_junitxml.py::test_logxml_changingdir", "testing/test_junitxml.py::test_logxml_makedir", "testing/test_junitxml.py::test_logxml_check_isdir", "testing/test_junitxml.py::test_escaped_parametrized_names_xml", "testing/test_junitxml.py::test_double_colon_split_function_issue469", "testing/test_junitxml.py::test_double_colon_split_method_issue469", "testing/test_junitxml.py::test_unicode_issue368", "testing/test_junitxml.py::test_record_property", "testing/test_junitxml.py::test_record_property_same_name", "testing/test_junitxml.py::test_record_fixtures_without_junitxml[record_property]", "testing/test_junitxml.py::test_record_fixtures_without_junitxml[record_xml_attribute]", "testing/test_junitxml.py::test_record_attribute", "testing/test_junitxml.py::test_record_fixtures_xunit2[record_xml_attribute]", "testing/test_junitxml.py::test_record_fixtures_xunit2[record_property]", "testing/test_junitxml.py::test_root_testsuites_tag", "testing/test_junitxml.py::test_runs_twice", "testing/test_junitxml.py::test_fancy_items_regression", "testing/test_junitxml.py::test_global_properties", "testing/test_junitxml.py::test_url_property", "testing/test_junitxml.py::test_record_testsuite_property", "testing/test_junitxml.py::test_record_testsuite_property_junit_disabled", "testing/test_junitxml.py::test_record_testsuite_property_type_checking[True]", "testing/test_junitxml.py::test_record_testsuite_property_type_checking[False]", "testing/test_junitxml.py::test_set_suite_name[my_suite]", "testing/test_junitxml.py::test_set_suite_name[]", "testing/test_junitxml.py::test_escaped_skipreason_issue3533", "testing/test_junitxml.py::test_logging_passing_tests_disabled_does_not_log_test_output"]

**Base Commit**: 29e336bd9bf87eaef8e2683196ee1975f1ad4088
**Environment Setup Commit**: c2f762460f4c42547de906d53ea498dd499ea837
