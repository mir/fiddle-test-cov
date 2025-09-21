# pallets__flask-4992

**Repository**: pallets/flask
**Created**: 2023-02-22T14:00:17Z
**Version**: 2.3

## Problem Statement

Add a file mode parameter to flask.Config.from_file()
Python 3.11 introduced native TOML support with the `tomllib` package. This could work nicely with the `flask.Config.from_file()` method as an easy way to load TOML config files:

```python
app.config.from_file("config.toml", tomllib.load)
```

However, `tomllib.load()` takes an object readable in binary mode, while `flask.Config.from_file()` opens a file in text mode, resulting in this error:

```
TypeError: File must be opened in binary mode, e.g. use `open('foo.toml', 'rb')`
```

We can get around this with a more verbose expression, like loading from a file opened with the built-in `open()` function and passing the `dict` to `app.Config.from_mapping()`:

```python
# We have to repeat the path joining that from_file() does
with open(os.path.join(app.config.root_path, "config.toml"), "rb") as file:
    app.config.from_mapping(tomllib.load(file))
```

But adding a file mode parameter to `flask.Config.from_file()` would enable the use of a simpler expression. E.g.:

```python
app.config.from_file("config.toml", tomllib.load, mode="b")
```



## Hints

You can also use:

```python
app.config.from_file("config.toml", lambda f: tomllib.load(f.buffer))
```
Thanks - I was looking for another way to do it. I'm happy with that for now, although it's worth noting this about `io.TextIOBase.buffer` from the docs:

> This is not part of the [TextIOBase](https://docs.python.org/3/library/io.html#io.TextIOBase) API and may not exist in some implementations.
Oh, didn't mean for you to close this, that was just a shorter workaround. I think a `text=True` parameter would be better, easier to use `True` or `False` rather than mode strings. Some libraries, like `tomllib`, have _Opinions_ about whether text or bytes are correct for parsing files, and we can accommodate that.
can i work on this?
No need to ask to work on an issue. As long as the issue is not assigned to anyone and doesn't have have a linked open PR (both can be seen in the sidebar), anyone is welcome to work on any issue.

## Patch

```diff

diff --git a/src/flask/config.py b/src/flask/config.py
--- a/src/flask/config.py
+++ b/src/flask/config.py
@@ -234,6 +234,7 @@ def from_file(
         filename: str,
         load: t.Callable[[t.IO[t.Any]], t.Mapping],
         silent: bool = False,
+        text: bool = True,
     ) -> bool:
         """Update the values in the config from a file that is loaded
         using the ``load`` parameter. The loaded data is passed to the
@@ -244,8 +245,8 @@ def from_file(
             import json
             app.config.from_file("config.json", load=json.load)
 
-            import toml
-            app.config.from_file("config.toml", load=toml.load)
+            import tomllib
+            app.config.from_file("config.toml", load=tomllib.load, text=False)
 
         :param filename: The path to the data file. This can be an
             absolute path or relative to the config root path.
@@ -254,14 +255,18 @@ def from_file(
         :type load: ``Callable[[Reader], Mapping]`` where ``Reader``
             implements a ``read`` method.
         :param silent: Ignore the file if it doesn't exist.
+        :param text: Open the file in text or binary mode.
         :return: ``True`` if the file was loaded successfully.
 
+        .. versionchanged:: 2.3
+            The ``text`` parameter was added.
+
         .. versionadded:: 2.0
         """
         filename = os.path.join(self.root_path, filename)
 
         try:
-            with open(filename) as f:
+            with open(filename, "r" if text else "rb") as f:
                 obj = load(f)
         except OSError as e:
             if silent and e.errno in (errno.ENOENT, errno.EISDIR):


```

## Test Patch

```diff
diff --git a/tests/static/config.toml b/tests/static/config.toml
new file mode 100644
--- /dev/null
+++ b/tests/static/config.toml
@@ -0,0 +1,2 @@
+TEST_KEY="foo"
+SECRET_KEY="config"
diff --git a/tests/test_config.py b/tests/test_config.py
--- a/tests/test_config.py
+++ b/tests/test_config.py
@@ -6,7 +6,6 @@
 
 import flask
 
-
 # config keys used for the TestConfig
 TEST_KEY = "foo"
 SECRET_KEY = "config"
@@ -30,13 +29,23 @@ def test_config_from_object():
     common_object_test(app)
 
 
-def test_config_from_file():
+def test_config_from_file_json():
     app = flask.Flask(__name__)
     current_dir = os.path.dirname(os.path.abspath(__file__))
     app.config.from_file(os.path.join(current_dir, "static", "config.json"), json.load)
     common_object_test(app)
 
 
+def test_config_from_file_toml():
+    tomllib = pytest.importorskip("tomllib", reason="tomllib added in 3.11")
+    app = flask.Flask(__name__)
+    current_dir = os.path.dirname(os.path.abspath(__file__))
+    app.config.from_file(
+        os.path.join(current_dir, "static", "config.toml"), tomllib.load, text=False
+    )
+    common_object_test(app)
+
+
 def test_from_prefixed_env(monkeypatch):
     monkeypatch.setenv("FLASK_STRING", "value")
     monkeypatch.setenv("FLASK_BOOL", "true")

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/test_config.py::test_config_from_file_toml"]

**Tests that should PASS→PASS**: ["tests/test_config.py::test_config_from_pyfile", "tests/test_config.py::test_config_from_object", "tests/test_config.py::test_config_from_file_json", "tests/test_config.py::test_from_prefixed_env", "tests/test_config.py::test_from_prefixed_env_custom_prefix", "tests/test_config.py::test_from_prefixed_env_nested", "tests/test_config.py::test_config_from_mapping", "tests/test_config.py::test_config_from_class", "tests/test_config.py::test_config_from_envvar", "tests/test_config.py::test_config_from_envvar_missing", "tests/test_config.py::test_config_missing", "tests/test_config.py::test_config_missing_file", "tests/test_config.py::test_custom_config_class", "tests/test_config.py::test_session_lifetime", "tests/test_config.py::test_get_namespace", "tests/test_config.py::test_from_pyfile_weird_encoding[utf-8]", "tests/test_config.py::test_from_pyfile_weird_encoding[iso-8859-15]", "tests/test_config.py::test_from_pyfile_weird_encoding[latin-1]"]

**Base Commit**: 4c288bc97ea371817199908d0d9b12de9dae327e
**Environment Setup Commit**: 182ce3dd15dfa3537391c3efaf9c3ff407d134d4
