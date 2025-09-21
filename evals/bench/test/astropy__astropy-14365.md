# astropy__astropy-14365

**Repository**: astropy/astropy
**Created**: 2023-02-06T19:20:34Z
**Version**: 5.1

## Problem Statement

ascii.qdp Table format assumes QDP commands are upper case
### Description

ascii.qdp assumes that commands in a QDP file are upper case, for example, for errors they must be "READ SERR 1 2" whereas QDP itself is not case sensitive and case use "read serr 1 2". 

As many QDP files are created by hand, the expectation that all commands be all-caps should be removed.

### Expected behavior

The following qdp file should read into a `Table` with errors, rather than crashing.
```
read serr 1 2 
1 0.5 1 0.5
```

### How to Reproduce

Create a QDP file:
```
> cat > test.qdp
read serr 1 2 
1 0.5 1 0.5
<EOF>

 > python
Python 3.10.9 (main, Dec  7 2022, 02:03:23) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from astropy.table import Table
>>> Table.read('test.qdp',format='ascii.qdp')
WARNING: table_id not specified. Reading the first available table [astropy.io.ascii.qdp]
Traceback (most recent call last):
...
    raise ValueError(f'Unrecognized QDP line: {line}')
ValueError: Unrecognized QDP line: read serr 1 2
```

Running "qdp test.qdp" works just fine.


### Versions

Python 3.10.9 (main, Dec  7 2022, 02:03:23) [Clang 13.0.0 (clang-1300.0.29.30)]
astropy 5.1
Numpy 1.24.1
pyerfa 2.0.0.1
Scipy 1.10.0
Matplotlib 3.6.3



## Hints

Welcome to Astropy 👋 and thank you for your first issue!

A project member will respond to you as soon as possible; in the meantime, please double-check the [guidelines for submitting issues](https://github.com/astropy/astropy/blob/main/CONTRIBUTING.md#reporting-issues) and make sure you've provided the requested details.

GitHub issues in the Astropy repository are used to track bug reports and feature requests; If your issue poses a question about how to use Astropy, please instead raise your question in the [Astropy Discourse user forum](https://community.openastronomy.org/c/astropy/8) and close this issue.

If you feel that this issue has not been responded to in a timely manner, please send a message directly to the [development mailing list](http://groups.google.com/group/astropy-dev).  If the issue is urgent or sensitive in nature (e.g., a security vulnerability) please send an e-mail directly to the private e-mail feedback@astropy.org.
Huh, so we do have this format... https://docs.astropy.org/en/stable/io/ascii/index.html

@taldcroft , you know anything about this?
This is the format I'm using, which has the issue: https://docs.astropy.org/en/stable/api/astropy.io.ascii.QDP.html

The issue is that the regex that searches for QDP commands is not case insensitive. 

This attached patch fixes the issue, but I'm sure there's a better way of doing it.

[qdp.patch](https://github.com/astropy/astropy/files/10667923/qdp.patch)

@jak574 - the fix is probably as simple as that. Would you like to put in a bugfix PR?

## Patch

```diff

diff --git a/astropy/io/ascii/qdp.py b/astropy/io/ascii/qdp.py
--- a/astropy/io/ascii/qdp.py
+++ b/astropy/io/ascii/qdp.py
@@ -68,7 +68,7 @@ def _line_type(line, delimiter=None):
     _new_re = rf"NO({sep}NO)+"
     _data_re = rf"({_decimal_re}|NO|[-+]?nan)({sep}({_decimal_re}|NO|[-+]?nan))*)"
     _type_re = rf"^\s*((?P<command>{_command_re})|(?P<new>{_new_re})|(?P<data>{_data_re})?\s*(\!(?P<comment>.*))?\s*$"
-    _line_type_re = re.compile(_type_re)
+    _line_type_re = re.compile(_type_re, re.IGNORECASE)
     line = line.strip()
     if not line:
         return "comment"
@@ -306,7 +306,7 @@ def _get_tables_from_qdp_file(qdp_file, input_colnames=None, delimiter=None):
 
             values = []
             for v in line.split(delimiter):
-                if v == "NO":
+                if v.upper() == "NO":
                     values.append(np.ma.masked)
                 else:
                     # Understand if number is int or float


```

## Test Patch

```diff
diff --git a/astropy/io/ascii/tests/test_qdp.py b/astropy/io/ascii/tests/test_qdp.py
--- a/astropy/io/ascii/tests/test_qdp.py
+++ b/astropy/io/ascii/tests/test_qdp.py
@@ -43,7 +43,18 @@ def test_get_tables_from_qdp_file(tmp_path):
     assert np.isclose(table2["MJD_nerr"][0], -2.37847222222222e-05)
 
 
-def test_roundtrip(tmp_path):
+def lowercase_header(value):
+    """Make every non-comment line lower case."""
+    lines = []
+    for line in value.splitlines():
+        if not line.startswith("!"):
+            line = line.lower()
+        lines.append(line)
+    return "\n".join(lines)
+
+
+@pytest.mark.parametrize("lowercase", [False, True])
+def test_roundtrip(tmp_path, lowercase):
     example_qdp = """
     ! Swift/XRT hardness ratio of trigger: XXXX, name: BUBU X-2
     ! Columns are as labelled
@@ -70,6 +81,8 @@ def test_roundtrip(tmp_path):
     53000.123456 2.37847222222222e-05    -2.37847222222222e-05   -0.292553       -0.374935
     NO 1.14467592592593e-05    -1.14467592592593e-05   0.000000        NO
     """
+    if lowercase:
+        example_qdp = lowercase_header(example_qdp)
 
     path = str(tmp_path / "test.qdp")
     path2 = str(tmp_path / "test2.qdp")

```

## Test Information

**Tests that should FAIL→PASS**: ["astropy/io/ascii/tests/test_qdp.py::test_roundtrip[True]"]

**Tests that should PASS→PASS**: ["astropy/io/ascii/tests/test_qdp.py::test_get_tables_from_qdp_file", "astropy/io/ascii/tests/test_qdp.py::test_roundtrip[False]", "astropy/io/ascii/tests/test_qdp.py::test_read_example", "astropy/io/ascii/tests/test_qdp.py::test_roundtrip_example", "astropy/io/ascii/tests/test_qdp.py::test_roundtrip_example_comma", "astropy/io/ascii/tests/test_qdp.py::test_read_write_simple", "astropy/io/ascii/tests/test_qdp.py::test_read_write_simple_specify_name", "astropy/io/ascii/tests/test_qdp.py::test_get_lines_from_qdp"]

**Base Commit**: 7269fa3e33e8d02485a647da91a5a2a60a06af61
**Environment Setup Commit**: 5f74eacbcc7fff707a44d8eb58adaa514cb7dcb5
