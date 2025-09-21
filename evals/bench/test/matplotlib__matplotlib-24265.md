# matplotlib__matplotlib-24265

**Repository**: matplotlib/matplotlib
**Created**: 2022-10-25T02:03:19Z
**Version**: 3.6

## Problem Statement

[Bug]: Setting matplotlib.pyplot.style.library['seaborn-colorblind'] result in key error on matplotlib v3.6.1
### Bug summary

I have code that executes:
```
import matplotlib.pyplot as plt
the_rc = plt.style.library["seaborn-colorblind"]
```

Using version 3.4.3 of matplotlib, this works fine. I recently installed my code on a machine with matplotlib version 3.6.1 and upon importing my code, this generated a key error for line `the_rc = plt.style.library["seaborn-colorblind"]` saying "seaborn-colorblind" was a bad key.

### Code for reproduction

```python
import matplotlib.pyplot as plt
the_rc = plt.style.library["seaborn-colorblind"]
```


### Actual outcome

Traceback (most recent call last):
KeyError: 'seaborn-colorblind'

### Expected outcome

seaborn-colorblind should be set as the matplotlib library style and I should be able to continue plotting with that style.

### Additional information

- Bug occurs with matplotlib version 3.6.1
- Bug does not occur with matplotlib version 3.4.3
- Tested on MacOSX and Ubuntu (same behavior on both)

### Operating system

OS/X

### Matplotlib Version

3.6.1

### Matplotlib Backend

MacOSX

### Python version

3.9.7

### Jupyter version

_No response_

### Installation

pip


## Patch

```diff

diff --git a/lib/matplotlib/style/core.py b/lib/matplotlib/style/core.py
--- a/lib/matplotlib/style/core.py
+++ b/lib/matplotlib/style/core.py
@@ -43,6 +43,32 @@ class __getattr__:
     'toolbar', 'timezone', 'figure.max_open_warning',
     'figure.raise_window', 'savefig.directory', 'tk.window_focus',
     'docstring.hardcopy', 'date.epoch'}
+_DEPRECATED_SEABORN_STYLES = {
+    s: s.replace("seaborn", "seaborn-v0_8")
+    for s in [
+        "seaborn",
+        "seaborn-bright",
+        "seaborn-colorblind",
+        "seaborn-dark",
+        "seaborn-darkgrid",
+        "seaborn-dark-palette",
+        "seaborn-deep",
+        "seaborn-muted",
+        "seaborn-notebook",
+        "seaborn-paper",
+        "seaborn-pastel",
+        "seaborn-poster",
+        "seaborn-talk",
+        "seaborn-ticks",
+        "seaborn-white",
+        "seaborn-whitegrid",
+    ]
+}
+_DEPRECATED_SEABORN_MSG = (
+    "The seaborn styles shipped by Matplotlib are deprecated since %(since)s, "
+    "as they no longer correspond to the styles shipped by seaborn. However, "
+    "they will remain available as 'seaborn-v0_8-<style>'. Alternatively, "
+    "directly use the seaborn API instead.")
 
 
 def _remove_blacklisted_style_params(d, warn=True):
@@ -113,31 +139,9 @@ def use(style):
     def fix_style(s):
         if isinstance(s, str):
             s = style_alias.get(s, s)
-            if s in [
-                "seaborn",
-                "seaborn-bright",
-                "seaborn-colorblind",
-                "seaborn-dark",
-                "seaborn-darkgrid",
-                "seaborn-dark-palette",
-                "seaborn-deep",
-                "seaborn-muted",
-                "seaborn-notebook",
-                "seaborn-paper",
-                "seaborn-pastel",
-                "seaborn-poster",
-                "seaborn-talk",
-                "seaborn-ticks",
-                "seaborn-white",
-                "seaborn-whitegrid",
-            ]:
-                _api.warn_deprecated(
-                    "3.6", message="The seaborn styles shipped by Matplotlib "
-                    "are deprecated since %(since)s, as they no longer "
-                    "correspond to the styles shipped by seaborn. However, "
-                    "they will remain available as 'seaborn-v0_8-<style>'. "
-                    "Alternatively, directly use the seaborn API instead.")
-                s = s.replace("seaborn", "seaborn-v0_8")
+            if s in _DEPRECATED_SEABORN_STYLES:
+                _api.warn_deprecated("3.6", message=_DEPRECATED_SEABORN_MSG)
+                s = _DEPRECATED_SEABORN_STYLES[s]
         return s
 
     for style in map(fix_style, styles):
@@ -244,17 +248,26 @@ def update_nested_dict(main_dict, new_dict):
     return main_dict
 
 
+class _StyleLibrary(dict):
+    def __getitem__(self, key):
+        if key in _DEPRECATED_SEABORN_STYLES:
+            _api.warn_deprecated("3.6", message=_DEPRECATED_SEABORN_MSG)
+            key = _DEPRECATED_SEABORN_STYLES[key]
+
+        return dict.__getitem__(self, key)
+
+
 # Load style library
 # ==================
 _base_library = read_style_directory(BASE_LIBRARY_PATH)
-library = None
+library = _StyleLibrary()
 available = []
 
 
 def reload_library():
     """Reload the style library."""
-    global library
-    library = update_user_library(_base_library)
+    library.clear()
+    library.update(update_user_library(_base_library))
     available[:] = sorted(library.keys())
 
 


```

## Test Patch

```diff
diff --git a/lib/matplotlib/tests/test_style.py b/lib/matplotlib/tests/test_style.py
--- a/lib/matplotlib/tests/test_style.py
+++ b/lib/matplotlib/tests/test_style.py
@@ -184,6 +184,8 @@ def test_deprecated_seaborn_styles():
     with pytest.warns(mpl._api.MatplotlibDeprecationWarning):
         mpl.style.use("seaborn-bright")
     assert mpl.rcParams == seaborn_bright
+    with pytest.warns(mpl._api.MatplotlibDeprecationWarning):
+        mpl.style.library["seaborn-bright"]
 
 
 def test_up_to_date_blacklist():

```

## Test Information

**Tests that should FAIL→PASS**: ["lib/matplotlib/tests/test_style.py::test_deprecated_seaborn_styles"]

**Tests that should PASS→PASS**: ["lib/matplotlib/tests/test_style.py::test_invalid_rc_warning_includes_filename", "lib/matplotlib/tests/test_style.py::test_available", "lib/matplotlib/tests/test_style.py::test_use", "lib/matplotlib/tests/test_style.py::test_use_url", "lib/matplotlib/tests/test_style.py::test_single_path", "lib/matplotlib/tests/test_style.py::test_context", "lib/matplotlib/tests/test_style.py::test_context_with_dict", "lib/matplotlib/tests/test_style.py::test_context_with_dict_after_namedstyle", "lib/matplotlib/tests/test_style.py::test_context_with_dict_before_namedstyle", "lib/matplotlib/tests/test_style.py::test_context_with_union_of_dict_and_namedstyle", "lib/matplotlib/tests/test_style.py::test_context_with_badparam", "lib/matplotlib/tests/test_style.py::test_alias[mpl20]", "lib/matplotlib/tests/test_style.py::test_alias[mpl15]", "lib/matplotlib/tests/test_style.py::test_xkcd_no_cm", "lib/matplotlib/tests/test_style.py::test_xkcd_cm", "lib/matplotlib/tests/test_style.py::test_up_to_date_blacklist"]

**Base Commit**: e148998d9bed9d1b53a91587ad48f9bb43c7737f
**Environment Setup Commit**: 73909bcb408886a22e2b84581d6b9e6d9907c813
