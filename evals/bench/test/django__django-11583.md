# django__django-11583

**Repository**: django/django
**Created**: 2019-07-21T20:56:14Z
**Version**: 3.0

## Problem Statement

Auto-reloading with StatReloader very intermittently throws "ValueError: embedded null byte".
Description
	
Raising this mainly so that it's tracked, as I have no idea how to reproduce it, nor why it's happening. It ultimately looks like a problem with Pathlib, which wasn't used prior to 2.2.
Stacktrace:
Traceback (most recent call last):
 File "manage.py" ...
	execute_from_command_line(sys.argv)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/core/management/__init__.py", line 381, in execute_from_command_line
	utility.execute()
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/core/management/__init__.py", line 375, in execute
	self.fetch_command(subcommand).run_from_argv(self.argv)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/core/management/base.py", line 323, in run_from_argv
	self.execute(*args, **cmd_options)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/core/management/commands/runserver.py", line 60, in execute
	super().execute(*args, **options)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/core/management/base.py", line 364, in execute
	output = self.handle(*args, **options)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/core/management/commands/runserver.py", line 95, in handle
	self.run(**options)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/core/management/commands/runserver.py", line 102, in run
	autoreload.run_with_reloader(self.inner_run, **options)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 577, in run_with_reloader
	start_django(reloader, main_func, *args, **kwargs)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 562, in start_django
	reloader.run(django_main_thread)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 280, in run
	self.run_loop()
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 286, in run_loop
	next(ticker)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 326, in tick
	for filepath, mtime in self.snapshot_files():
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 342, in snapshot_files
	for file in self.watched_files():
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 241, in watched_files
	yield from iter_all_python_module_files()
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 103, in iter_all_python_module_files
	return iter_modules_and_files(modules, frozenset(_error_files))
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 132, in iter_modules_and_files
	results.add(path.resolve().absolute())
 File "/Users/kez/.pyenv/versions/3.6.2/lib/python3.6/pathlib.py", line 1120, in resolve
	s = self._flavour.resolve(self, strict=strict)
 File "/Users/kez/.pyenv/versions/3.6.2/lib/python3.6/pathlib.py", line 346, in resolve
	return _resolve(base, str(path)) or sep
 File "/Users/kez/.pyenv/versions/3.6.2/lib/python3.6/pathlib.py", line 330, in _resolve
	target = accessor.readlink(newpath)
 File "/Users/kez/.pyenv/versions/3.6.2/lib/python3.6/pathlib.py", line 441, in readlink
	return os.readlink(path)
ValueError: embedded null byte
I did print(path) before os.readlink(path) in pathlib and ended up with:
/Users/kez
/Users/kez/.pyenv
/Users/kez/.pyenv/versions
/Users/kez/.pyenv/versions/3.6.2
/Users/kez/.pyenv/versions/3.6.2/lib
/Users/kez/.pyenv/versions/3.6.2/lib/python3.6
/Users/kez/.pyenv/versions/3.6.2/lib/python3.6/asyncio
/Users/kez/.pyenv/versions/3.6.2/lib/python3.6/asyncio/selector_events.py
/Users
It always seems to be /Users which is last
It may have already printed /Users as part of another .resolve() multiple times (that is, the order is not deterministic, and it may have traversed beyond /Users successfully many times during startup.
I don't know where to begin looking for the rogue null byte, nor why it only exists sometimes.
Best guess I have is that there's a mountpoint in /Users to a samba share which may not have been connected to yet? I dunno.
I have no idea if it's fixable without removing the use of pathlib (which tbh I think should happen anyway, because it's slow) and reverting to using os.path.join and friends. 
I have no idea if it's fixed in a later Python version, but with no easy way to reproduce ... dunno how I'd check.
I have no idea if it's something specific to my system (pyenv, OSX 10.11, etc)


## Hints

Thanks for the report, however as you've admitted there is too many unknowns to accept this ticket. I don't believe that it is related with pathlib, maybe samba connection is unstable it's hard to tell.
I don't believe that it is related with pathlib Well ... it definitely is, you can see that from the stacktrace. The difference between 2.2 and 2.1 (and every version prior) for the purposes of this report is that AFAIK 2.2 is using pathlib.resolve() which deals with symlinks where under <2.2 I don't think the equivalent (os.path.realpath rather than os.path.abspath) was used. But yes, there's no path forward to fix the ticket as it stands, short of not using pathlib (or at least .resolve()).
Hey Keryn, Have you tried removing resolve() yourself, and did it fix the issue? I chose to use resolve() to try and work around a corner case with symlinks, and to generally just normalize the paths to prevent duplication. Also, regarding your comment above, you would need to use print(repr(path)), as I think the print machinery stops at the first null byte found (hence just /Users, which should never be monitored by itself). If you can provide me some more information I'm more than willing to look into this, or consider removing the resolve() call.
Replying to Tom Forbes: Hey Keryn, Have you tried removing resolve() yourself, and did it fix the issue? I chose to use resolve() to try and work around a corner case with symlinks, and to generally just normalize the paths to prevent duplication. Also, regarding your comment above, you would need to use print(repr(path)), as I think the print machinery stops at the first null byte found (hence just /Users, which should never be monitored by itself). If you can provide me some more information I'm more than willing to look into this, or consider removing the resolve() call. Hi Tom, I am also getting this error, see here for the stackoverflow question which I have attempted to answer: ​https://stackoverflow.com/questions/56406965/django-valueerror-embedded-null-byte/56685648#56685648 What is really odd is that it doesn't error every time and looks to error on a random file each time. I believe the issue is caused by having a venv within the top level directory but might be wrong. Bug is on all versions of django >= 2.2.0
Felix, I'm going to re-open this ticket if that's OK. While this is clearly something "funky" going on at a lower level than we handle, it used to work (at least, the error was swallowed). I think this is a fairly simple fix.

## Patch

```diff

diff --git a/django/utils/autoreload.py b/django/utils/autoreload.py
--- a/django/utils/autoreload.py
+++ b/django/utils/autoreload.py
@@ -143,6 +143,10 @@ def iter_modules_and_files(modules, extra_files):
             # The module could have been removed, don't fail loudly if this
             # is the case.
             continue
+        except ValueError as e:
+            # Network filesystems may return null bytes in file paths.
+            logger.debug('"%s" raised when resolving path: "%s"' % (str(e), path))
+            continue
         results.add(resolved_path)
     return frozenset(results)
 


```

## Test Patch

```diff
diff --git a/tests/utils_tests/test_autoreload.py b/tests/utils_tests/test_autoreload.py
--- a/tests/utils_tests/test_autoreload.py
+++ b/tests/utils_tests/test_autoreload.py
@@ -140,6 +140,17 @@ def test_main_module_without_file_is_not_resolved(self):
         fake_main = types.ModuleType('__main__')
         self.assertEqual(autoreload.iter_modules_and_files((fake_main,), frozenset()), frozenset())
 
+    def test_path_with_embedded_null_bytes(self):
+        for path in (
+            'embedded_null_byte\x00.py',
+            'di\x00rectory/embedded_null_byte.py',
+        ):
+            with self.subTest(path=path):
+                self.assertEqual(
+                    autoreload.iter_modules_and_files((), frozenset([path])),
+                    frozenset(),
+                )
+
 
 class TestCommonRoots(SimpleTestCase):
     def test_common_roots(self):

```

## Test Information

**Tests that should FAIL→PASS**: ["test_path_with_embedded_null_bytes (utils_tests.test_autoreload.TestIterModulesAndFiles)", "test_paths_are_pathlib_instances (utils_tests.test_autoreload.TestIterModulesAndFiles)"]

**Tests that should PASS→PASS**: ["test_no_exception (utils_tests.test_autoreload.TestRaiseLastException)", "test_raises_custom_exception (utils_tests.test_autoreload.TestRaiseLastException)", "test_raises_exception (utils_tests.test_autoreload.TestRaiseLastException)", "test_raises_exception_with_context (utils_tests.test_autoreload.TestRaiseLastException)", "test_watchman_available (utils_tests.test_autoreload.GetReloaderTests)", "test_watchman_unavailable (utils_tests.test_autoreload.GetReloaderTests)", "test_common_roots (utils_tests.test_autoreload.TestCommonRoots)", "test_calls_start_django (utils_tests.test_autoreload.RunWithReloaderTests)", "test_calls_sys_exit (utils_tests.test_autoreload.RunWithReloaderTests)", "test_swallows_keyboard_interrupt (utils_tests.test_autoreload.RunWithReloaderTests)", "test_mutates_error_files (utils_tests.test_autoreload.TestCheckErrors)", "test_sys_paths_absolute (utils_tests.test_autoreload.TestSysPathDirectories)", "test_sys_paths_directories (utils_tests.test_autoreload.TestSysPathDirectories)", "test_sys_paths_non_existing (utils_tests.test_autoreload.TestSysPathDirectories)", "test_sys_paths_with_directories (utils_tests.test_autoreload.TestSysPathDirectories)", "test_manage_py (utils_tests.test_autoreload.RestartWithReloaderTests)", "test_python_m_django (utils_tests.test_autoreload.RestartWithReloaderTests)", "test_run_loop_catches_stopiteration (utils_tests.test_autoreload.BaseReloaderTests)", "test_run_loop_stop_and_return (utils_tests.test_autoreload.BaseReloaderTests)", "test_wait_for_apps_ready_checks_for_exception (utils_tests.test_autoreload.BaseReloaderTests)", "test_wait_for_apps_ready_without_exception (utils_tests.test_autoreload.BaseReloaderTests)", "test_watch_files_with_recursive_glob (utils_tests.test_autoreload.BaseReloaderTests)", "test_watch_with_glob (utils_tests.test_autoreload.BaseReloaderTests)", "test_watch_with_single_file (utils_tests.test_autoreload.BaseReloaderTests)", "test_watch_without_absolute (utils_tests.test_autoreload.BaseReloaderTests)", "test_file (utils_tests.test_autoreload.StatReloaderTests)", "test_glob (utils_tests.test_autoreload.StatReloaderTests)", "test_glob_recursive (utils_tests.test_autoreload.StatReloaderTests)", "test_multiple_globs (utils_tests.test_autoreload.StatReloaderTests)", "test_multiple_recursive_globs (utils_tests.test_autoreload.StatReloaderTests)", "test_nested_glob_recursive (utils_tests.test_autoreload.StatReloaderTests)", "test_overlapping_glob_recursive (utils_tests.test_autoreload.StatReloaderTests)", "test_overlapping_globs (utils_tests.test_autoreload.StatReloaderTests)", "test_snapshot_files_ignores_missing_files (utils_tests.test_autoreload.StatReloaderTests)", "test_snapshot_files_updates (utils_tests.test_autoreload.StatReloaderTests)", "test_snapshot_files_with_duplicates (utils_tests.test_autoreload.StatReloaderTests)", "test_tick_does_not_trigger_twice (utils_tests.test_autoreload.StatReloaderTests)", "test_check_errors_called (utils_tests.test_autoreload.StartDjangoTests)", "test_echo_on_called (utils_tests.test_autoreload.StartDjangoTests)", "test_starts_thread_with_args (utils_tests.test_autoreload.StartDjangoTests)", "test_watchman_becomes_unavailable (utils_tests.test_autoreload.StartDjangoTests)", ".pyc and .pyo files are included in the files list.", "test_check_errors (utils_tests.test_autoreload.TestIterModulesAndFiles)", "test_check_errors_catches_all_exceptions (utils_tests.test_autoreload.TestIterModulesAndFiles)", "test_file_added (utils_tests.test_autoreload.TestIterModulesAndFiles)", "test_main_module_is_resolved (utils_tests.test_autoreload.TestIterModulesAndFiles)", "test_main_module_without_file_is_not_resolved (utils_tests.test_autoreload.TestIterModulesAndFiles)", "test_module_without_spec (utils_tests.test_autoreload.TestIterModulesAndFiles)", "iter_all_python_module_file() ignores weakref modules.", "test_zip_reload (utils_tests.test_autoreload.TestIterModulesAndFiles)"]

**Base Commit**: 60dc957a825232fdda9138e2f8878b2ca407a7c9
**Environment Setup Commit**: 419a78300f7cd27611196e1e464d50fd0385ff27
