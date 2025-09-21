# pylint-dev__astroid-1333

**Repository**: pylint-dev/astroid
**Created**: 2022-01-08T19:36:45Z
**Version**: 2.10

## Problem Statement

astroid 2.9.1 breaks pylint with missing __init__.py: F0010: error while code parsing: Unable to load file __init__.py
### Steps to reproduce
> Steps provided are for Windows 11, but initial problem found in Ubuntu 20.04

> Update 2022-01-04: Corrected repro steps and added more environment details

1. Set up simple repo with following structure (all files can be empty):
```
root_dir/
|--src/
|----project/ # Notice the missing __init__.py
|------file.py # It can be empty, but I added `import os` at the top
|----__init__.py
```
2. Open a command prompt
3. `cd root_dir`
4. `python -m venv venv`
5. `venv/Scripts/activate`
6. `pip install pylint astroid==2.9.1` # I also repro'd on the latest, 2.9.2
7. `pylint src/project` # Updated from `pylint src`
8. Observe failure:
```
src\project\__init__.py:1:0: F0010: error while code parsing: Unable to load file src\project\__init__.py:
```

### Current behavior
Fails with `src\project\__init__.py:1:0: F0010: error while code parsing: Unable to load file src\project\__init__.py:`

### Expected behavior
Does not fail with error.
> If you replace step 6 with `pip install pylint astroid==2.9.0`, you get no failure with an empty output - since no files have content

### `python -c "from astroid import __pkginfo__; print(__pkginfo__.version)"` output
2.9.1

`python 3.9.1`
`pylint 2.12.2 `



This issue has been observed with astroid `2.9.1` and `2.9.2`


## Hints

I can't seem to reproduce this in my `virtualenv`. This might be specific to `venv`? Needs some further investigation.
@interifter Which version of `pylint` are you using?
Right, ``pip install pylint astroid==2.9.0``, will keep the local version if you already have one, so I thought it was ``2.12.2`` but that could be false. In fact it probably isn't 2.12.2. For the record, you're not supposed to set the version of ``astroid`` yourself, pylint does, and bad thing will happen if you try to set the version of an incompatible astroid. We might want to update the issue's template to have this information next.
My apologies... I updated the repro steps with a critical missed detail: `pylint src/project`, instead of `pylint src`

But I verified that either with, or without, `venv`, the issue is reproduced.

Also, I never have specified the `astroid` version, before. 

However, this isn't the first time the issue has been observed.
Back in early 2019, a [similar issue](https://stackoverflow.com/questions/48024049/pylint-raises-error-if-directory-doesnt-contain-init-py-file) was observed with either `astroid 2.2.0` or `isort 4.3.5`, which led me to try pinning `astroid==2.9.0`, which worked.
> @interifter Which version of `pylint` are you using?

`2.12.2`

Full env info:

```
Package           Version
----------------- -------
astroid           2.9.2
colorama          0.4.4
isort             5.10.1
lazy-object-proxy 1.7.1
mccabe            0.6.1
pip               20.2.3
platformdirs      2.4.1
pylint            2.12.2
setuptools        49.2.1
toml              0.10.2
typing-extensions 4.0.1
wrapt             1.13.3
```

I confirm the bug and i'm able to reproduce it with `python 3.9.1`. 
```
$> pip freeze
astroid==2.9.2
isort==5.10.1
lazy-object-proxy==1.7.1
mccabe==0.6.1
platformdirs==2.4.1
pylint==2.12.2
toml==0.10.2
typing-extensions==4.0.1
wrapt==1.13.3
```
Bisected and this is the faulty commit:
https://github.com/PyCQA/astroid/commit/2ee20ccdf62450db611acc4a1a7e42f407ce8a14
Fix in #1333, no time to write tests yet so if somebody has any good ideas: please let me know!

## Patch

```diff

diff --git a/astroid/modutils.py b/astroid/modutils.py
--- a/astroid/modutils.py
+++ b/astroid/modutils.py
@@ -297,6 +297,9 @@ def _get_relative_base_path(filename, path_to_check):
     if os.path.normcase(real_filename).startswith(path_to_check):
         importable_path = real_filename
 
+    # if "var" in path_to_check:
+    #     breakpoint()
+
     if importable_path:
         base_path = os.path.splitext(importable_path)[0]
         relative_base_path = base_path[len(path_to_check) :]
@@ -307,8 +310,11 @@ def _get_relative_base_path(filename, path_to_check):
 
 def modpath_from_file_with_callback(filename, path=None, is_package_cb=None):
     filename = os.path.expanduser(_path_from_filename(filename))
+    paths_to_check = sys.path.copy()
+    if path:
+        paths_to_check += path
     for pathname in itertools.chain(
-        path or [], map(_cache_normalize_path, sys.path), sys.path
+        paths_to_check, map(_cache_normalize_path, paths_to_check)
     ):
         if not pathname:
             continue


```

## Test Patch

```diff
diff --git a/tests/unittest_modutils.py b/tests/unittest_modutils.py
--- a/tests/unittest_modutils.py
+++ b/tests/unittest_modutils.py
@@ -30,6 +30,7 @@
 import tempfile
 import unittest
 import xml
+from pathlib import Path
 from xml import etree
 from xml.etree import ElementTree
 
@@ -189,6 +190,30 @@ def test_load_from_module_symlink_on_symlinked_paths_in_syspath(self) -> None:
         # this should be equivalent to: import secret
         self.assertEqual(modutils.modpath_from_file(symlink_secret_path), ["secret"])
 
+    def test_load_packages_without_init(self) -> None:
+        """Test that we correctly find packages with an __init__.py file.
+
+        Regression test for issue reported in:
+        https://github.com/PyCQA/astroid/issues/1327
+        """
+        tmp_dir = Path(tempfile.gettempdir())
+        self.addCleanup(os.chdir, os.curdir)
+        os.chdir(tmp_dir)
+
+        self.addCleanup(shutil.rmtree, tmp_dir / "src")
+        os.mkdir(tmp_dir / "src")
+        os.mkdir(tmp_dir / "src" / "package")
+        with open(tmp_dir / "src" / "__init__.py", "w", encoding="utf-8"):
+            pass
+        with open(tmp_dir / "src" / "package" / "file.py", "w", encoding="utf-8"):
+            pass
+
+        # this should be equivalent to: import secret
+        self.assertEqual(
+            modutils.modpath_from_file(str(Path("src") / "package"), ["."]),
+            ["src", "package"],
+        )
+
 
 class LoadModuleFromPathTest(resources.SysPathSetup, unittest.TestCase):
     def test_do_not_load_twice(self) -> None:

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/unittest_modutils.py::ModPathFromFileTest::test_load_packages_without_init"]

**Tests that should PASS→PASS**: ["tests/unittest_modutils.py::ModuleFileTest::test_find_egg_module", "tests/unittest_modutils.py::ModuleFileTest::test_find_zipped_module", "tests/unittest_modutils.py::LoadModuleFromNameTest::test_known_values_load_module_from_name_1", "tests/unittest_modutils.py::LoadModuleFromNameTest::test_known_values_load_module_from_name_2", "tests/unittest_modutils.py::LoadModuleFromNameTest::test_raise_load_module_from_name_1", "tests/unittest_modutils.py::GetModulePartTest::test_get_module_part_exception", "tests/unittest_modutils.py::GetModulePartTest::test_known_values_get_builtin_module_part", "tests/unittest_modutils.py::GetModulePartTest::test_known_values_get_compiled_module_part", "tests/unittest_modutils.py::GetModulePartTest::test_known_values_get_module_part_1", "tests/unittest_modutils.py::GetModulePartTest::test_known_values_get_module_part_2", "tests/unittest_modutils.py::GetModulePartTest::test_known_values_get_module_part_3", "tests/unittest_modutils.py::ModPathFromFileTest::test_import_symlink_both_outside_of_path", "tests/unittest_modutils.py::ModPathFromFileTest::test_import_symlink_with_source_outside_of_path", "tests/unittest_modutils.py::ModPathFromFileTest::test_known_values_modpath_from_file_1", "tests/unittest_modutils.py::ModPathFromFileTest::test_load_from_module_symlink_on_symlinked_paths_in_syspath", "tests/unittest_modutils.py::ModPathFromFileTest::test_raise_modpath_from_file_exception", "tests/unittest_modutils.py::LoadModuleFromPathTest::test_do_not_load_twice", "tests/unittest_modutils.py::FileFromModPathTest::test_builtin", "tests/unittest_modutils.py::FileFromModPathTest::test_site_packages", "tests/unittest_modutils.py::FileFromModPathTest::test_std_lib", "tests/unittest_modutils.py::FileFromModPathTest::test_unexisting", "tests/unittest_modutils.py::FileFromModPathTest::test_unicode_in_package_init", "tests/unittest_modutils.py::GetSourceFileTest::test", "tests/unittest_modutils.py::GetSourceFileTest::test_raise", "tests/unittest_modutils.py::StandardLibModuleTest::test_4", "tests/unittest_modutils.py::StandardLibModuleTest::test_builtin", "tests/unittest_modutils.py::StandardLibModuleTest::test_builtins", "tests/unittest_modutils.py::StandardLibModuleTest::test_custom_path", "tests/unittest_modutils.py::StandardLibModuleTest::test_datetime", "tests/unittest_modutils.py::StandardLibModuleTest::test_failing_edge_cases", "tests/unittest_modutils.py::StandardLibModuleTest::test_nonstandard", "tests/unittest_modutils.py::StandardLibModuleTest::test_unknown", "tests/unittest_modutils.py::IsRelativeTest::test_deep_relative", "tests/unittest_modutils.py::IsRelativeTest::test_deep_relative2", "tests/unittest_modutils.py::IsRelativeTest::test_deep_relative3", "tests/unittest_modutils.py::IsRelativeTest::test_deep_relative4", "tests/unittest_modutils.py::IsRelativeTest::test_is_relative_bad_path", "tests/unittest_modutils.py::IsRelativeTest::test_known_values_is_relative_1", "tests/unittest_modutils.py::IsRelativeTest::test_known_values_is_relative_3", "tests/unittest_modutils.py::IsRelativeTest::test_known_values_is_relative_4", "tests/unittest_modutils.py::IsRelativeTest::test_known_values_is_relative_5", "tests/unittest_modutils.py::GetModuleFilesTest::test_get_all_files", "tests/unittest_modutils.py::GetModuleFilesTest::test_get_module_files_1", "tests/unittest_modutils.py::GetModuleFilesTest::test_load_module_set_attribute", "tests/unittest_modutils.py::ExtensionPackageWhitelistTest::test_is_module_name_part_of_extension_package_whitelist_success", "tests/unittest_modutils.py::ExtensionPackageWhitelistTest::test_is_module_name_part_of_extension_package_whitelist_true"]

**Base Commit**: d2a5b3c7b1e203fec3c7ca73c30eb1785d3d4d0a
**Environment Setup Commit**: da745538c7236028a22cdf0405f6829fcf6886bc
