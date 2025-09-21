# pytest-dev__pytest-5413

**Repository**: pytest-dev/pytest
**Created**: 2019-06-06T15:21:20Z
**Version**: 4.6

## Problem Statement

str() on the pytest.raises context variable doesn't behave same as normal exception catch
Pytest 4.6.2, macOS 10.14.5

```Python
try:
    raise LookupError(
        f"A\n"
        f"B\n"
        f"C"
    )
except LookupError as e:
    print(str(e))
```
prints

> A
> B
> C

But

```Python
with pytest.raises(LookupError) as e:
    raise LookupError(
        f"A\n"
        f"B\n"
        f"C"
    )

print(str(e))
```

prints

> <console>:3: LookupError: A

In order to get the full error message, one must do `str(e.value)`, which is documented, but this is a different interaction. Any chance the behavior could be changed to eliminate this gotcha?

-----

Pip list gives

```
Package            Version  Location
------------------ -------- ------------------------------------------------------
apipkg             1.5
asn1crypto         0.24.0
atomicwrites       1.3.0
attrs              19.1.0
aws-xray-sdk       0.95
boto               2.49.0
boto3              1.9.51
botocore           1.12.144
certifi            2019.3.9
cffi               1.12.3
chardet            3.0.4
Click              7.0
codacy-coverage    1.3.11
colorama           0.4.1
coverage           4.5.3
cryptography       2.6.1
decorator          4.4.0
docker             3.7.2
docker-pycreds     0.4.0
docutils           0.14
ecdsa              0.13.2
execnet            1.6.0
future             0.17.1
idna               2.8
importlib-metadata 0.17
ipaddress          1.0.22
Jinja2             2.10.1
jmespath           0.9.4
jsondiff           1.1.1
jsonpickle         1.1
jsonschema         2.6.0
MarkupSafe         1.1.1
mock               3.0.4
more-itertools     7.0.0
moto               1.3.7
neobolt            1.7.10
neotime            1.7.4
networkx           2.1
numpy              1.15.0
packaging          19.0
pandas             0.24.2
pip                19.1.1
pluggy             0.12.0
prompt-toolkit     2.0.9
py                 1.8.0
py2neo             4.2.0
pyaml              19.4.1
pycodestyle        2.5.0
pycparser          2.19
pycryptodome       3.8.1
Pygments           2.3.1
pyOpenSSL          19.0.0
pyparsing          2.4.0
pytest             4.6.2
pytest-cache       1.0
pytest-codestyle   1.4.0
pytest-cov         2.6.1
pytest-forked      1.0.2
python-dateutil    2.7.3
python-jose        2.0.2
pytz               2018.5
PyYAML             5.1
requests           2.21.0
requests-mock      1.5.2
responses          0.10.6
s3transfer         0.1.13
setuptools         41.0.1
six                1.11.0
sqlite3worker      1.1.7
tabulate           0.8.3
urllib3            1.24.3
wcwidth            0.1.7
websocket-client   0.56.0
Werkzeug           0.15.2
wheel              0.33.1
wrapt              1.11.1
xlrd               1.1.0
xmltodict          0.12.0
zipp               0.5.1
```


## Hints

> Any chance the behavior could be changed to eliminate this gotcha?

What do you suggest?

Proxying through to the exceptions `__str__`?
Hi @fiendish,

Indeed this is a bit confusing.

Currently `ExceptionInfo` objects (which is `pytest.raises` returns to the context manager) implements `__str__` like this:

https://github.com/pytest-dev/pytest/blob/9f8b566ea976df3a3ea16f74b56dd6d4909b84ee/src/_pytest/_code/code.py#L537-L542

I don't see much use for this, I would rather it didn't implement `__str__` at all and let `__repr__` take over, which would show something like:

```
<ExceptionInfo LookupError tb=10>
```

Which makes it more obvious that this is not what the user intended with `str(e)` probably.

So I think a good solution is to simply delete the `__str__` method.

Thoughts?

Also, @fiendish which Python version are you using?
> So I think a good solution is to simply delete the `__str__` method.

Makes sense to me.


Python 3.7.3

My ideal outcome would be for str(e) to act the same as str(e.value), but I can understand if that isn't desired.
> My ideal outcome would be for str(e) to act the same as str(e.value), but I can understand if that isn't desired.

I understand, but I think it is better to be explicit here, because users might use `print(e)` to see what `e` is, assume it is the exception value, and then get confused later when it actually isn't (an `isinstance` check or accessing `e.args`).
+1 for deleting the current `__str__` implementation
-1 for proxying it to the underlying `e.value`

the `ExceptionInfo` object is not the exception and anything that makes it look more like the exception is just going to add to the confusion

## Patch

```diff

diff --git a/src/_pytest/_code/code.py b/src/_pytest/_code/code.py
--- a/src/_pytest/_code/code.py
+++ b/src/_pytest/_code/code.py
@@ -534,13 +534,6 @@ def getrepr(
         )
         return fmt.repr_excinfo(self)
 
-    def __str__(self):
-        if self._excinfo is None:
-            return repr(self)
-        entry = self.traceback[-1]
-        loc = ReprFileLocation(entry.path, entry.lineno + 1, self.exconly())
-        return str(loc)
-
     def match(self, regexp):
         """
         Check whether the regular expression 'regexp' is found in the string


```

## Test Patch

```diff
diff --git a/testing/code/test_excinfo.py b/testing/code/test_excinfo.py
--- a/testing/code/test_excinfo.py
+++ b/testing/code/test_excinfo.py
@@ -333,18 +333,10 @@ def test_excinfo_exconly():
     assert msg.endswith("world")
 
 
-def test_excinfo_repr():
+def test_excinfo_repr_str():
     excinfo = pytest.raises(ValueError, h)
-    s = repr(excinfo)
-    assert s == "<ExceptionInfo ValueError tblen=4>"
-
-
-def test_excinfo_str():
-    excinfo = pytest.raises(ValueError, h)
-    s = str(excinfo)
-    assert s.startswith(__file__[:-9])  # pyc file and $py.class
-    assert s.endswith("ValueError")
-    assert len(s.split(":")) >= 3  # on windows it's 4
+    assert repr(excinfo) == "<ExceptionInfo ValueError tblen=4>"
+    assert str(excinfo) == "<ExceptionInfo ValueError tblen=4>"
 
 
 def test_excinfo_for_later():

```

## Test Information

**Tests that should FAIL→PASS**: ["testing/code/test_excinfo.py::test_excinfo_repr_str"]

**Tests that should PASS→PASS**: ["testing/code/test_excinfo.py::test_excinfo_simple", "testing/code/test_excinfo.py::test_excinfo_getstatement", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_entries", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_entry_getsource", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_entry_getsource_in_construct", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_cut", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_filter", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_filter_selective[<lambda>-True]", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_filter_selective[<lambda>-False]", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_filter_selective[tracebackhide2-True]", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_filter_selective[tracebackhide3-False]", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_recursion_index", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_only_specific_recursion_errors", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_no_recursion_index", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_getcrashentry", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_getcrashentry_empty", "testing/code/test_excinfo.py::test_excinfo_exconly", "testing/code/test_excinfo.py::test_excinfo_for_later", "testing/code/test_excinfo.py::test_excinfo_errisinstance", "testing/code/test_excinfo.py::test_excinfo_no_sourcecode", "testing/code/test_excinfo.py::test_entrysource_Queue_example", "testing/code/test_excinfo.py::test_codepath_Queue_example", "testing/code/test_excinfo.py::test_match_succeeds", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_source", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_source_excinfo", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_source_not_existing", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_many_line_source_not_existing", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_source_failing_fullsource", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_local", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_local_with_error", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_local_with_exception_in_class_property", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_local_truncated", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_tracebackentry_lines", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_tracebackentry_lines2", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_tracebackentry_lines_var_kw_args", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_tracebackentry_short", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_tracebackentry_no", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_traceback_tbfilter", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_traceback_short_no_source", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_traceback_and_excinfo", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_traceback_with_invalid_cwd", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_excinfo_addouterr", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_excinfo_reprcrash", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_repr_traceback_recursion", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_reprexcinfo_getrepr", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_reprexcinfo_unicode", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_toterminal_long", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_toterminal_long_missing_source", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_toterminal_long_incomplete_source", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_toterminal_long_filenames", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions0]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions1]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions2]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions3]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions4]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions5]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions6]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions7]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions8]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions9]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions10]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions11]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions12]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions13]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions14]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions15]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions16]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions17]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions18]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions19]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions20]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions21]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions22]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_format_excinfo[reproptions23]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_traceback_repr_style", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_exc_chain_repr", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_exc_repr_chain_suppression[from_none]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_exc_repr_chain_suppression[explicit_suppress]", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_exc_chain_repr_without_traceback[cause-The", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_exc_chain_repr_without_traceback[context-During", "testing/code/test_excinfo.py::TestFormattedExcinfo::test_exc_chain_repr_cycle", "testing/code/test_excinfo.py::test_repr_traceback_with_unicode[None-short]", "testing/code/test_excinfo.py::test_repr_traceback_with_unicode[None-long]", "testing/code/test_excinfo.py::test_repr_traceback_with_unicode[utf8-short]", "testing/code/test_excinfo.py::test_repr_traceback_with_unicode[utf8-long]", "testing/code/test_excinfo.py::test_repr_traceback_with_unicode[utf16-short]", "testing/code/test_excinfo.py::test_repr_traceback_with_unicode[utf16-long]", "testing/code/test_excinfo.py::test_exception_repr_extraction_error_on_recursion", "testing/code/test_excinfo.py::test_no_recursion_index_on_recursion_error", "testing/code/test_excinfo.py::TestTraceback_f_g_h::test_traceback_cut_excludepath", "testing/code/test_excinfo.py::test_match_raises_error", "testing/code/test_excinfo.py::test_cwd_deleted"]

**Base Commit**: 450d2646233c670654744d3d24330b69895bb9d2
**Environment Setup Commit**: d5843f89d3c008ddcb431adbc335b080a79e617e
