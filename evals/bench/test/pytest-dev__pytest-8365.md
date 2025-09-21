# pytest-dev__pytest-8365

**Repository**: pytest-dev/pytest
**Created**: 2021-02-22T20:26:35Z
**Version**: 6.3

## Problem Statement

tmpdir creation fails when the username contains illegal characters for directory names
`tmpdir`, `tmpdir_factory` and `tmp_path_factory` rely on `getpass.getuser()` for determining the `basetemp` directory. I found that the user name returned by `getpass.getuser()` may return characters that are not allowed for directory names. This may lead to errors while creating the temporary directory.

The situation in which I reproduced this issue was while being logged in through an ssh connection into my Windows 10 x64 Enterprise version (1909) using an OpenSSH_for_Windows_7.7p1 server. In this configuration the command `python -c "import getpass; print(getpass.getuser())"` returns my domain username e.g. `contoso\john_doe` instead of `john_doe` as when logged in regularly using a local session.

When trying to create a temp directory in pytest through e.g. `tmpdir_factory.mktemp('foobar')` this fails with the following error message:
```
self = WindowsPath('C:/Users/john_doe/AppData/Local/Temp/pytest-of-contoso/john_doe')
mode = 511, parents = False, exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        if self._closed:
            self._raise_closed()
        try:
>           self._accessor.mkdir(self, mode)
E           FileNotFoundError: [WinError 3] The system cannot find the path specified: 'C:\\Users\\john_doe\\AppData\\Local\\Temp\\pytest-of-contoso\\john_doe'

C:\Python38\lib\pathlib.py:1266: FileNotFoundError
```

I could also reproduce this without the complicated ssh/windows setup with pytest 6.2.2 using the following commands from a `cmd`:
```bat
echo def test_tmpdir(tmpdir):>test_tmp.py
echo   pass>>test_tmp.py
set LOGNAME=contoso\john_doe
py.test test_tmp.py
```

Thanks for having a look at this!


## Hints

Thanks for the report @pborsutzki!

## Patch

```diff

diff --git a/src/_pytest/tmpdir.py b/src/_pytest/tmpdir.py
--- a/src/_pytest/tmpdir.py
+++ b/src/_pytest/tmpdir.py
@@ -115,7 +115,12 @@ def getbasetemp(self) -> Path:
             # use a sub-directory in the temproot to speed-up
             # make_numbered_dir() call
             rootdir = temproot.joinpath(f"pytest-of-{user}")
-            rootdir.mkdir(exist_ok=True)
+            try:
+                rootdir.mkdir(exist_ok=True)
+            except OSError:
+                # getuser() likely returned illegal characters for the platform, use unknown back off mechanism
+                rootdir = temproot.joinpath("pytest-of-unknown")
+                rootdir.mkdir(exist_ok=True)
             basetemp = make_numbered_dir_with_cleanup(
                 prefix="pytest-", root=rootdir, keep=3, lock_timeout=LOCK_TIMEOUT
             )


```

## Test Patch

```diff
diff --git a/testing/test_tmpdir.py b/testing/test_tmpdir.py
--- a/testing/test_tmpdir.py
+++ b/testing/test_tmpdir.py
@@ -11,6 +11,7 @@
 import pytest
 from _pytest import pathlib
 from _pytest.config import Config
+from _pytest.monkeypatch import MonkeyPatch
 from _pytest.pathlib import cleanup_numbered_dir
 from _pytest.pathlib import create_cleanup_lock
 from _pytest.pathlib import make_numbered_dir
@@ -445,3 +446,14 @@ def test(tmp_path):
     # running a second time and ensure we don't crash
     result = pytester.runpytest("--basetemp=tmp")
     assert result.ret == 0
+
+
+def test_tmp_path_factory_handles_invalid_dir_characters(
+    tmp_path_factory: TempPathFactory, monkeypatch: MonkeyPatch
+) -> None:
+    monkeypatch.setattr("getpass.getuser", lambda: "os/<:*?;>agnostic")
+    # _basetemp / _given_basetemp are cached / set in parallel runs, patch them
+    monkeypatch.setattr(tmp_path_factory, "_basetemp", None)
+    monkeypatch.setattr(tmp_path_factory, "_given_basetemp", None)
+    p = tmp_path_factory.getbasetemp()
+    assert "pytest-of-unknown" in str(p)

```

## Test Information

**Tests that should FAIL→PASS**: ["testing/test_tmpdir.py::test_tmp_path_factory_handles_invalid_dir_characters"]

**Tests that should PASS→PASS**: ["testing/test_tmpdir.py::TestTempdirHandler::test_mktemp", "testing/test_tmpdir.py::TestTempdirHandler::test_tmppath_relative_basetemp_absolute", "testing/test_tmpdir.py::test_get_user_uid_not_found", "testing/test_tmpdir.py::TestNumberedDir::test_make", "testing/test_tmpdir.py::TestNumberedDir::test_cleanup_lock_create", "testing/test_tmpdir.py::TestNumberedDir::test_lock_register_cleanup_removal", "testing/test_tmpdir.py::TestNumberedDir::test_cleanup_keep", "testing/test_tmpdir.py::TestNumberedDir::test_cleanup_locked", "testing/test_tmpdir.py::TestNumberedDir::test_cleanup_ignores_symlink", "testing/test_tmpdir.py::TestNumberedDir::test_removal_accepts_lock", "testing/test_tmpdir.py::TestRmRf::test_rm_rf", "testing/test_tmpdir.py::TestRmRf::test_rm_rf_with_read_only_file", "testing/test_tmpdir.py::TestRmRf::test_rm_rf_with_read_only_directory", "testing/test_tmpdir.py::TestRmRf::test_on_rm_rf_error", "testing/test_tmpdir.py::test_tmpdir_equals_tmp_path", "testing/test_tmpdir.py::test_tmpdir_fixture", "testing/test_tmpdir.py::TestConfigTmpdir::test_getbasetemp_custom_removes_old", "testing/test_tmpdir.py::test_mktemp[mypath-True]", "testing/test_tmpdir.py::test_mktemp[/mypath1-False]", "testing/test_tmpdir.py::test_mktemp[./mypath1-True]", "testing/test_tmpdir.py::test_mktemp[../mypath3-False]", "testing/test_tmpdir.py::test_mktemp[../../mypath4-False]", "testing/test_tmpdir.py::test_mktemp[mypath5/..-False]", "testing/test_tmpdir.py::test_mktemp[mypath6/../mypath6-True]", "testing/test_tmpdir.py::test_mktemp[mypath7/../mypath7/..-False]", "testing/test_tmpdir.py::test_tmpdir_always_is_realpath", "testing/test_tmpdir.py::test_tmp_path_always_is_realpath", "testing/test_tmpdir.py::test_tmpdir_too_long_on_parametrization", "testing/test_tmpdir.py::test_tmpdir_factory", "testing/test_tmpdir.py::test_tmpdir_fallback_tox_env", "testing/test_tmpdir.py::test_tmpdir_fallback_uid_not_found", "testing/test_tmpdir.py::test_basetemp_with_read_only_files"]

**Base Commit**: 4964b468c83c06971eb743fbc57cc404f760c573
**Environment Setup Commit**: 634312b14a45db8d60d72016e01294284e3a18d4
