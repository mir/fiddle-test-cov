# sqlfluff__sqlfluff-2419

**Repository**: sqlfluff/sqlfluff
**Created**: 2022-01-22T12:21:52Z
**Version**: 0.8

## Problem Statement

Rule L060 could give a specific error message
At the moment rule L060 flags something like this:

```
L:  21 | P:   9 | L060 | Use 'COALESCE' instead of 'IFNULL' or 'NVL'.
```

Since we likely know the wrong word, it might be nice to actually flag that instead of both `IFNULL` and `NVL` - like most of the other rules do.

That is it should flag this:

```
L:  21 | P:   9 | L060 | Use 'COALESCE' instead of 'IFNULL'.
```
 Or this:

```
L:  21 | P:   9 | L060 | Use 'COALESCE' instead of 'NVL'.
```

As appropriate.

What do you think @jpy-git ?



## Hints

@tunetheweb Yeah definitely, should be a pretty quick change 😊

## Patch

```diff

diff --git a/src/sqlfluff/rules/L060.py b/src/sqlfluff/rules/L060.py
--- a/src/sqlfluff/rules/L060.py
+++ b/src/sqlfluff/rules/L060.py
@@ -59,4 +59,8 @@ def _eval(self, context: RuleContext) -> Optional[LintResult]:
             ],
         )
 
-        return LintResult(context.segment, [fix])
+        return LintResult(
+            anchor=context.segment,
+            fixes=[fix],
+            description=f"Use 'COALESCE' instead of '{context.segment.raw_upper}'.",
+        )


```

## Test Patch

```diff
diff --git a/test/rules/std_L060_test.py b/test/rules/std_L060_test.py
new file mode 100644
--- /dev/null
+++ b/test/rules/std_L060_test.py
@@ -0,0 +1,12 @@
+"""Tests the python routines within L060."""
+import sqlfluff
+
+
+def test__rules__std_L060_raised() -> None:
+    """L060 is raised for use of ``IFNULL`` or ``NVL``."""
+    sql = "SELECT\n\tIFNULL(NULL, 100),\n\tNVL(NULL,100);"
+    result = sqlfluff.lint(sql, rules=["L060"])
+
+    assert len(result) == 2
+    assert result[0]["description"] == "Use 'COALESCE' instead of 'IFNULL'."
+    assert result[1]["description"] == "Use 'COALESCE' instead of 'NVL'."

```

## Test Information

**Tests that should FAIL→PASS**: ["test/rules/std_L060_test.py::test__rules__std_L060_raised"]

**Tests that should PASS→PASS**: []

**Base Commit**: f1dba0e1dd764ae72d67c3d5e1471cf14d3db030
**Environment Setup Commit**: a5c4eae4e3e419fe95460c9afd9cf39a35a470c4
