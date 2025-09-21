# psf__requests-3362

**Repository**: psf/requests
**Created**: 2016-06-24T13:31:31Z
**Version**: 2.10

## Problem Statement

Uncertain about content/text vs iter_content(decode_unicode=True/False)
When requesting an application/json document, I'm seeing `next(r.iter_content(16*1024, decode_unicode=True))` returning bytes, whereas `r.text` returns unicode. My understanding was that both should return a unicode object. In essence, I thought "iter_content" was equivalent to "iter_text" when decode_unicode was True. Have I misunderstood something? I can provide an example if needed.

For reference, I'm using python 3.5.1 and requests 2.10.0.

Thanks!



## Hints

what does (your response object).encoding return?

There's at least one key difference: `decode_unicode=True` doesn't fall back to `apparent_encoding`, which means it'll never autodetect the encoding. This means if `response.encoding` is None it is a no-op: in fact, it's a no-op that yields bytes.

That behaviour seems genuinely bad to me, so I think we should consider it a bug. I'd rather we had the same logic as in `text` for this.

`r.encoding` returns `None`.

On a related note, `iter_text` might be clearer/more consistent than `iter_content(decode_unicode=True)` if there's room for change in the APIs future (and `iter_content_lines` and `iter_text_lines` I guess), assuming you don't see that as bloat.

@mikepelley The API is presently frozen so I don't think we'll be adding those three methods. Besides, `iter_text` likely wouldn't provide much extra value outside of calling `iter_content(decode_unicode=True)`.


## Patch

```diff

diff --git a/requests/utils.py b/requests/utils.py
--- a/requests/utils.py
+++ b/requests/utils.py
@@ -358,13 +358,20 @@ def get_encoding_from_headers(headers):
 
 def stream_decode_response_unicode(iterator, r):
     """Stream decodes a iterator."""
+    encoding = r.encoding
 
-    if r.encoding is None:
-        for item in iterator:
-            yield item
-        return
+    if encoding is None:
+        encoding = r.apparent_encoding
+
+    try:
+        decoder = codecs.getincrementaldecoder(encoding)(errors='replace')
+    except (LookupError, TypeError):
+        # A LookupError is raised if the encoding was not found which could
+        # indicate a misspelling or similar mistake.
+        #
+        # A TypeError can be raised if encoding is None
+        raise UnicodeError("Unable to decode contents with encoding %s." % encoding)
 
-    decoder = codecs.getincrementaldecoder(r.encoding)(errors='replace')
     for chunk in iterator:
         rv = decoder.decode(chunk)
         if rv:


```

## Test Patch

```diff
diff --git a/tests/test_requests.py b/tests/test_requests.py
--- a/tests/test_requests.py
+++ b/tests/test_requests.py
@@ -980,6 +980,13 @@ def test_response_decode_unicode(self):
         chunks = r.iter_content(decode_unicode=True)
         assert all(isinstance(chunk, str) for chunk in chunks)
 
+        # check for encoding value of None
+        r = requests.Response()
+        r.raw = io.BytesIO(b'the content')
+        r.encoding = None
+        chunks = r.iter_content(decode_unicode=True)
+        assert all(isinstance(chunk, str) for chunk in chunks)
+
     def test_response_chunk_size_int(self):
         """Ensure that chunk_size is passed as an integer, otherwise
         raise a TypeError.

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/test_requests.py::TestRequests::test_response_decode_unicode"]

**Tests that should PASS→PASS**: ["tests/test_requests.py::TestRequests::test_entry_points", "tests/test_requests.py::TestRequests::test_invalid_url[MissingSchema-hiwpefhipowhefopw]", "tests/test_requests.py::TestRequests::test_invalid_url[InvalidSchema-localhost:3128]", "tests/test_requests.py::TestRequests::test_invalid_url[InvalidSchema-localhost.localdomain:3128/]", "tests/test_requests.py::TestRequests::test_invalid_url[InvalidSchema-10.122.1.1:3128/]", "tests/test_requests.py::TestRequests::test_invalid_url[InvalidURL-http://]", "tests/test_requests.py::TestRequests::test_basic_building", "tests/test_requests.py::TestRequests::test_path_is_not_double_encoded", "tests/test_requests.py::TestRequests::test_params_are_added_before_fragment[http://example.com/path#fragment-http://example.com/path?a=b#fragment]", "tests/test_requests.py::TestRequests::test_params_are_added_before_fragment[http://example.com/path?key=value#fragment-http://example.com/path?key=value&a=b#fragment]", "tests/test_requests.py::TestRequests::test_params_original_order_is_preserved_by_default", "tests/test_requests.py::TestRequests::test_params_bytes_are_encoded", "tests/test_requests.py::TestRequests::test_binary_put", "tests/test_requests.py::TestRequests::test_errors[http://doesnotexist.google.com-ConnectionError]", "tests/test_requests.py::TestRequests::test_errors[http://localhost:1-ConnectionError]", "tests/test_requests.py::TestRequests::test_errors[http://fe80::5054:ff:fe5a:fc0-InvalidURL]", "tests/test_requests.py::TestRequests::test_proxy_error", "tests/test_requests.py::TestRequests::test_non_prepared_request_error", "tests/test_requests.py::TestRequests::test_prepare_request_with_bytestring_url", "tests/test_requests.py::TestRequests::test_links", "tests/test_requests.py::TestRequests::test_cookie_parameters", "tests/test_requests.py::TestRequests::test_cookie_as_dict_keeps_len", "tests/test_requests.py::TestRequests::test_cookie_as_dict_keeps_items", "tests/test_requests.py::TestRequests::test_cookie_as_dict_keys", "tests/test_requests.py::TestRequests::test_cookie_as_dict_values", "tests/test_requests.py::TestRequests::test_cookie_as_dict_items", "tests/test_requests.py::TestRequests::test_cookie_duplicate_names_different_domains", "tests/test_requests.py::TestRequests::test_cookie_duplicate_names_raises_cookie_conflict_error", "tests/test_requests.py::TestRequests::test_response_is_iterable", "tests/test_requests.py::TestRequests::test_response_chunk_size_int", "tests/test_requests.py::TestRequests::test_http_error", "tests/test_requests.py::TestRequests::test_transport_adapter_ordering", "tests/test_requests.py::TestRequests::test_long_authinfo_in_url", "tests/test_requests.py::TestRequests::test_nonhttp_schemes_dont_check_URLs", "tests/test_requests.py::TestRequests::test_basic_auth_str_is_always_native", "tests/test_requests.py::TestCaseInsensitiveDict::test_init[cid0]", "tests/test_requests.py::TestCaseInsensitiveDict::test_init[cid1]", "tests/test_requests.py::TestCaseInsensitiveDict::test_init[cid2]", "tests/test_requests.py::TestCaseInsensitiveDict::test_docstring_example", "tests/test_requests.py::TestCaseInsensitiveDict::test_len", "tests/test_requests.py::TestCaseInsensitiveDict::test_getitem", "tests/test_requests.py::TestCaseInsensitiveDict::test_fixes_649", "tests/test_requests.py::TestCaseInsensitiveDict::test_delitem", "tests/test_requests.py::TestCaseInsensitiveDict::test_contains", "tests/test_requests.py::TestCaseInsensitiveDict::test_get", "tests/test_requests.py::TestCaseInsensitiveDict::test_update", "tests/test_requests.py::TestCaseInsensitiveDict::test_update_retains_unchanged", "tests/test_requests.py::TestCaseInsensitiveDict::test_iter", "tests/test_requests.py::TestCaseInsensitiveDict::test_equality", "tests/test_requests.py::TestCaseInsensitiveDict::test_setdefault", "tests/test_requests.py::TestCaseInsensitiveDict::test_lower_items", "tests/test_requests.py::TestCaseInsensitiveDict::test_preserve_key_case", "tests/test_requests.py::TestCaseInsensitiveDict::test_preserve_last_key_case", "tests/test_requests.py::TestCaseInsensitiveDict::test_copy", "tests/test_requests.py::TestMorselToCookieExpires::test_expires_valid_str", "tests/test_requests.py::TestMorselToCookieExpires::test_expires_invalid_int[100-TypeError]", "tests/test_requests.py::TestMorselToCookieExpires::test_expires_invalid_int[woops-ValueError]", "tests/test_requests.py::TestMorselToCookieExpires::test_expires_none", "tests/test_requests.py::TestMorselToCookieMaxAge::test_max_age_valid_int", "tests/test_requests.py::TestMorselToCookieMaxAge::test_max_age_invalid_str", "tests/test_requests.py::TestTimeout::test_connect_timeout", "tests/test_requests.py::TestTimeout::test_total_timeout_connect", "tests/test_requests.py::test_json_encodes_as_bytes", "tests/test_requests.py::test_proxy_env_vars_override_default[http_proxy-http://example.com-socks5://proxy.com:9876]", "tests/test_requests.py::test_proxy_env_vars_override_default[https_proxy-https://example.com-socks5://proxy.com:9876]", "tests/test_requests.py::test_proxy_env_vars_override_default[all_proxy-http://example.com-socks5://proxy.com:9876]", "tests/test_requests.py::test_proxy_env_vars_override_default[all_proxy-https://example.com-socks5://proxy.com:9876]", "tests/test_requests.py::test_data_argument_accepts_tuples[data0]", "tests/test_requests.py::test_data_argument_accepts_tuples[data1]", "tests/test_requests.py::test_data_argument_accepts_tuples[data2]", "tests/test_requests.py::test_prepared_copy[None]", "tests/test_requests.py::test_prepared_copy[kwargs1]", "tests/test_requests.py::test_prepared_copy[kwargs2]", "tests/test_requests.py::test_prepared_copy[kwargs3]", "tests/test_requests.py::test_vendor_aliases"]

**Base Commit**: 36453b95b13079296776d11b09cab2567ea3e703
**Environment Setup Commit**: 36453b95b13079296776d11b09cab2567ea3e703
