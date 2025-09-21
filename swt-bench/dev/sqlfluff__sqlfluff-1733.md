# sqlfluff__sqlfluff-1733

**Repository**: sqlfluff/sqlfluff
**Created**: 2021-10-22T18:23:33Z
**Version**: 0.6

## Problem Statement

Extra space when first field moved to new line in a WITH statement
Note, the query below uses a `WITH` statement. If I just try to fix the SQL within the CTE, this works fine.

Given the following SQL:

```sql
WITH example AS (
    SELECT my_id,
        other_thing,
        one_more
    FROM
        my_table
)

SELECT *
FROM example
```

## Expected Behaviour

after running `sqlfluff fix` I'd expect (`my_id` gets moved down and indented properly):

```sql
WITH example AS (
    SELECT
        my_id,
        other_thing,
        one_more
    FROM
        my_table
)

SELECT *
FROM example
```

## Observed Behaviour

after running `sqlfluff fix` we get (notice that `my_id` is indented one extra space)

```sql
WITH example AS (
    SELECT
         my_id,
        other_thing,
        one_more
    FROM
        my_table
)

SELECT *
FROM example
```

## Steps to Reproduce

Noted above. Create a file with the initial SQL and fun `sqfluff fix` on it.

## Dialect

Running with default config.

## Version
Include the output of `sqlfluff --version` along with your Python version

sqlfluff, version 0.7.0
Python 3.7.5

## Configuration

Default config.



## Hints

Does running `sqlfluff fix` again correct the SQL?
@tunetheweb yes, yes it does. Is that something that the user is supposed to do (run it multiple times) or is this indeed a bug?
Ideally not, but there are some circumstances where it’s understandable that would happen. This however seems an easy enough example where it should not happen.
This appears to be a combination of rules L036, L003, and L039 not playing nicely together.

The original error is rule L036 and it produces this:

```sql
WITH example AS (
    SELECT
my_id,
        other_thing,
        one_more
    FROM
        my_table
)

SELECT *
FROM example
```

That is, it moves the `my_id` down to the newline but does not even try to fix the indentation.

Then we have another run through and L003 spots the lack of indentation and fixes it by adding the first set of whitespace:

```sql
WITH example AS (
    SELECT
    my_id,
        other_thing,
        one_more
    FROM
        my_table
)

SELECT *
FROM example
```

Then we have another run through and L003 spots that there still isn't enough indentation and fixes it by adding the second set of whitespace:

```sql
WITH example AS (
    SELECT
        my_id,
        other_thing,
        one_more
    FROM
        my_table
)

SELECT *
FROM example
```

At this point we're all good.

However then L039 has a look. It never expects two sets of whitespace following a new line and is specifically coded to only assume one set of spaces (which it normally would be if the other rules hadn't interfered as it would be parsed as one big space), so it think's the second set is too much indentation, so it replaces it with a single space.

Then another run and L003 and the whitespace back in so we end up with two indents, and a single space.

Luckily the fix is easier than that explanation. PR coming up...



## Patch

```diff

diff --git a/src/sqlfluff/rules/L039.py b/src/sqlfluff/rules/L039.py
--- a/src/sqlfluff/rules/L039.py
+++ b/src/sqlfluff/rules/L039.py
@@ -44,7 +44,9 @@ def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
                 # This is to avoid indents
                 if not prev_newline:
                     prev_whitespace = seg
-                prev_newline = False
+                # We won't set prev_newline to False, just for whitespace
+                # in case there's multiple indents, inserted by other rule
+                # fixes (see #1713)
             elif seg.is_type("comment"):
                 prev_newline = False
                 prev_whitespace = None


```

## Test Patch

```diff
diff --git a/test/rules/std_L003_L036_L039_combo_test.py b/test/rules/std_L003_L036_L039_combo_test.py
new file mode 100644
--- /dev/null
+++ b/test/rules/std_L003_L036_L039_combo_test.py
@@ -0,0 +1,36 @@
+"""Tests issue #1373 doesn't reoccur.
+
+The combination of L003 (incorrect indentation), L036 (select targets),
+and L039 (unnecessary white space) can result in incorrect indentation.
+"""
+
+import sqlfluff
+
+
+def test__rules__std_L003_L036_L039():
+    """Verify that double indents don't flag L039."""
+    sql = """
+    WITH example AS (
+        SELECT my_id,
+            other_thing,
+            one_more
+        FROM
+            my_table
+    )
+
+    SELECT *
+    FROM example\n"""
+    fixed_sql = """
+    WITH example AS (
+        SELECT
+            my_id,
+            other_thing,
+            one_more
+        FROM
+            my_table
+    )
+
+    SELECT *
+    FROM example\n"""
+    result = sqlfluff.fix(sql)
+    assert result == fixed_sql
diff --git a/test/rules/std_L016_L36_combo.py b/test/rules/std_L016_L36_combo_test.py
similarity index 100%
rename from test/rules/std_L016_L36_combo.py
rename to test/rules/std_L016_L36_combo_test.py

```

## Test Information

**Tests that should FAIL→PASS**: ["test/rules/std_L003_L036_L039_combo_test.py::test__rules__std_L003_L036_L039"]

**Tests that should PASS→PASS**: ["test/rules/std_L016_L36_combo_test.py::test__rules__std_L016_L036_long_line_lint", "test/rules/std_L016_L36_combo_test.py::test__rules__std_L016_L036_long_line_fix", "test/rules/std_L016_L36_combo_test.py::test__rules__std_L016_L036_long_line_fix2"]

**Base Commit**: a1579a16b1d8913d9d7c7d12add374a290bcc78c
**Environment Setup Commit**: 67023b85c41d23d6c6d69812a41b207c4f8a9331
