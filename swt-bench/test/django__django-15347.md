# django__django-15347

**Repository**: django/django
**Created**: 2022-01-22T01:56:48Z
**Version**: 4.1

## Problem Statement

Messages framework incorrectly serializes/deserializes extra_tags when it's an empty string
Description
	
When a message is serialised and then deserialised with any of the built in storage backends, then extra_tags=="" is converted to extra_tags==None. This is because MessageEncoder checks for the truthyness of extra_tags rather than checking it is not None.
To replicate this bug
>>> from django.conf import settings
>>> settings.configure() # Just to allow the following import
>>> from django.contrib.messages.storage.base import Message
>>> from django.contrib.messages.storage.cookie import MessageEncoder, MessageDecoder
>>> original_message = Message(10, "Here is a message", extra_tags="")
>>> encoded_message = MessageEncoder().encode(original_message)
>>> decoded_message = MessageDecoder().decode(encoded_message)
>>> original_message.extra_tags == ""
True
>>> decoded_message.extra_tags is None
True
Effect of the bug in application behaviour
This error occurred in the wild with a template tag similar to the following:
{% if x not in message.extra_tags %}
When the message was displayed as part of a redirect, it had been serialised and deserialized which meant that extra_tags was None instead of the empty string. This caused an error.
It's important to note that this bug affects all of the standard API (messages.debug, messages.info etc. all have a default value of extra_tags equal to "").


## Patch

```diff

diff --git a/django/contrib/messages/storage/cookie.py b/django/contrib/messages/storage/cookie.py
--- a/django/contrib/messages/storage/cookie.py
+++ b/django/contrib/messages/storage/cookie.py
@@ -19,7 +19,7 @@ def default(self, obj):
             # Using 0/1 here instead of False/True to produce more compact json
             is_safedata = 1 if isinstance(obj.message, SafeData) else 0
             message = [self.message_key, is_safedata, obj.level, obj.message]
-            if obj.extra_tags:
+            if obj.extra_tags is not None:
                 message.append(obj.extra_tags)
             return message
         return super().default(obj)


```

## Test Patch

```diff
diff --git a/tests/messages_tests/test_cookie.py b/tests/messages_tests/test_cookie.py
--- a/tests/messages_tests/test_cookie.py
+++ b/tests/messages_tests/test_cookie.py
@@ -52,6 +52,12 @@ class CookieTests(BaseTests, SimpleTestCase):
     def stored_messages_count(self, storage, response):
         return stored_cookie_messages_count(storage, response)
 
+    def encode_decode(self, *args, **kwargs):
+        storage = self.get_storage()
+        message = Message(constants.DEBUG, *args, **kwargs)
+        encoded = storage._encode(message)
+        return storage._decode(encoded)
+
     def test_get(self):
         storage = self.storage_class(self.get_request())
         # Set initial data.
@@ -168,12 +174,23 @@ def test_safedata(self):
         A message containing SafeData is keeping its safe status when
         retrieved from the message storage.
         """
-        def encode_decode(data):
-            message = Message(constants.DEBUG, data)
-            encoded = storage._encode(message)
-            decoded = storage._decode(encoded)
-            return decoded.message
+        self.assertIsInstance(
+            self.encode_decode(mark_safe('<b>Hello Django!</b>')).message,
+            SafeData,
+        )
+        self.assertNotIsInstance(
+            self.encode_decode('<b>Hello Django!</b>').message,
+            SafeData,
+        )
 
-        storage = self.get_storage()
-        self.assertIsInstance(encode_decode(mark_safe("<b>Hello Django!</b>")), SafeData)
-        self.assertNotIsInstance(encode_decode("<b>Hello Django!</b>"), SafeData)
+    def test_extra_tags(self):
+        """
+        A message's extra_tags attribute is correctly preserved when retrieved
+        from the message storage.
+        """
+        for extra_tags in ['', None, 'some tags']:
+            with self.subTest(extra_tags=extra_tags):
+                self.assertEqual(
+                    self.encode_decode('message', extra_tags=extra_tags).extra_tags,
+                    extra_tags,
+                )

```

## Test Information

**Tests that should FAIL→PASS**: ["A message's extra_tags attribute is correctly preserved when retrieved"]

**Tests that should PASS→PASS**: ["test_add (messages_tests.test_cookie.CookieTests)", "test_add_lazy_translation (messages_tests.test_cookie.CookieTests)", "test_add_update (messages_tests.test_cookie.CookieTests)", "test_context_processor_message_levels (messages_tests.test_cookie.CookieTests)", "CookieStorage honors SESSION_COOKIE_DOMAIN, SESSION_COOKIE_SECURE, and", "test_custom_tags (messages_tests.test_cookie.CookieTests)", "test_default_level (messages_tests.test_cookie.CookieTests)", "test_existing_add (messages_tests.test_cookie.CookieTests)", "test_existing_add_read_update (messages_tests.test_cookie.CookieTests)", "Reading the existing storage doesn't cause the data to be lost.", "test_existing_read_add_update (messages_tests.test_cookie.CookieTests)", "With the message middleware enabled, messages are properly stored and", "test_get (messages_tests.test_cookie.CookieTests)", "test_get_bad_cookie (messages_tests.test_cookie.CookieTests)", "test_high_level (messages_tests.test_cookie.CookieTests)", "A complex nested data structure containing Message", "test_level_tag (messages_tests.test_cookie.CookieTests)", "test_low_level (messages_tests.test_cookie.CookieTests)", "If the data exceeds what is allowed in a cookie, older messages are", "test_message_rfc6265 (messages_tests.test_cookie.CookieTests)", "When the middleware is disabled, an exception is raised when one", "When the middleware is disabled, an exception is not raised", "Messages persist properly when multiple POSTs are made before a GET.", "test_no_update (messages_tests.test_cookie.CookieTests)", "test_repr (messages_tests.test_cookie.CookieTests)", "A message containing SafeData is keeping its safe status when", "test_settings_level (messages_tests.test_cookie.CookieTests)", "test_tags (messages_tests.test_cookie.CookieTests)", "test_with_template_response (messages_tests.test_cookie.CookieTests)"]

**Base Commit**: 7c4f3965098baad2396e24501e09237425a7bd6f
**Environment Setup Commit**: 647480166bfe7532e8c471fef0146e3a17e6c0c9
