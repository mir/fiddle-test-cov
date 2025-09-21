# django__django-12915

**Repository**: django/django
**Created**: 2020-05-14T23:30:01Z
**Version**: 3.2

## Problem Statement

Add get_response_async for ASGIStaticFilesHandler
Description
	
It looks like the StaticFilesHandlerMixin is missing the the async response function.
Without this, when trying to use the ASGIStaticFilesHandler, this is the traceback:
Exception inside application: 'NoneType' object is not callable
Traceback (most recent call last):
 File ".../lib/python3.7/site-packages/daphne/cli.py", line 30, in asgi
	await self.app(scope, receive, send)
 File ".../src/django/django/contrib/staticfiles/handlers.py", line 86, in __call__
	return await super().__call__(scope, receive, send)
 File ".../src/django/django/core/handlers/asgi.py", line 161, in __call__
	response = await self.get_response_async(request)
 File ".../src/django/django/core/handlers/base.py", line 148, in get_response_async
	response = await self._middleware_chain(request)
TypeError: 'NoneType' object is not callable


## Patch

```diff

diff --git a/django/contrib/staticfiles/handlers.py b/django/contrib/staticfiles/handlers.py
--- a/django/contrib/staticfiles/handlers.py
+++ b/django/contrib/staticfiles/handlers.py
@@ -1,6 +1,8 @@
 from urllib.parse import urlparse
 from urllib.request import url2pathname
 
+from asgiref.sync import sync_to_async
+
 from django.conf import settings
 from django.contrib.staticfiles import utils
 from django.contrib.staticfiles.views import serve
@@ -52,6 +54,12 @@ def get_response(self, request):
         except Http404 as e:
             return response_for_exception(request, e)
 
+    async def get_response_async(self, request):
+        try:
+            return await sync_to_async(self.serve)(request)
+        except Http404 as e:
+            return await sync_to_async(response_for_exception)(request, e)
+
 
 class StaticFilesHandler(StaticFilesHandlerMixin, WSGIHandler):
     """


```

## Test Patch

```diff
diff --git a/tests/asgi/project/static/file.txt b/tests/asgi/project/static/file.txt
new file mode 100644
--- /dev/null
+++ b/tests/asgi/project/static/file.txt
@@ -0,0 +1 @@
+test
diff --git a/tests/asgi/tests.py b/tests/asgi/tests.py
--- a/tests/asgi/tests.py
+++ b/tests/asgi/tests.py
@@ -1,18 +1,25 @@
 import asyncio
 import sys
 import threading
+from pathlib import Path
 from unittest import skipIf
 
 from asgiref.sync import SyncToAsync
 from asgiref.testing import ApplicationCommunicator
 
+from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
 from django.core.asgi import get_asgi_application
 from django.core.signals import request_finished, request_started
 from django.db import close_old_connections
-from django.test import AsyncRequestFactory, SimpleTestCase, override_settings
+from django.test import (
+    AsyncRequestFactory, SimpleTestCase, modify_settings, override_settings,
+)
+from django.utils.http import http_date
 
 from .urls import test_filename
 
+TEST_STATIC_ROOT = Path(__file__).parent / 'project' / 'static'
+
 
 @skipIf(sys.platform == 'win32' and (3, 8, 0) < sys.version_info < (3, 8, 1), 'https://bugs.python.org/issue38563')
 @override_settings(ROOT_URLCONF='asgi.urls')
@@ -79,6 +86,45 @@ async def test_file_response(self):
         # Allow response.close() to finish.
         await communicator.wait()
 
+    @modify_settings(INSTALLED_APPS={'append': 'django.contrib.staticfiles'})
+    @override_settings(
+        STATIC_URL='/static/',
+        STATIC_ROOT=TEST_STATIC_ROOT,
+        STATICFILES_DIRS=[TEST_STATIC_ROOT],
+        STATICFILES_FINDERS=[
+            'django.contrib.staticfiles.finders.FileSystemFinder',
+        ],
+    )
+    async def test_static_file_response(self):
+        application = ASGIStaticFilesHandler(get_asgi_application())
+        # Construct HTTP request.
+        scope = self.async_request_factory._base_scope(path='/static/file.txt')
+        communicator = ApplicationCommunicator(application, scope)
+        await communicator.send_input({'type': 'http.request'})
+        # Get the file content.
+        file_path = TEST_STATIC_ROOT / 'file.txt'
+        with open(file_path, 'rb') as test_file:
+            test_file_contents = test_file.read()
+        # Read the response.
+        stat = file_path.stat()
+        response_start = await communicator.receive_output()
+        self.assertEqual(response_start['type'], 'http.response.start')
+        self.assertEqual(response_start['status'], 200)
+        self.assertEqual(
+            set(response_start['headers']),
+            {
+                (b'Content-Length', str(len(test_file_contents)).encode('ascii')),
+                (b'Content-Type', b'text/plain'),
+                (b'Content-Disposition', b'inline; filename="file.txt"'),
+                (b'Last-Modified', http_date(stat.st_mtime).encode('ascii')),
+            },
+        )
+        response_body = await communicator.receive_output()
+        self.assertEqual(response_body['type'], 'http.response.body')
+        self.assertEqual(response_body['body'], test_file_contents)
+        # Allow response.close() to finish.
+        await communicator.wait()
+
     async def test_headers(self):
         application = get_asgi_application()
         communicator = ApplicationCommunicator(
diff --git a/tests/staticfiles_tests/test_handlers.py b/tests/staticfiles_tests/test_handlers.py
new file mode 100644
--- /dev/null
+++ b/tests/staticfiles_tests/test_handlers.py
@@ -0,0 +1,22 @@
+from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
+from django.core.handlers.asgi import ASGIHandler
+from django.test import AsyncRequestFactory
+
+from .cases import StaticFilesTestCase
+
+
+class TestASGIStaticFilesHandler(StaticFilesTestCase):
+    async_request_factory = AsyncRequestFactory()
+
+    async def test_get_async_response(self):
+        request = self.async_request_factory.get('/static/test/file.txt')
+        handler = ASGIStaticFilesHandler(ASGIHandler())
+        response = await handler.get_response_async(request)
+        response.close()
+        self.assertEqual(response.status_code, 200)
+
+    async def test_get_async_response_not_found(self):
+        request = self.async_request_factory.get('/static/test/not-found.txt')
+        handler = ASGIStaticFilesHandler(ASGIHandler())
+        response = await handler.get_response_async(request)
+        self.assertEqual(response.status_code, 404)

```

## Test Information

**Tests that should FAIL→PASS**: ["test_get_async_response (staticfiles_tests.test_handlers.TestASGIStaticFilesHandler)", "test_get_async_response_not_found (staticfiles_tests.test_handlers.TestASGIStaticFilesHandler)", "test_static_file_response (asgi.tests.ASGITest)"]

**Tests that should PASS→PASS**: ["test_disconnect (asgi.tests.ASGITest)", "test_file_response (asgi.tests.ASGITest)", "test_get_asgi_application (asgi.tests.ASGITest)", "test_get_query_string (asgi.tests.ASGITest)", "test_headers (asgi.tests.ASGITest)", "test_non_unicode_query_string (asgi.tests.ASGITest)", "test_request_lifecycle_signals_dispatched_with_thread_sensitive (asgi.tests.ASGITest)", "test_wrong_connection_type (asgi.tests.ASGITest)"]

**Base Commit**: 4652f1f0aa459a7b980441d629648707c32e36bf
**Environment Setup Commit**: 65dfb06a1ab56c238cc80f5e1c31f61210c4577d
