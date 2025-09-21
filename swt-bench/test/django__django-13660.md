# django__django-13660

**Repository**: django/django
**Created**: 2020-11-09T22:43:32Z
**Version**: 3.2

## Problem Statement

shell command crashes when passing (with -c) the python code with functions.
Description
	
The examples below use Python 3.7 and Django 2.2.16, but I checked that the code is the same on master and works the same in Python 3.8.
Here's how ​python -c works:
$ python -c <<EOF " 
import django
def f():
		print(django.__version__)
f()"
EOF
2.2.16
Here's how ​python -m django shell -c works (paths shortened for clarify):
$ python -m django shell -c <<EOF "
import django
def f():
		print(django.__version__)
f()"
EOF
Traceback (most recent call last):
 File "{sys.base_prefix}/lib/python3.7/runpy.py", line 193, in _run_module_as_main
	"__main__", mod_spec)
 File "{sys.base_prefix}/lib/python3.7/runpy.py", line 85, in _run_code
	exec(code, run_globals)
 File "{sys.prefix}/lib/python3.7/site-packages/django/__main__.py", line 9, in <module>
	management.execute_from_command_line()
 File "{sys.prefix}/lib/python3.7/site-packages/django/core/management/__init__.py", line 381, in execute_from_command_line
	utility.execute()
 File "{sys.prefix}/lib/python3.7/site-packages/django/core/management/__init__.py", line 375, in execute
	self.fetch_command(subcommand).run_from_argv(self.argv)
 File "{sys.prefix}/lib/python3.7/site-packages/django/core/management/base.py", line 323, in run_from_argv
	self.execute(*args, **cmd_options)
 File "{sys.prefix}/lib/python3.7/site-packages/django/core/management/base.py", line 364, in execute
	output = self.handle(*args, **options)
 File "{sys.prefix}/lib/python3.7/site-packages/django/core/management/commands/shell.py", line 86, in handle
	exec(options['command'])
 File "<string>", line 5, in <module>
 File "<string>", line 4, in f
NameError: name 'django' is not defined
The problem is in the ​usage of ​exec:
	def handle(self, **options):
		# Execute the command and exit.
		if options['command']:
			exec(options['command'])
			return
		# Execute stdin if it has anything to read and exit.
		# Not supported on Windows due to select.select() limitations.
		if sys.platform != 'win32' and not sys.stdin.isatty() and select.select([sys.stdin], [], [], 0)[0]:
			exec(sys.stdin.read())
			return
exec should be passed a dictionary containing a minimal set of globals. This can be done by just passing a new, empty dictionary as the second argument of exec.


## Hints

​PR includes tests and documents the new feature in the release notes (but not in the main docs since it seems more like a bug fix than a new feature to me).

## Patch

```diff

diff --git a/django/core/management/commands/shell.py b/django/core/management/commands/shell.py
--- a/django/core/management/commands/shell.py
+++ b/django/core/management/commands/shell.py
@@ -84,13 +84,13 @@ def python(self, options):
     def handle(self, **options):
         # Execute the command and exit.
         if options['command']:
-            exec(options['command'])
+            exec(options['command'], globals())
             return
 
         # Execute stdin if it has anything to read and exit.
         # Not supported on Windows due to select.select() limitations.
         if sys.platform != 'win32' and not sys.stdin.isatty() and select.select([sys.stdin], [], [], 0)[0]:
-            exec(sys.stdin.read())
+            exec(sys.stdin.read(), globals())
             return
 
         available_shells = [options['interface']] if options['interface'] else self.shells


```

## Test Patch

```diff
diff --git a/tests/shell/tests.py b/tests/shell/tests.py
--- a/tests/shell/tests.py
+++ b/tests/shell/tests.py
@@ -9,6 +9,13 @@
 
 
 class ShellCommandTestCase(SimpleTestCase):
+    script_globals = 'print("__name__" in globals())'
+    script_with_inline_function = (
+        'import django\n'
+        'def f():\n'
+        '    print(django.__version__)\n'
+        'f()'
+    )
 
     def test_command_option(self):
         with self.assertLogs('test', 'INFO') as cm:
@@ -21,6 +28,16 @@ def test_command_option(self):
             )
         self.assertEqual(cm.records[0].getMessage(), __version__)
 
+    def test_command_option_globals(self):
+        with captured_stdout() as stdout:
+            call_command('shell', command=self.script_globals)
+        self.assertEqual(stdout.getvalue().strip(), 'True')
+
+    def test_command_option_inline_function_call(self):
+        with captured_stdout() as stdout:
+            call_command('shell', command=self.script_with_inline_function)
+        self.assertEqual(stdout.getvalue().strip(), __version__)
+
     @unittest.skipIf(sys.platform == 'win32', "Windows select() doesn't support file descriptors.")
     @mock.patch('django.core.management.commands.shell.select')
     def test_stdin_read(self, select):
@@ -30,6 +47,30 @@ def test_stdin_read(self, select):
             call_command('shell')
         self.assertEqual(stdout.getvalue().strip(), '100')
 
+    @unittest.skipIf(
+        sys.platform == 'win32',
+        "Windows select() doesn't support file descriptors.",
+    )
+    @mock.patch('django.core.management.commands.shell.select')  # [1]
+    def test_stdin_read_globals(self, select):
+        with captured_stdin() as stdin, captured_stdout() as stdout:
+            stdin.write(self.script_globals)
+            stdin.seek(0)
+            call_command('shell')
+        self.assertEqual(stdout.getvalue().strip(), 'True')
+
+    @unittest.skipIf(
+        sys.platform == 'win32',
+        "Windows select() doesn't support file descriptors.",
+    )
+    @mock.patch('django.core.management.commands.shell.select')  # [1]
+    def test_stdin_read_inline_function_call(self, select):
+        with captured_stdin() as stdin, captured_stdout() as stdout:
+            stdin.write(self.script_with_inline_function)
+            stdin.seek(0)
+            call_command('shell')
+        self.assertEqual(stdout.getvalue().strip(), __version__)
+
     @mock.patch('django.core.management.commands.shell.select.select')  # [1]
     @mock.patch.dict('sys.modules', {'IPython': None})
     def test_shell_with_ipython_not_installed(self, select):

```

## Test Information

**Tests that should FAIL→PASS**: ["test_command_option_inline_function_call (shell.tests.ShellCommandTestCase)", "test_stdin_read_inline_function_call (shell.tests.ShellCommandTestCase)"]

**Tests that should PASS→PASS**: ["test_command_option (shell.tests.ShellCommandTestCase)", "test_command_option_globals (shell.tests.ShellCommandTestCase)", "test_shell_with_bpython_not_installed (shell.tests.ShellCommandTestCase)", "test_shell_with_ipython_not_installed (shell.tests.ShellCommandTestCase)", "test_stdin_read (shell.tests.ShellCommandTestCase)", "test_stdin_read_globals (shell.tests.ShellCommandTestCase)"]

**Base Commit**: 50c3ac6fa9b7c8a94a6d1dc87edf775e3bc4d575
**Environment Setup Commit**: 65dfb06a1ab56c238cc80f5e1c31f61210c4577d
