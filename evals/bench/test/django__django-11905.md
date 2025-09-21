# django__django-11905

**Repository**: django/django
**Created**: 2019-10-11T18:19:39Z
**Version**: 3.1

## Problem Statement

Prevent using __isnull lookup with non-boolean value.
Description
	 
		(last modified by Mariusz Felisiak)
	 
__isnull should not allow for non-boolean values. Using truthy/falsey doesn't promote INNER JOIN to an OUTER JOIN but works fine for a simple queries. Using non-boolean values is ​undocumented and untested. IMO we should raise an error for non-boolean values to avoid confusion and for consistency.


## Hints

PR here: ​https://github.com/django/django/pull/11873
After the reconsideration I don't think that we should change this ​documented behavior (that is in Django from the very beginning). __isnull lookup expects boolean values in many places and IMO it would be confusing if we'll allow for truthy/falsy values, e.g. take a look at these examples field__isnull='false' or field__isnull='true' (both would return the same result). You can always call bool() on a right hand side. Sorry for my previous acceptation (I shouldn't triage tickets in the weekend).
Replying to felixxm: After the reconsideration I don't think that we should change this ​documented behavior (that is in Django from the very beginning). __isnull lookup expects boolean values in many places and IMO it would be confusing if we'll allow for truthy/falsy values, e.g. take a look at these examples field__isnull='false' or field__isnull='true' (both would return the same result). You can always call bool() on a right hand side. Sorry for my previous acceptation (I shouldn't triage tickets in the weekend). I understand your point. But is there anything we can do to avoid people falling for the same pitfall I did? The problem, in my opinion, is that it works fine for simple queries but as soon as you add a join that needs promotion it will break, silently. Maybe we should make it raise an exception when a non-boolean is passed? One valid example is to have a class that implements __bool__. You can see here ​https://github.com/django/django/blob/d9881a025c15d87b2a7883ee50771117450ea90d/django/db/models/lookups.py#L465-L470 that non-bool value is converted to IS NULL and IS NOT NULL already using the truthy/falsy values. IMO it would be confusing if we'll allow for truthy/falsy values, e.g. take a look at these examples fieldisnull='false' or fieldisnull='true' (both would return the same result). This is already the case. It just is inconsistent, in lookups.py field__isnull='false' will be a positive condition but on the query.py it will be the negative condition.
Maybe adding a note on the documentation? something like: "Although it might seem like it will work with non-bool fields, this is not supported and can lead to inconsistent behaviours"
Agreed, we should raise an error for non-boolean values, e.g. diff --git a/django/db/models/lookups.py b/django/db/models/lookups.py index 9344979c56..fc4a38c4fe 100644 --- a/django/db/models/lookups.py +++ b/django/db/models/lookups.py @@ -463,6 +463,11 @@ class IsNull(BuiltinLookup): prepare_rhs = False def as_sql(self, compiler, connection): + if not isinstance(self.rhs, bool): + raise ValueError( + 'The QuerySet value for an isnull lookup must be True or ' + 'False.' + ) sql, params = compiler.compile(self.lhs) if self.rhs: return "%s IS NULL" % sql, params I changed the ticket description.
Thanks, I'll work on it! Wouldn't that possibly break backward compatibility? I'm not familiar with how Django moves in that regard.
We can add a release note in "Backwards incompatible changes" or deprecate this and remove in Django 4.0. I have to thing about it, please give me a day, maybe I will change my mind :)
No problem. Thanks for taking the time to look into this!
Another interesting example related to this: As an anecdote, I've also got bitten by this possibility. An attempt to write WHERE (field IS NULL) = boolean_field as .filter(field__isnull=F('boolean_field')) didn't go as I expected. Alexandr Aktsipetrov -- ​https://groups.google.com/forum/#!msg/django-developers/AhY2b3rxkfA/0sz3hNanCgAJ This example will generate the WHERE .... IS NULL. I guess we also would want an exception thrown here.
André, IMO we should deprecate using non-boolean values in Django 3.1 (RemovedInDjango40Warning) and remove in Django 4.0 (even if it is untested and undocumented). I can imagine that a lot of people use e.g. 1 and 0 instead of booleans. Attached diff fixes also issue with passing a F() expression. def as_sql(self, compiler, connection): if not isinstance(self.rhs, bool): raise RemovedInDjango40Warning(...) ....
Replying to felixxm: André, IMO we should deprecate using non-boolean values in Django 3.1 (RemovedInDjango40Warning) and remove in Django 4.0 (even if it is untested and undocumented). I can imagine that a lot of people use e.g. 1 and 0 instead of booleans. Attached diff fixes also issue with passing a F() expression. def as_sql(self, compiler, connection): if not isinstance(self.rhs, bool): raise RemovedInDjango40Warning(...) .... Sound like a good plan. Not super familiar with the branch structure of Django. So, I guess the path to follow is to make a PR to master adding the deprecation warning and eventually when master is 4.x we create the PR raising the ValueError. Is that right? Thanks!
André, yes mostly. You can find more details about that ​from the documentation.

## Patch

```diff

diff --git a/django/db/models/lookups.py b/django/db/models/lookups.py
--- a/django/db/models/lookups.py
+++ b/django/db/models/lookups.py
@@ -1,5 +1,6 @@
 import itertools
 import math
+import warnings
 from copy import copy
 
 from django.core.exceptions import EmptyResultSet
@@ -9,6 +10,7 @@
 )
 from django.db.models.query_utils import RegisterLookupMixin
 from django.utils.datastructures import OrderedSet
+from django.utils.deprecation import RemovedInDjango40Warning
 from django.utils.functional import cached_property
 
 
@@ -463,6 +465,17 @@ class IsNull(BuiltinLookup):
     prepare_rhs = False
 
     def as_sql(self, compiler, connection):
+        if not isinstance(self.rhs, bool):
+            # When the deprecation ends, replace with:
+            # raise ValueError(
+            #     'The QuerySet value for an isnull lookup must be True or '
+            #     'False.'
+            # )
+            warnings.warn(
+                'Using a non-boolean value for an isnull lookup is '
+                'deprecated, use True or False instead.',
+                RemovedInDjango40Warning,
+            )
         sql, params = compiler.compile(self.lhs)
         if self.rhs:
             return "%s IS NULL" % sql, params


```

## Test Patch

```diff
diff --git a/tests/lookup/models.py b/tests/lookup/models.py
--- a/tests/lookup/models.py
+++ b/tests/lookup/models.py
@@ -96,3 +96,15 @@ class Product(models.Model):
 class Stock(models.Model):
     product = models.ForeignKey(Product, models.CASCADE)
     qty_available = models.DecimalField(max_digits=6, decimal_places=2)
+
+
+class Freebie(models.Model):
+    gift_product = models.ForeignKey(Product, models.CASCADE)
+    stock_id = models.IntegerField(blank=True, null=True)
+
+    stock = models.ForeignObject(
+        Stock,
+        from_fields=['stock_id', 'gift_product'],
+        to_fields=['id', 'product'],
+        on_delete=models.CASCADE,
+    )
diff --git a/tests/lookup/tests.py b/tests/lookup/tests.py
--- a/tests/lookup/tests.py
+++ b/tests/lookup/tests.py
@@ -9,9 +9,10 @@
 from django.db.models.expressions import Exists, OuterRef
 from django.db.models.functions import Substr
 from django.test import TestCase, skipUnlessDBFeature
+from django.utils.deprecation import RemovedInDjango40Warning
 
 from .models import (
-    Article, Author, Game, IsNullWithNoneAsRHS, Player, Season, Tag,
+    Article, Author, Freebie, Game, IsNullWithNoneAsRHS, Player, Season, Tag,
 )
 
 
@@ -969,3 +970,24 @@ def test_exact_query_rhs_with_selected_columns(self):
         ).values('max_id')
         authors = Author.objects.filter(id=authors_max_ids[:1])
         self.assertEqual(authors.get(), newest_author)
+
+    def test_isnull_non_boolean_value(self):
+        # These tests will catch ValueError in Django 4.0 when using
+        # non-boolean values for an isnull lookup becomes forbidden.
+        # msg = (
+        #     'The QuerySet value for an isnull lookup must be True or False.'
+        # )
+        msg = (
+            'Using a non-boolean value for an isnull lookup is deprecated, '
+            'use True or False instead.'
+        )
+        tests = [
+            Author.objects.filter(alias__isnull=1),
+            Article.objects.filter(author__isnull=1),
+            Season.objects.filter(games__isnull=1),
+            Freebie.objects.filter(stock__isnull=1),
+        ]
+        for qs in tests:
+            with self.subTest(qs=qs):
+                with self.assertWarnsMessage(RemovedInDjango40Warning, msg):
+                    qs.exists()

```

## Test Information

**Tests that should FAIL→PASS**: ["test_isnull_non_boolean_value (lookup.tests.LookupTests)", "test_iterator (lookup.tests.LookupTests)"]

**Tests that should PASS→PASS**: ["test_chain_date_time_lookups (lookup.tests.LookupTests)", "test_count (lookup.tests.LookupTests)", "test_custom_field_none_rhs (lookup.tests.LookupTests)", "Lookup.can_use_none_as_rhs=True allows None as a lookup value.", "test_error_messages (lookup.tests.LookupTests)", "test_escaping (lookup.tests.LookupTests)", "test_exact_exists (lookup.tests.LookupTests)", "Transforms are used for __exact=None.", "test_exact_query_rhs_with_selected_columns (lookup.tests.LookupTests)", "test_exact_sliced_queryset_limit_one (lookup.tests.LookupTests)", "test_exact_sliced_queryset_limit_one_offset (lookup.tests.LookupTests)", "test_exact_sliced_queryset_not_limited_to_one (lookup.tests.LookupTests)", "test_exclude (lookup.tests.LookupTests)", "test_exists (lookup.tests.LookupTests)", "test_get_next_previous_by (lookup.tests.LookupTests)", "test_in (lookup.tests.LookupTests)", "test_in_bulk (lookup.tests.LookupTests)", "test_in_bulk_lots_of_ids (lookup.tests.LookupTests)", "test_in_bulk_non_unique_field (lookup.tests.LookupTests)", "test_in_bulk_with_field (lookup.tests.LookupTests)", "test_in_different_database (lookup.tests.LookupTests)", "test_in_keeps_value_ordering (lookup.tests.LookupTests)", "test_lookup_collision (lookup.tests.LookupTests)", "test_lookup_date_as_str (lookup.tests.LookupTests)", "test_lookup_int_as_str (lookup.tests.LookupTests)", "test_nested_outerref_lhs (lookup.tests.LookupTests)", "test_none (lookup.tests.LookupTests)", "test_nonfield_lookups (lookup.tests.LookupTests)", "test_pattern_lookups_with_substr (lookup.tests.LookupTests)", "test_regex (lookup.tests.LookupTests)", "test_regex_backreferencing (lookup.tests.LookupTests)", "test_regex_non_ascii (lookup.tests.LookupTests)", "test_regex_non_string (lookup.tests.LookupTests)", "test_regex_null (lookup.tests.LookupTests)", "test_relation_nested_lookup_error (lookup.tests.LookupTests)", "test_unsupported_lookups (lookup.tests.LookupTests)", "test_values (lookup.tests.LookupTests)", "test_values_list (lookup.tests.LookupTests)"]

**Base Commit**: 2f72480fbd27896c986c45193e1603e35c0b19a7
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
