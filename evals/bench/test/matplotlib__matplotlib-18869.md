# matplotlib__matplotlib-18869

**Repository**: matplotlib/matplotlib
**Created**: 2020-11-01T23:18:42Z
**Version**: 3.3

## Problem Statement

Add easily comparable version info to toplevel
<!--
Welcome! Thanks for thinking of a way to improve Matplotlib.


Before creating a new feature request please search the issues for relevant feature requests.
-->

### Problem

Currently matplotlib only exposes `__version__`.  For quick version checks, exposing either a `version_info` tuple (which can be compared with other tuples) or a `LooseVersion` instance (which can be properly compared with other strings) would be a small usability improvement.

(In practice I guess boring string comparisons will work just fine until we hit mpl 3.10 or 4.10 which is unlikely to happen soon, but that feels quite dirty :))
<!--
Provide a clear and concise description of the problem this feature will solve. 

For example:
* I'm always frustrated when [...] because [...]
* I would like it if [...] happened when I [...] because [...]
* Here is a sample image of what I am asking for [...]
-->

### Proposed Solution

I guess I slightly prefer `LooseVersion`, but exposing just a `version_info` tuple is much more common in other packages (and perhaps simpler to understand).  The hardest(?) part is probably just bikeshedding this point :-)
<!-- Provide a clear and concise description of a way to accomplish what you want. For example:

* Add an option so that when [...]  [...] will happen
 -->

### Additional context and prior art

`version_info` is a pretty common thing (citation needed).
<!-- Add any other context or screenshots about the feature request here. You can also include links to examples of other programs that have something similar to your request. For example:

* Another project [...] solved this by [...]
-->



## Hints

It seems that `__version_info__` is the way to go.

### Prior art
- There's no official specification for version tuples. [PEP 396 - Module Version Numbers](https://www.python.org/dev/peps/pep-0396/) only defines the string `__version__`.

- Many projects don't bother with version tuples.

- When they do, `__version_info__` seems to be a common thing:
  - [Stackoverflow discussion](https://stackoverflow.com/a/466694)
  - [PySide2](https://doc.qt.io/qtforpython-5.12/pysideversion.html#printing-project-and-qt-version) uses it.

- Python itself has the string [sys.version](https://docs.python.org/3/library/sys.html#sys.version) and the (named)tuple [sys.version_info](https://docs.python.org/3/library/sys.html#sys.version_info). In analogy to that `__version_info__` next to `__version__` makes sense for packages.


## Patch

```diff

diff --git a/lib/matplotlib/__init__.py b/lib/matplotlib/__init__.py
--- a/lib/matplotlib/__init__.py
+++ b/lib/matplotlib/__init__.py
@@ -129,25 +129,60 @@
   year      = 2007
 }"""
 
+# modelled after sys.version_info
+_VersionInfo = namedtuple('_VersionInfo',
+                          'major, minor, micro, releaselevel, serial')
 
-def __getattr__(name):
-    if name == "__version__":
+
+def _parse_to_version_info(version_str):
+    """
+    Parse a version string to a namedtuple analogous to sys.version_info.
+
+    See:
+    https://packaging.pypa.io/en/latest/version.html#packaging.version.parse
+    https://docs.python.org/3/library/sys.html#sys.version_info
+    """
+    v = parse_version(version_str)
+    if v.pre is None and v.post is None and v.dev is None:
+        return _VersionInfo(v.major, v.minor, v.micro, 'final', 0)
+    elif v.dev is not None:
+        return _VersionInfo(v.major, v.minor, v.micro, 'alpha', v.dev)
+    elif v.pre is not None:
+        releaselevel = {
+            'a': 'alpha',
+            'b': 'beta',
+            'rc': 'candidate'}.get(v.pre[0], 'alpha')
+        return _VersionInfo(v.major, v.minor, v.micro, releaselevel, v.pre[1])
+    else:
+        # fallback for v.post: guess-next-dev scheme from setuptools_scm
+        return _VersionInfo(v.major, v.minor, v.micro + 1, 'alpha', v.post)
+
+
+def _get_version():
+    """Return the version string used for __version__."""
+    # Only shell out to a git subprocess if really needed, and not on a
+    # shallow clone, such as those used by CI, as the latter would trigger
+    # a warning from setuptools_scm.
+    root = Path(__file__).resolve().parents[2]
+    if (root / ".git").exists() and not (root / ".git/shallow").exists():
         import setuptools_scm
+        return setuptools_scm.get_version(
+            root=root,
+            version_scheme="post-release",
+            local_scheme="node-and-date",
+            fallback_version=_version.version,
+        )
+    else:  # Get the version from the _version.py setuptools_scm file.
+        return _version.version
+
+
+def __getattr__(name):
+    if name in ("__version__", "__version_info__"):
         global __version__  # cache it.
-        # Only shell out to a git subprocess if really needed, and not on a
-        # shallow clone, such as those used by CI, as the latter would trigger
-        # a warning from setuptools_scm.
-        root = Path(__file__).resolve().parents[2]
-        if (root / ".git").exists() and not (root / ".git/shallow").exists():
-            __version__ = setuptools_scm.get_version(
-                root=root,
-                version_scheme="post-release",
-                local_scheme="node-and-date",
-                fallback_version=_version.version,
-            )
-        else:  # Get the version from the _version.py setuptools_scm file.
-            __version__ = _version.version
-        return __version__
+        __version__ = _get_version()
+        global __version__info__  # cache it.
+        __version_info__ = _parse_to_version_info(__version__)
+        return __version__ if name == "__version__" else __version_info__
     raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
 
 


```

## Test Patch

```diff
diff --git a/lib/matplotlib/tests/test_matplotlib.py b/lib/matplotlib/tests/test_matplotlib.py
--- a/lib/matplotlib/tests/test_matplotlib.py
+++ b/lib/matplotlib/tests/test_matplotlib.py
@@ -7,6 +7,16 @@
 import matplotlib
 
 
+@pytest.mark.parametrize('version_str, version_tuple', [
+    ('3.5.0', (3, 5, 0, 'final', 0)),
+    ('3.5.0rc2', (3, 5, 0, 'candidate', 2)),
+    ('3.5.0.dev820+g6768ef8c4c', (3, 5, 0, 'alpha', 820)),
+    ('3.5.0.post820+g6768ef8c4c', (3, 5, 1, 'alpha', 820)),
+])
+def test_parse_to_version_info(version_str, version_tuple):
+    assert matplotlib._parse_to_version_info(version_str) == version_tuple
+
+
 @pytest.mark.skipif(
     os.name == "nt", reason="chmod() doesn't work as is on Windows")
 @pytest.mark.skipif(os.name != "nt" and os.geteuid() == 0,

```

## Test Information

**Tests that should FAIL→PASS**: ["lib/matplotlib/tests/test_matplotlib.py::test_parse_to_version_info[3.5.0-version_tuple0]", "lib/matplotlib/tests/test_matplotlib.py::test_parse_to_version_info[3.5.0rc2-version_tuple1]", "lib/matplotlib/tests/test_matplotlib.py::test_parse_to_version_info[3.5.0.dev820+g6768ef8c4c-version_tuple2]", "lib/matplotlib/tests/test_matplotlib.py::test_parse_to_version_info[3.5.0.post820+g6768ef8c4c-version_tuple3]"]

**Tests that should PASS→PASS**: ["lib/matplotlib/tests/test_matplotlib.py::test_tmpconfigdir_warning", "lib/matplotlib/tests/test_matplotlib.py::test_importable_with_no_home", "lib/matplotlib/tests/test_matplotlib.py::test_use_doc_standard_backends", "lib/matplotlib/tests/test_matplotlib.py::test_importable_with__OO"]

**Base Commit**: b7d05919865fc0c37a0164cf467d5d5513bd0ede
**Environment Setup Commit**: 28289122be81e0bc0a6ee0c4c5b7343a46ce2e4e
