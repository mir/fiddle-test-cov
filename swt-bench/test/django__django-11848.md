# django__django-11848

**Repository**: django/django
**Created**: 2019-09-28T04:28:22Z
**Version**: 3.1

## Problem Statement

django.utils.http.parse_http_date two digit year check is incorrect
Description
	 
		(last modified by Ad Timmering)
	 
RFC 850 does not mention this, but in RFC 7231 (and there's something similar in RFC 2822), there's the following quote:
Recipients of a timestamp value in rfc850-date format, which uses a
two-digit year, MUST interpret a timestamp that appears to be more
than 50 years in the future as representing the most recent year in
the past that had the same last two digits.
Current logic is hard coded to consider 0-69 to be in 2000-2069, and 70-99 to be 1970-1999, instead of comparing versus the current year.


## Hints

Accepted, however I don't think your patch is correct. The check should be relative to the current year, if I read the RFC quote correctly.
Created a pull request: Created a pull request: ​https://github.com/django/django/pull/9214
Still some suggested edits on the PR.
I added regression test that fails with old code (test_parsing_rfc850_year_69), updated commit message to hopefully follow the guidelines, and added additional comments about the change. Squashed commits as well. Could you review the pull request again?
sent new pull request
This is awaiting for changes from Tim's feedback on PR. (Please uncheck "Patch needs improvement" again when that's done. 🙂)
As this issue hasn't received any updates in the last 8 months, may I work on this ticket?
Go for it, I don't think I will have time to finish it.
Thanks, I'll pick up from where you left off in the PR and make the recommended changes on a new PR.
Tameesh Biswas Are you working on this ?
Yes, I am.
I've just picked up from the previous PR and opened a new PR here: ​https://github.com/django/django/pull/10749 It adds regression tests in the first commit that pass without applying the fix and adds the fix with another test-case that only passes with the fix applied. Could you please review the changes?
Tameesh, I left a comment on the PR regarding the use of non-UTC today.
As an issue haven't received an update for 4 months, I'm taking it over (djangocon europe 2019 sprint day 1).
Created new PR: ​https://github.com/django/django/pull/11212
I think an earlier comment by Simon Charette (about using a fixed year in the tests) still applies to the new PR; I've added it.
Taking the liberty to reassign due to inactivity (6 months) and adding a pull request with revised code and addressing feedback on prior PRs. Please add give your comments for any concerns:) PR => ​https://github.com/django/django/pull/11848 Year is now checked in relation to current year, rolling over to the past if more than 50 years in the future Test now uses a patched version of datetime.datetime to pin to a specific year and have static test cases, addressing feedback from charettes@ on PR 10749 in Dec 2018.

## Patch

```diff

diff --git a/django/utils/http.py b/django/utils/http.py
--- a/django/utils/http.py
+++ b/django/utils/http.py
@@ -176,10 +176,14 @@ def parse_http_date(date):
     try:
         year = int(m.group('year'))
         if year < 100:
-            if year < 70:
-                year += 2000
+            current_year = datetime.datetime.utcnow().year
+            current_century = current_year - (current_year % 100)
+            if year - (current_year % 100) > 50:
+                # year that appears to be more than 50 years in the future are
+                # interpreted as representing the past.
+                year += current_century - 100
             else:
-                year += 1900
+                year += current_century
         month = MONTHS.index(m.group('mon').lower()) + 1
         day = int(m.group('day'))
         hour = int(m.group('hour'))


```

## Test Patch

```diff
diff --git a/tests/utils_tests/test_http.py b/tests/utils_tests/test_http.py
--- a/tests/utils_tests/test_http.py
+++ b/tests/utils_tests/test_http.py
@@ -1,5 +1,6 @@
 import unittest
 from datetime import datetime
+from unittest import mock
 
 from django.test import SimpleTestCase, ignore_warnings
 from django.utils.datastructures import MultiValueDict
@@ -316,9 +317,27 @@ def test_parsing_rfc1123(self):
         parsed = parse_http_date('Sun, 06 Nov 1994 08:49:37 GMT')
         self.assertEqual(datetime.utcfromtimestamp(parsed), datetime(1994, 11, 6, 8, 49, 37))
 
-    def test_parsing_rfc850(self):
-        parsed = parse_http_date('Sunday, 06-Nov-94 08:49:37 GMT')
-        self.assertEqual(datetime.utcfromtimestamp(parsed), datetime(1994, 11, 6, 8, 49, 37))
+    @mock.patch('django.utils.http.datetime.datetime')
+    def test_parsing_rfc850(self, mocked_datetime):
+        mocked_datetime.side_effect = datetime
+        mocked_datetime.utcnow = mock.Mock()
+        utcnow_1 = datetime(2019, 11, 6, 8, 49, 37)
+        utcnow_2 = datetime(2020, 11, 6, 8, 49, 37)
+        utcnow_3 = datetime(2048, 11, 6, 8, 49, 37)
+        tests = (
+            (utcnow_1, 'Tuesday, 31-Dec-69 08:49:37 GMT', datetime(2069, 12, 31, 8, 49, 37)),
+            (utcnow_1, 'Tuesday, 10-Nov-70 08:49:37 GMT', datetime(1970, 11, 10, 8, 49, 37)),
+            (utcnow_1, 'Sunday, 06-Nov-94 08:49:37 GMT', datetime(1994, 11, 6, 8, 49, 37)),
+            (utcnow_2, 'Wednesday, 31-Dec-70 08:49:37 GMT', datetime(2070, 12, 31, 8, 49, 37)),
+            (utcnow_2, 'Friday, 31-Dec-71 08:49:37 GMT', datetime(1971, 12, 31, 8, 49, 37)),
+            (utcnow_3, 'Sunday, 31-Dec-00 08:49:37 GMT', datetime(2000, 12, 31, 8, 49, 37)),
+            (utcnow_3, 'Friday, 31-Dec-99 08:49:37 GMT', datetime(1999, 12, 31, 8, 49, 37)),
+        )
+        for utcnow, rfc850str, expected_date in tests:
+            with self.subTest(rfc850str=rfc850str):
+                mocked_datetime.utcnow.return_value = utcnow
+                parsed = parse_http_date(rfc850str)
+                self.assertEqual(datetime.utcfromtimestamp(parsed), expected_date)
 
     def test_parsing_asctime(self):
         parsed = parse_http_date('Sun Nov  6 08:49:37 1994')

```

## Test Information

**Tests that should FAIL→PASS**: ["test_parsing_rfc850 (utils_tests.test_http.HttpDateProcessingTests)", "test_parsing_year_less_than_70 (utils_tests.test_http.HttpDateProcessingTests)"]

**Tests that should PASS→PASS**: ["test_input_too_large (utils_tests.test_http.Base36IntTests)", "test_invalid_literal (utils_tests.test_http.Base36IntTests)", "test_negative_input (utils_tests.test_http.Base36IntTests)", "test_roundtrip (utils_tests.test_http.Base36IntTests)", "test_to_base36_errors (utils_tests.test_http.Base36IntTests)", "test_to_int_errors (utils_tests.test_http.Base36IntTests)", "test_values (utils_tests.test_http.Base36IntTests)", "test (utils_tests.test_http.EscapeLeadingSlashesTests)", "test_quote (utils_tests.test_http.URLQuoteTests)", "test_quote_plus (utils_tests.test_http.URLQuoteTests)", "test_unquote (utils_tests.test_http.URLQuoteTests)", "test_unquote_plus (utils_tests.test_http.URLQuoteTests)", "test_parsing (utils_tests.test_http.ETagProcessingTests)", "test_quoting (utils_tests.test_http.ETagProcessingTests)", "test_allowed_hosts_str (utils_tests.test_http.IsSafeURLTests)", "test_bad_urls (utils_tests.test_http.IsSafeURLTests)", "test_basic_auth (utils_tests.test_http.IsSafeURLTests)", "test_good_urls (utils_tests.test_http.IsSafeURLTests)", "test_is_safe_url_deprecated (utils_tests.test_http.IsSafeURLTests)", "test_no_allowed_hosts (utils_tests.test_http.IsSafeURLTests)", "test_secure_param_https_urls (utils_tests.test_http.IsSafeURLTests)", "test_secure_param_non_https_urls (utils_tests.test_http.IsSafeURLTests)", "test_bad (utils_tests.test_http.IsSameDomainTests)", "test_good (utils_tests.test_http.IsSameDomainTests)", "test_roundtrip (utils_tests.test_http.URLSafeBase64Tests)", "test_http_date (utils_tests.test_http.HttpDateProcessingTests)", "test_parsing_asctime (utils_tests.test_http.HttpDateProcessingTests)", "test_parsing_rfc1123 (utils_tests.test_http.HttpDateProcessingTests)", "test_custom_iterable_not_doseq (utils_tests.test_http.URLEncodeTests)", "test_dict (utils_tests.test_http.URLEncodeTests)", "test_dict_containing_empty_sequence_doseq (utils_tests.test_http.URLEncodeTests)", "test_dict_containing_sequence_doseq (utils_tests.test_http.URLEncodeTests)", "test_dict_containing_sequence_not_doseq (utils_tests.test_http.URLEncodeTests)", "test_dict_containing_tuple_not_doseq (utils_tests.test_http.URLEncodeTests)", "test_dict_with_bytearray (utils_tests.test_http.URLEncodeTests)", "test_dict_with_bytes_values (utils_tests.test_http.URLEncodeTests)", "test_dict_with_sequence_of_bytes (utils_tests.test_http.URLEncodeTests)", "test_generator (utils_tests.test_http.URLEncodeTests)", "test_multivaluedict (utils_tests.test_http.URLEncodeTests)", "test_none (utils_tests.test_http.URLEncodeTests)", "test_none_in_generator (utils_tests.test_http.URLEncodeTests)", "test_none_in_sequence (utils_tests.test_http.URLEncodeTests)", "test_tuples (utils_tests.test_http.URLEncodeTests)"]

**Base Commit**: f0adf3b9b7a19cdee05368ff0c0c2d087f011180
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
