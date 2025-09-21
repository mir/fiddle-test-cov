# django__django-11797

**Repository**: django/django
**Created**: 2019-09-20T02:23:19Z
**Version**: 3.1

## Problem Statement

Filtering on query result overrides GROUP BY of internal query
Description
	
from django.contrib.auth import models
a = models.User.objects.filter(email__isnull=True).values('email').annotate(m=Max('id')).values('m')
print(a.query) # good
# SELECT MAX("auth_user"."id") AS "m" FROM "auth_user" WHERE "auth_user"."email" IS NULL GROUP BY "auth_user"."email"
print(a[:1].query) # good
# SELECT MAX("auth_user"."id") AS "m" FROM "auth_user" WHERE "auth_user"."email" IS NULL GROUP BY "auth_user"."email" LIMIT 1
b = models.User.objects.filter(id=a[:1])
print(b.query) # GROUP BY U0."id" should be GROUP BY U0."email"
# SELECT ... FROM "auth_user" WHERE "auth_user"."id" = (SELECT U0."id" FROM "auth_user" U0 WHERE U0."email" IS NULL GROUP BY U0."id" LIMIT 1)


## Hints

Workaround: from django.contrib.auth import models a = models.User.objects.filter(email__isnull=True).values('email').aggregate(Max('id'))['id_max'] b = models.User.objects.filter(id=a)
Thanks for tackling that one James! If I can provide you some guidance I'd suggest you have a look at lookups.Exact.process_rhs ​https://github.com/django/django/blob/ea25bdc2b94466bb1563000bf81628dea4d80612/django/db/models/lookups.py#L265-L267 We probably don't want to perform the clear_select_clause and add_fields(['pk']) when the query is already selecting fields. That's exactly what In.process_rhs ​does already by only performing these operations if not getattr(self.rhs, 'has_select_fields', True).
Thanks so much for the help Simon! This is a great jumping-off point. There's something that I'm unclear about, which perhaps you can shed some light on. While I was able to replicate the bug with 2.2, when I try to create a test on Master to validate the bug, the group-by behavior seems to have changed. Here's the test that I created: def test_exact_selected_field_rhs_subquery(self): author_1 = Author.objects.create(name='one') author_2 = Author.objects.create(name='two') max_ids = Author.objects.filter(alias__isnull=True).values('alias').annotate(m=Max('id')).values('m') authors = Author.objects.filter(id=max_ids[:1]) self.assertFalse(str(max_ids.query)) # This was just to force the test-runner to output the query. self.assertEqual(authors[0], author_2) And here's the resulting query: SELECT MAX("lookup_author"."id") AS "m" FROM "lookup_author" WHERE "lookup_author"."alias" IS NULL GROUP BY "lookup_author"."alias", "lookup_author"."name" It no longer appears to be grouping by the 'alias' field listed in the initial .values() preceeding the .annotate(). I looked at the docs and release notes to see if there was a behavior change, but didn't see anything listed. Do you know if I'm just misunderstanding what's happening here? Or does this seem like a possible regression?
It's possible that a regression was introduced in between. Could you try bisecting the commit that changed the behavior ​https://docs.djangoproject.com/en/dev/internals/contributing/triaging-tickets/#bisecting-a-regression
Mmm actually disregard that. The second value in the GROUP BY is due to the ordering value in the Author class's Meta class. class Author(models.Model): name = models.CharField(max_length=100) alias = models.CharField(max_length=50, null=True, blank=True) class Meta: ordering = ('name',) Regarding the bug in question in this ticket, what should the desired behavior be if the inner query is returning multiple fields? With the fix, which allows the inner query to define a field to return/group by, if there are multiple fields used then it will throw a sqlite3.OperationalError: row value misused. Is this the desired behavior or should it avoid this problem by defaulting back to pk if more than one field is selected?
I think that we should only default to pk if no fields are selected. The ORM has preliminary support for multi-column lookups and other interface dealing with subqueries doesn't prevent passing queries with multiple fields so I'd stick to the current __in lookup behavior.

## Patch

```diff

diff --git a/django/db/models/lookups.py b/django/db/models/lookups.py
--- a/django/db/models/lookups.py
+++ b/django/db/models/lookups.py
@@ -262,9 +262,9 @@ def process_rhs(self, compiler, connection):
         from django.db.models.sql.query import Query
         if isinstance(self.rhs, Query):
             if self.rhs.has_limit_one():
-                # The subquery must select only the pk.
-                self.rhs.clear_select_clause()
-                self.rhs.add_fields(['pk'])
+                if not self.rhs.has_select_fields:
+                    self.rhs.clear_select_clause()
+                    self.rhs.add_fields(['pk'])
             else:
                 raise ValueError(
                     'The QuerySet value for an exact lookup must be limited to '


```

## Test Patch

```diff
diff --git a/tests/lookup/tests.py b/tests/lookup/tests.py
--- a/tests/lookup/tests.py
+++ b/tests/lookup/tests.py
@@ -5,6 +5,7 @@
 
 from django.core.exceptions import FieldError
 from django.db import connection
+from django.db.models import Max
 from django.db.models.expressions import Exists, OuterRef
 from django.db.models.functions import Substr
 from django.test import TestCase, skipUnlessDBFeature
@@ -956,3 +957,15 @@ def test_nested_outerref_lhs(self):
             ),
         )
         self.assertEqual(qs.get(has_author_alias_match=True), tag)
+
+    def test_exact_query_rhs_with_selected_columns(self):
+        newest_author = Author.objects.create(name='Author 2')
+        authors_max_ids = Author.objects.filter(
+            name='Author 2',
+        ).values(
+            'name',
+        ).annotate(
+            max_id=Max('id'),
+        ).values('max_id')
+        authors = Author.objects.filter(id=authors_max_ids[:1])
+        self.assertEqual(authors.get(), newest_author)

```

## Test Information

**Tests that should FAIL→PASS**: ["test_exact_query_rhs_with_selected_columns (lookup.tests.LookupTests)"]

**Tests that should PASS→PASS**: ["test_chain_date_time_lookups (lookup.tests.LookupTests)", "test_count (lookup.tests.LookupTests)", "test_custom_field_none_rhs (lookup.tests.LookupTests)", "Lookup.can_use_none_as_rhs=True allows None as a lookup value.", "test_error_messages (lookup.tests.LookupTests)", "test_escaping (lookup.tests.LookupTests)", "test_exact_exists (lookup.tests.LookupTests)", "Transforms are used for __exact=None.", "test_exact_sliced_queryset_limit_one (lookup.tests.LookupTests)", "test_exact_sliced_queryset_limit_one_offset (lookup.tests.LookupTests)", "test_exact_sliced_queryset_not_limited_to_one (lookup.tests.LookupTests)", "test_exclude (lookup.tests.LookupTests)", "test_exists (lookup.tests.LookupTests)", "test_get_next_previous_by (lookup.tests.LookupTests)", "test_in (lookup.tests.LookupTests)", "test_in_bulk (lookup.tests.LookupTests)", "test_in_bulk_lots_of_ids (lookup.tests.LookupTests)", "test_in_bulk_non_unique_field (lookup.tests.LookupTests)", "test_in_bulk_with_field (lookup.tests.LookupTests)", "test_in_different_database (lookup.tests.LookupTests)", "test_in_keeps_value_ordering (lookup.tests.LookupTests)", "test_iterator (lookup.tests.LookupTests)", "test_lookup_collision (lookup.tests.LookupTests)", "test_lookup_date_as_str (lookup.tests.LookupTests)", "test_lookup_int_as_str (lookup.tests.LookupTests)", "test_nested_outerref_lhs (lookup.tests.LookupTests)", "test_none (lookup.tests.LookupTests)", "test_nonfield_lookups (lookup.tests.LookupTests)", "test_pattern_lookups_with_substr (lookup.tests.LookupTests)", "test_regex (lookup.tests.LookupTests)", "test_regex_backreferencing (lookup.tests.LookupTests)", "test_regex_non_ascii (lookup.tests.LookupTests)", "test_regex_non_string (lookup.tests.LookupTests)", "test_regex_null (lookup.tests.LookupTests)", "test_relation_nested_lookup_error (lookup.tests.LookupTests)", "test_unsupported_lookups (lookup.tests.LookupTests)", "test_values (lookup.tests.LookupTests)", "test_values_list (lookup.tests.LookupTests)"]

**Base Commit**: 3346b78a8a872286a245d1e77ef4718fc5e6be1a
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
