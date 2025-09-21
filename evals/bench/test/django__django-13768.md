# django__django-13768

**Repository**: django/django
**Created**: 2020-12-12T07:34:48Z
**Version**: 3.2

## Problem Statement

Log exceptions handled in Signal.send_robust()
Description
	
As pointed out by ​Haki Benita on Twitter, by default Signal.send_robust() doesn't have any log messages for exceptions raised in receivers. Since Django logs exceptions in other similar situations, such as missing template variables, I think it would be worth adding a logger.exception() call in the except clause of send_robust() . Users would then see such exceptions in their error handling tools, e.g. Sentry, and be able to figure out what action to take from there. Ultimately any *expected* exception should be caught with a try in the receiver function.


## Hints

I would like to work on this issue. PS. i am new to this django. so any advice would be appreciated

## Patch

```diff

diff --git a/django/dispatch/dispatcher.py b/django/dispatch/dispatcher.py
--- a/django/dispatch/dispatcher.py
+++ b/django/dispatch/dispatcher.py
@@ -1,3 +1,4 @@
+import logging
 import threading
 import warnings
 import weakref
@@ -5,6 +6,8 @@
 from django.utils.deprecation import RemovedInDjango40Warning
 from django.utils.inspect import func_accepts_kwargs
 
+logger = logging.getLogger('django.dispatch')
+
 
 def _make_id(target):
     if hasattr(target, '__func__'):
@@ -208,6 +211,12 @@ def send_robust(self, sender, **named):
             try:
                 response = receiver(signal=self, sender=sender, **named)
             except Exception as err:
+                logger.error(
+                    'Error calling %s in Signal.send_robust() (%s)',
+                    receiver.__qualname__,
+                    err,
+                    exc_info=err,
+                )
                 responses.append((receiver, err))
             else:
                 responses.append((receiver, response))


```

## Test Patch

```diff
diff --git a/tests/dispatch/tests.py b/tests/dispatch/tests.py
--- a/tests/dispatch/tests.py
+++ b/tests/dispatch/tests.py
@@ -165,13 +165,28 @@ def test_send_robust_fail(self):
         def fails(val, **kwargs):
             raise ValueError('this')
         a_signal.connect(fails)
-        result = a_signal.send_robust(sender=self, val="test")
-        err = result[0][1]
-        self.assertIsInstance(err, ValueError)
-        self.assertEqual(err.args, ('this',))
-        self.assertTrue(hasattr(err, '__traceback__'))
-        self.assertIsInstance(err.__traceback__, TracebackType)
-        a_signal.disconnect(fails)
+        try:
+            with self.assertLogs('django.dispatch', 'ERROR') as cm:
+                result = a_signal.send_robust(sender=self, val='test')
+            err = result[0][1]
+            self.assertIsInstance(err, ValueError)
+            self.assertEqual(err.args, ('this',))
+            self.assertIs(hasattr(err, '__traceback__'), True)
+            self.assertIsInstance(err.__traceback__, TracebackType)
+
+            log_record = cm.records[0]
+            self.assertEqual(
+                log_record.getMessage(),
+                'Error calling '
+                'DispatcherTests.test_send_robust_fail.<locals>.fails in '
+                'Signal.send_robust() (this)',
+            )
+            self.assertIsNotNone(log_record.exc_info)
+            _, exc_value, _ = log_record.exc_info
+            self.assertIsInstance(exc_value, ValueError)
+            self.assertEqual(str(exc_value), 'this')
+        finally:
+            a_signal.disconnect(fails)
         self.assertTestIsClean(a_signal)
 
     def test_disconnection(self):

```

## Test Information

**Tests that should FAIL→PASS**: ["test_send_robust_fail (dispatch.tests.DispatcherTests)"]

**Tests that should PASS→PASS**: ["test_receiver_signal_list (dispatch.tests.ReceiverTestCase)", "test_receiver_single_signal (dispatch.tests.ReceiverTestCase)", "test_cached_garbaged_collected (dispatch.tests.DispatcherTests)", "test_cannot_connect_no_kwargs (dispatch.tests.DispatcherTests)", "test_cannot_connect_non_callable (dispatch.tests.DispatcherTests)", "test_disconnection (dispatch.tests.DispatcherTests)", "test_garbage_collected (dispatch.tests.DispatcherTests)", "test_has_listeners (dispatch.tests.DispatcherTests)", "test_multiple_registration (dispatch.tests.DispatcherTests)", "test_send (dispatch.tests.DispatcherTests)", "test_send_connected_no_sender (dispatch.tests.DispatcherTests)", "test_send_different_no_sender (dispatch.tests.DispatcherTests)", "test_send_no_receivers (dispatch.tests.DispatcherTests)", "test_send_robust_ignored_sender (dispatch.tests.DispatcherTests)", "test_send_robust_no_receivers (dispatch.tests.DispatcherTests)", "test_send_robust_success (dispatch.tests.DispatcherTests)", "test_uid_registration (dispatch.tests.DispatcherTests)", "test_values_returned_by_disconnection (dispatch.tests.DispatcherTests)"]

**Base Commit**: 965d2d95c630939b53eb60d9c169f5dfc77ee0c6
**Environment Setup Commit**: 65dfb06a1ab56c238cc80f5e1c31f61210c4577d
