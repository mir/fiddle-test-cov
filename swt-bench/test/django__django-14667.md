# django__django-14667

**Repository**: django/django
**Created**: 2021-07-19T21:08:03Z
**Version**: 4.0

## Problem Statement

QuerySet.defer() doesn't clear deferred field when chaining with only().
Description
	
Considering a simple Company model with four fields: id, name, trade_number and country. If we evaluate a queryset containing a .defer() following a .only(), the generated sql query selects unexpected fields. For example: 
Company.objects.only("name").defer("name")
loads all the fields with the following query:
SELECT "company"."id", "company"."name", "company"."trade_number", "company"."country" FROM "company"
and 
Company.objects.only("name").defer("name").defer("country")
also loads all the fields with the same query:
SELECT "company"."id", "company"."name", "company"."trade_number", "company"."country" FROM "company"
In those two cases, i would expect the sql query to be:
SELECT "company"."id" FROM "company"
In the following example, we get the expected behavior:
Company.objects.only("name", "country").defer("name")
only loads "id" and "country" fields with the following query:
SELECT "company"."id", "company"."country" FROM "company"


## Hints

Replying to Manuel Baclet: Considering a simple Company model with four fields: id, name, trade_number and country. If we evaluate a queryset containing a .defer() following a .only(), the generated sql query selects unexpected fields. For example: Company.objects.only("name").defer("name") loads all the fields with the following query: SELECT "company"."id", "company"."name", "company"."trade_number", "company"."country" FROM "company" This is an expected behavior, defer() removes fields from the list of fields specified by the only() method (i.e. list of fields that should not be deferred). In this example only() adds name to the list, defer() removes name from the list, so you have empty lists and all fields will be loaded. It is also ​documented: # Final result is that everything except "headline" is deferred. Entry.objects.only("headline", "body").defer("body") Company.objects.only("name").defer("name").defer("country") also loads all the fields with the same query: SELECT "company"."id", "company"."name", "company"."trade_number", "company"."country" FROM "company" I agree you shouldn't get all field, but only pk, name, and trade_number: SELECT "ticket_32704_company"."id", "ticket_32704_company"."name", "ticket_32704_company"."trade_number" FROM "ticket_32704_company" this is due to the fact that defer() doesn't clear the list of deferred field when chaining with only(). I attached a proposed patch.
Draft.
After reading the documentation carefully, i cannot say that it is clearly stated that deferring all the fields used in a previous .only() call performs a reset of the deferred set. Moreover, in the .defer() ​section, we have: You can make multiple calls to defer(). Each call adds new fields to the deferred set: and this seems to suggest that: calls to .defer() cannot remove items from the deferred set and evaluating qs.defer("some_field") should never fetch the column "some_field" (since this should add "some_field" to the deferred set) the querysets qs.defer("field1").defer("field2") and qs.defer("field1", "field2") should be equivalent IMHO, there is a mismatch between the doc and the actual implementation.
calls to .defer() cannot remove items from the deferred set and evaluating qs.defer("some_field") should never fetch the column "some_field" (since this should add "some_field" to the deferred set) Feel-free to propose a docs clarification (see also #24048). the querysets qs.defer("field1").defer("field2") and qs.defer("field1", "field2") should be equivalent That's why I accepted Company.objects.only("name").defer("name").defer("country") as a bug.
I think that what is described in the documentation is what users are expected and it is the implementation that should be fixed! With your patch proposal, i do not think that: Company.objects.only("name").defer("name").defer("country") is equivalent to Company.objects.only("name").defer("name", "country")
Replying to Manuel Baclet: I think that what is described in the documentation is what users are expected and it is the implementation that should be fixed! I don't agree, and there is no need to shout. As documented: "The only() method is more or less the opposite of defer(). You call it with the fields that should not be deferred ...", so .only('name').defer('name') should return all fields. You can start a discussion on DevelopersMailingList if you don't agree. With your patch proposal, i do not think that: Company.objects.only("name").defer("name").defer("country") is equivalent to Company.objects.only("name").defer("name", "country") Did you check this? with proposed patch country is the only deferred fields in both cases. As far as I'm aware that's an intended behavior.
With the proposed patch, I think that: Company.objects.only("name").defer("name", "country") loads all fields whereas: Company.objects.only("name").defer("name").defer("country") loads all fields except "country". Why is that? In the first case: existing.difference(field_names) == {"name"}.difference(["name", "country"]) == empty_set and we go into the if branch clearing all the deferred fields and we are done. In the second case: existing.difference(field_names) == {"name"}.difference(["name"]) == empty_set and we go into the if branch clearing all the deferred fields. Then we add "country" to the set of deferred fields.
Hey all, Replying to Mariusz Felisiak: Replying to Manuel Baclet: With your patch proposal, i do not think that: Company.objects.only("name").defer("name").defer("country") is equivalent to Company.objects.only("name").defer("name", "country") Did you check this? with proposed patch country is the only deferred fields in both cases. As far as I'm aware that's an intended behavior. I believe Manuel is right. This happens because the set difference in one direction gives you the empty set that will clear out the deferred fields - but it is missing the fact that we might also be adding more defer fields than we had only fields in the first place, so that we actually switch from an .only() to a .defer() mode. See the corresponding PR that should fix this behaviour ​https://github.com/django/django/pull/14667

## Patch

```diff

diff --git a/django/db/models/sql/query.py b/django/db/models/sql/query.py
--- a/django/db/models/sql/query.py
+++ b/django/db/models/sql/query.py
@@ -2086,7 +2086,12 @@ def add_deferred_loading(self, field_names):
             self.deferred_loading = existing.union(field_names), True
         else:
             # Remove names from the set of any existing "immediate load" names.
-            self.deferred_loading = existing.difference(field_names), False
+            if new_existing := existing.difference(field_names):
+                self.deferred_loading = new_existing, False
+            else:
+                self.clear_deferred_loading()
+                if new_only := set(field_names).difference(existing):
+                    self.deferred_loading = new_only, True
 
     def add_immediate_loading(self, field_names):
         """


```

## Test Patch

```diff
diff --git a/tests/defer/tests.py b/tests/defer/tests.py
--- a/tests/defer/tests.py
+++ b/tests/defer/tests.py
@@ -49,8 +49,16 @@ def test_defer_only_chaining(self):
         qs = Primary.objects.all()
         self.assert_delayed(qs.only("name", "value").defer("name")[0], 2)
         self.assert_delayed(qs.defer("name").only("value", "name")[0], 2)
+        self.assert_delayed(qs.defer('name').only('name').only('value')[0], 2)
         self.assert_delayed(qs.defer("name").only("value")[0], 2)
         self.assert_delayed(qs.only("name").defer("value")[0], 2)
+        self.assert_delayed(qs.only('name').defer('name').defer('value')[0], 1)
+        self.assert_delayed(qs.only('name').defer('name', 'value')[0], 1)
+
+    def test_defer_only_clear(self):
+        qs = Primary.objects.all()
+        self.assert_delayed(qs.only('name').defer('name')[0], 0)
+        self.assert_delayed(qs.defer('name').only('name')[0], 0)
 
     def test_defer_on_an_already_deferred_field(self):
         qs = Primary.objects.all()

```

## Test Information

**Tests that should FAIL→PASS**: ["test_defer_only_chaining (defer.tests.DeferTests)"]

**Tests that should PASS→PASS**: ["test_custom_refresh_on_deferred_loading (defer.tests.TestDefer2)", "When an inherited model is fetched from the DB, its PK is also fetched.", "Ensure select_related together with only on a proxy model behaves", "test_eq (defer.tests.TestDefer2)", "test_refresh_not_loading_deferred_fields (defer.tests.TestDefer2)", "test_defer_baseclass_when_subclass_has_added_field (defer.tests.BigChildDeferTests)", "test_defer_subclass (defer.tests.BigChildDeferTests)", "test_defer_subclass_both (defer.tests.BigChildDeferTests)", "test_only_baseclass_when_subclass_has_added_field (defer.tests.BigChildDeferTests)", "test_only_subclass (defer.tests.BigChildDeferTests)", "test_defer (defer.tests.DeferTests)", "test_defer_baseclass_when_subclass_has_no_added_fields (defer.tests.DeferTests)", "test_defer_extra (defer.tests.DeferTests)", "test_defer_foreign_keys_are_deferred_and_not_traversed (defer.tests.DeferTests)", "test_defer_none_to_clear_deferred_set (defer.tests.DeferTests)", "test_defer_of_overridden_scalar (defer.tests.DeferTests)", "test_defer_on_an_already_deferred_field (defer.tests.DeferTests)", "test_defer_only_clear (defer.tests.DeferTests)", "test_defer_select_related_raises_invalid_query (defer.tests.DeferTests)", "test_defer_values_does_not_defer (defer.tests.DeferTests)", "test_defer_with_select_related (defer.tests.DeferTests)", "test_get (defer.tests.DeferTests)", "test_only (defer.tests.DeferTests)", "test_only_baseclass_when_subclass_has_no_added_fields (defer.tests.DeferTests)", "test_only_none_raises_error (defer.tests.DeferTests)", "test_only_select_related_raises_invalid_query (defer.tests.DeferTests)", "test_only_values_does_not_defer (defer.tests.DeferTests)", "test_only_with_select_related (defer.tests.DeferTests)", "test_saving_object_with_deferred_field (defer.tests.DeferTests)"]

**Base Commit**: 6a970a8b4600eb91be25f38caed0a52269d6303d
**Environment Setup Commit**: 475cffd1d64c690cdad16ede4d5e81985738ceb4
