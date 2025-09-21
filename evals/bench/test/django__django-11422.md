# django__django-11422

**Repository**: django/django
**Created**: 2019-05-27T19:15:21Z
**Version**: 3.0

## Problem Statement

Autoreloader with StatReloader doesn't track changes in manage.py.
Description
	 
		(last modified by Mariusz Felisiak)
	 
This is a bit convoluted, but here we go.
Environment (OSX 10.11):
$ python -V
Python 3.6.2
$ pip -V
pip 19.1.1
$ pip install Django==2.2.1
Steps to reproduce:
Run a server python manage.py runserver
Edit the manage.py file, e.g. add print(): 
def main():
	print('sth')
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket_30479.settings')
	...
Under 2.1.8 (and prior), this will trigger the auto-reloading mechanism. Under 2.2.1, it won't. As far as I can tell from the django.utils.autoreload log lines, it never sees the manage.py itself.


## Hints

Thanks for the report. I simplified scenario. Regression in c8720e7696ca41f3262d5369365cc1bd72a216ca. Reproduced at 8d010f39869f107820421631111417298d1c5bb9.
Argh. I guess this is because manage.py isn't showing up in the sys.modules. I'm not sure I remember any specific manage.py handling in the old implementation, so I'm not sure how it used to work, but I should be able to fix this pretty easily.
Done a touch of debugging: iter_modules_and_files is where it gets lost. Specifically, it ends up in there twice: (<module '__future__' from '/../lib/python3.6/__future__.py'>, <module '__main__' from 'manage.py'>, <module '__main__' from 'manage.py'>, ...,) But getattr(module, "__spec__", None) is None is True so it continues onwards. I thought I managed to get one of them to have a __spec__ attr but no has_location, but I can't seem to get that again (stepping around with pdb) Digging into wtf __spec__ is None: ​Here's the py3 docs on it, which helpfully mentions that ​The one exception is __main__, where __spec__ is set to None in some cases
Tom, will you have time to work on this in the next few days?
I'm sorry for assigning it to myself Mariusz, I intended to work on it on Tuesday but work overtook me and now I am travelling for a wedding this weekend. So I doubt it I'm afraid. It seems Keryn's debugging is a great help, it should be somewhat simple to add special case handling for __main__, while __spec__ is None we can still get the filename and watch on that.
np, Tom, thanks for info. Keryn, it looks that you've already made most of the work. Would you like to prepare a patch?

## Patch

```diff

diff --git a/django/utils/autoreload.py b/django/utils/autoreload.py
--- a/django/utils/autoreload.py
+++ b/django/utils/autoreload.py
@@ -114,7 +114,15 @@ def iter_modules_and_files(modules, extra_files):
         # During debugging (with PyDev) the 'typing.io' and 'typing.re' objects
         # are added to sys.modules, however they are types not modules and so
         # cause issues here.
-        if not isinstance(module, ModuleType) or getattr(module, '__spec__', None) is None:
+        if not isinstance(module, ModuleType):
+            continue
+        if module.__name__ == '__main__':
+            # __main__ (usually manage.py) doesn't always have a __spec__ set.
+            # Handle this by falling back to using __file__, resolved below.
+            # See https://docs.python.org/reference/import.html#main-spec
+            sys_file_paths.append(module.__file__)
+            continue
+        if getattr(module, '__spec__', None) is None:
             continue
         spec = module.__spec__
         # Modules could be loaded from places without a concrete location. If


```

## Test Patch

```diff
diff --git a/tests/utils_tests/test_autoreload.py b/tests/utils_tests/test_autoreload.py
--- a/tests/utils_tests/test_autoreload.py
+++ b/tests/utils_tests/test_autoreload.py
@@ -132,6 +132,10 @@ def test_module_without_spec(self):
         del module.__spec__
         self.assertEqual(autoreload.iter_modules_and_files((module,), frozenset()), frozenset())
 
+    def test_main_module_is_resolved(self):
+        main_module = sys.modules['__main__']
+        self.assertFileFound(Path(main_module.__file__))
+
 
 class TestCommonRoots(SimpleTestCase):
     def test_common_roots(self):

```

## Test Information

**Tests that should FAIL→PASS**: ["test_main_module_is_resolved (utils_tests.test_autoreload.TestIterModulesAndFiles)"]

**Tests that should PASS→PASS**: ["test_watchman_available (utils_tests.test_autoreload.GetReloaderTests)", "test_watchman_unavailable (utils_tests.test_autoreload.GetReloaderTests)", "test_calls_start_django (utils_tests.test_autoreload.RunWithReloaderTests)", "test_calls_sys_exit (utils_tests.test_autoreload.RunWithReloaderTests)", "test_swallows_keyboard_interrupt (utils_tests.test_autoreload.RunWithReloaderTests)", "test_common_roots (utils_tests.test_autoreload.TestCommonRoots)", "test_no_exception (utils_tests.test_autoreload.TestRaiseLastException)", "test_raises_exception (utils_tests.test_autoreload.TestRaiseLastException)", "test_mutates_error_files (utils_tests.test_autoreload.TestCheckErrors)", "test_sys_paths_absolute (utils_tests.test_autoreload.TestSysPathDirectories)", "test_sys_paths_directories (utils_tests.test_autoreload.TestSysPathDirectories)", "test_sys_paths_non_existing (utils_tests.test_autoreload.TestSysPathDirectories)", "test_sys_paths_with_directories (utils_tests.test_autoreload.TestSysPathDirectories)", "test_manage_py (utils_tests.test_autoreload.RestartWithReloaderTests)", "test_python_m_django (utils_tests.test_autoreload.RestartWithReloaderTests)", "test_run_loop_catches_stopiteration (utils_tests.test_autoreload.BaseReloaderTests)", "test_run_loop_stop_and_return (utils_tests.test_autoreload.BaseReloaderTests)", "test_wait_for_apps_ready_checks_for_exception (utils_tests.test_autoreload.BaseReloaderTests)", "test_wait_for_apps_ready_without_exception (utils_tests.test_autoreload.BaseReloaderTests)", "test_watch_files_with_recursive_glob (utils_tests.test_autoreload.BaseReloaderTests)", "test_watch_with_glob (utils_tests.test_autoreload.BaseReloaderTests)", "test_watch_with_single_file (utils_tests.test_autoreload.BaseReloaderTests)", "test_watch_without_absolute (utils_tests.test_autoreload.BaseReloaderTests)", "test_file (utils_tests.test_autoreload.StatReloaderTests)", "test_glob (utils_tests.test_autoreload.StatReloaderTests)", "test_glob_recursive (utils_tests.test_autoreload.StatReloaderTests)", "test_multiple_globs (utils_tests.test_autoreload.StatReloaderTests)", "test_multiple_recursive_globs (utils_tests.test_autoreload.StatReloaderTests)", "test_nested_glob_recursive (utils_tests.test_autoreload.StatReloaderTests)", "test_overlapping_glob_recursive (utils_tests.test_autoreload.StatReloaderTests)", "test_overlapping_globs (utils_tests.test_autoreload.StatReloaderTests)", "test_snapshot_files_ignores_missing_files (utils_tests.test_autoreload.StatReloaderTests)", "test_snapshot_files_updates (utils_tests.test_autoreload.StatReloaderTests)", "test_snapshot_files_with_duplicates (utils_tests.test_autoreload.StatReloaderTests)", "test_check_errors_called (utils_tests.test_autoreload.StartDjangoTests)", "test_echo_on_called (utils_tests.test_autoreload.StartDjangoTests)", "test_starts_thread_with_args (utils_tests.test_autoreload.StartDjangoTests)", "test_watchman_becomes_unavailable (utils_tests.test_autoreload.StartDjangoTests)", ".pyc and .pyo files are included in the files list.", "test_check_errors (utils_tests.test_autoreload.TestIterModulesAndFiles)", "test_check_errors_catches_all_exceptions (utils_tests.test_autoreload.TestIterModulesAndFiles)", "test_file_added (utils_tests.test_autoreload.TestIterModulesAndFiles)", "test_module_without_spec (utils_tests.test_autoreload.TestIterModulesAndFiles)", "test_paths_are_pathlib_instances (utils_tests.test_autoreload.TestIterModulesAndFiles)", "iter_all_python_module_file() ignores weakref modules.", "test_zip_reload (utils_tests.test_autoreload.TestIterModulesAndFiles)"]

**Base Commit**: df46b329e0900e9e4dc1d60816c1dce6dfc1094e
**Environment Setup Commit**: 419a78300f7cd27611196e1e464d50fd0385ff27
