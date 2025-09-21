# django__django-11133

**Repository**: django/django
**Created**: 2019-03-27T06:48:09Z
**Version**: 3.0

## Problem Statement

HttpResponse doesn't handle memoryview objects
Description
	
I am trying to write a BinaryField retrieved from the database into a HttpResponse. When the database is Sqlite this works correctly, but Postgresql returns the contents of the field as a memoryview object and it seems like current Django doesn't like this combination:
from django.http import HttpResponse																	 
# String content
response = HttpResponse("My Content")																			
response.content																								 
# Out: b'My Content'
# This is correct
# Bytes content
response = HttpResponse(b"My Content")																		 
response.content																								 
# Out: b'My Content'
# This is also correct
# memoryview content
response = HttpResponse(memoryview(b"My Content"))															 
response.content
# Out: b'<memory at 0x7fcc47ab2648>'
# This is not correct, I am expecting b'My Content'


## Hints

I guess HttpResponseBase.make_bytes ​could be adapted to deal with memoryview objects by casting them to bytes. In all cases simply wrapping the memoryview in bytes works as a workaround HttpResponse(bytes(model.binary_field)).
The fact make_bytes would still use force_bytes if da56e1bac6449daef9aeab8d076d2594d9fd5b44 didn't refactor it and that d680a3f4477056c69629b0421db4bb254b8c69d0 added memoryview support to force_bytes strengthen my assumption that make_bytes should be adjusted as well.
I'll try to work on this.

## Patch

```diff

diff --git a/django/http/response.py b/django/http/response.py
--- a/django/http/response.py
+++ b/django/http/response.py
@@ -229,7 +229,7 @@ def make_bytes(self, value):
         # Handle string types -- we can't rely on force_bytes here because:
         # - Python attempts str conversion first
         # - when self._charset != 'utf-8' it re-encodes the content
-        if isinstance(value, bytes):
+        if isinstance(value, (bytes, memoryview)):
             return bytes(value)
         if isinstance(value, str):
             return bytes(value.encode(self.charset))


```

## Test Patch

```diff
diff --git a/tests/httpwrappers/tests.py b/tests/httpwrappers/tests.py
--- a/tests/httpwrappers/tests.py
+++ b/tests/httpwrappers/tests.py
@@ -366,6 +366,10 @@ def test_non_string_content(self):
         r.content = 12345
         self.assertEqual(r.content, b'12345')
 
+    def test_memoryview_content(self):
+        r = HttpResponse(memoryview(b'memoryview'))
+        self.assertEqual(r.content, b'memoryview')
+
     def test_iter_content(self):
         r = HttpResponse(['abc', 'def', 'ghi'])
         self.assertEqual(r.content, b'abcdefghi')

```

## Test Information

**Tests that should FAIL→PASS**: ["test_memoryview_content (httpwrappers.tests.HttpResponseTests)"]

**Tests that should PASS→PASS**: ["test_streaming_response (httpwrappers.tests.StreamingHttpResponseTests)", "test_cookie_edgecases (httpwrappers.tests.CookieTests)", "Semicolons and commas are decoded.", "Semicolons and commas are encoded.", "test_httponly_after_load (httpwrappers.tests.CookieTests)", "test_invalid_cookies (httpwrappers.tests.CookieTests)", "test_load_dict (httpwrappers.tests.CookieTests)", "test_nonstandard_keys (httpwrappers.tests.CookieTests)", "test_pickle (httpwrappers.tests.CookieTests)", "test_python_cookies (httpwrappers.tests.CookieTests)", "test_repeated_nonstandard_keys (httpwrappers.tests.CookieTests)", "test_samesite (httpwrappers.tests.CookieTests)", "test_response (httpwrappers.tests.FileCloseTests)", "test_streaming_response (httpwrappers.tests.FileCloseTests)", "test_json_response_custom_encoder (httpwrappers.tests.JsonResponseTests)", "test_json_response_list (httpwrappers.tests.JsonResponseTests)", "test_json_response_non_ascii (httpwrappers.tests.JsonResponseTests)", "test_json_response_passing_arguments_to_json_dumps (httpwrappers.tests.JsonResponseTests)", "test_json_response_raises_type_error_with_default_setting (httpwrappers.tests.JsonResponseTests)", "test_json_response_text (httpwrappers.tests.JsonResponseTests)", "test_json_response_uuid (httpwrappers.tests.JsonResponseTests)", "test_invalid_redirect_repr (httpwrappers.tests.HttpResponseSubclassesTests)", "test_not_allowed (httpwrappers.tests.HttpResponseSubclassesTests)", "test_not_allowed_repr (httpwrappers.tests.HttpResponseSubclassesTests)", "test_not_allowed_repr_no_content_type (httpwrappers.tests.HttpResponseSubclassesTests)", "test_not_modified (httpwrappers.tests.HttpResponseSubclassesTests)", "test_not_modified_repr (httpwrappers.tests.HttpResponseSubclassesTests)", "test_redirect (httpwrappers.tests.HttpResponseSubclassesTests)", "Make sure HttpResponseRedirect works with lazy strings.", "test_redirect_repr (httpwrappers.tests.HttpResponseSubclassesTests)", "test_dict_behavior (httpwrappers.tests.HttpResponseTests)", "test_file_interface (httpwrappers.tests.HttpResponseTests)", "test_headers_type (httpwrappers.tests.HttpResponseTests)", "test_iter_content (httpwrappers.tests.HttpResponseTests)", "test_iterator_isnt_rewound (httpwrappers.tests.HttpResponseTests)", "test_lazy_content (httpwrappers.tests.HttpResponseTests)", "test_long_line (httpwrappers.tests.HttpResponseTests)", "test_newlines_in_headers (httpwrappers.tests.HttpResponseTests)", "test_non_string_content (httpwrappers.tests.HttpResponseTests)", "test_stream_interface (httpwrappers.tests.HttpResponseTests)", "test_unsafe_redirect (httpwrappers.tests.HttpResponseTests)", "test_basic_mutable_operations (httpwrappers.tests.QueryDictTests)", "test_create_with_no_args (httpwrappers.tests.QueryDictTests)", "test_duplicates_in_fromkeys_iterable (httpwrappers.tests.QueryDictTests)", "test_fromkeys_empty_iterable (httpwrappers.tests.QueryDictTests)", "test_fromkeys_is_immutable_by_default (httpwrappers.tests.QueryDictTests)", "test_fromkeys_mutable_override (httpwrappers.tests.QueryDictTests)", "test_fromkeys_noniterable (httpwrappers.tests.QueryDictTests)", "test_fromkeys_with_nondefault_encoding (httpwrappers.tests.QueryDictTests)", "test_fromkeys_with_nonempty_value (httpwrappers.tests.QueryDictTests)", "test_immutability (httpwrappers.tests.QueryDictTests)", "test_immutable_basic_operations (httpwrappers.tests.QueryDictTests)", "test_immutable_get_with_default (httpwrappers.tests.QueryDictTests)", "test_missing_key (httpwrappers.tests.QueryDictTests)", "Test QueryDict with two key/value pairs with same keys.", "A copy of a QueryDict is mutable.", "test_mutable_delete (httpwrappers.tests.QueryDictTests)", "#13572 - QueryDict with a non-default encoding", "test_pickle (httpwrappers.tests.QueryDictTests)", "test_querydict_fromkeys (httpwrappers.tests.QueryDictTests)", "Test QueryDict with one key/value pair", "Regression test for #8278: QueryDict.update(QueryDict)", "test_urlencode (httpwrappers.tests.QueryDictTests)", "test_urlencode_int (httpwrappers.tests.QueryDictTests)"]

**Base Commit**: 879cc3da6249e920b8d54518a0ae06de835d7373
**Environment Setup Commit**: 419a78300f7cd27611196e1e464d50fd0385ff27
