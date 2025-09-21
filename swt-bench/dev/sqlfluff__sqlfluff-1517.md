# sqlfluff__sqlfluff-1517

**Repository**: sqlfluff/sqlfluff
**Created**: 2021-10-06T07:57:35Z
**Version**: 0.6

## Problem Statement

"Dropped elements in sequence matching" when doubled semicolon
## Expected Behaviour
Frankly, I'm not sure whether it (doubled `;`) should be just ignored or rather some specific rule should be triggered.
## Observed Behaviour
```console
(.venv) ?master ~/prod/_inne/sqlfluff> echo "select id from tbl;;" | sqlfluff lint -
Traceback (most recent call last):
  File "/home/adam/prod/_inne/sqlfluff/.venv/bin/sqlfluff", line 11, in <module>
    load_entry_point('sqlfluff', 'console_scripts', 'sqlfluff')()
  File "/home/adam/prod/_inne/sqlfluff/.venv/lib/python3.9/site-packages/click/core.py", line 1137, in __call__
    return self.main(*args, **kwargs)
  File "/home/adam/prod/_inne/sqlfluff/.venv/lib/python3.9/site-packages/click/core.py", line 1062, in main
    rv = self.invoke(ctx)
  File "/home/adam/prod/_inne/sqlfluff/.venv/lib/python3.9/site-packages/click/core.py", line 1668, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/home/adam/prod/_inne/sqlfluff/.venv/lib/python3.9/site-packages/click/core.py", line 1404, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/home/adam/prod/_inne/sqlfluff/.venv/lib/python3.9/site-packages/click/core.py", line 763, in invoke
    return __callback(*args, **kwargs)
  File "/home/adam/prod/_inne/sqlfluff/src/sqlfluff/cli/commands.py", line 347, in lint
    result = lnt.lint_string_wrapped(sys.stdin.read(), fname="stdin")
  File "/home/adam/prod/_inne/sqlfluff/src/sqlfluff/core/linter/linter.py", line 789, in lint_string_wrapped
    linted_path.add(self.lint_string(string, fname=fname, fix=fix))
  File "/home/adam/prod/_inne/sqlfluff/src/sqlfluff/core/linter/linter.py", line 668, in lint_string
    parsed = self.parse_string(in_str=in_str, fname=fname, config=config)
  File "/home/adam/prod/_inne/sqlfluff/src/sqlfluff/core/linter/linter.py", line 607, in parse_string
    return self.parse_rendered(rendered, recurse=recurse)
  File "/home/adam/prod/_inne/sqlfluff/src/sqlfluff/core/linter/linter.py", line 313, in parse_rendered
    parsed, pvs = cls._parse_tokens(
  File "/home/adam/prod/_inne/sqlfluff/src/sqlfluff/core/linter/linter.py", line 190, in _parse_tokens
    parsed: Optional[BaseSegment] = parser.parse(
  File "/home/adam/prod/_inne/sqlfluff/src/sqlfluff/core/parser/parser.py", line 32, in parse
    parsed = root_segment.parse(parse_context=ctx)
  File "/home/adam/prod/_inne/sqlfluff/src/sqlfluff/core/parser/segments/base.py", line 821, in parse
    check_still_complete(segments, m.matched_segments, m.unmatched_segments)
  File "/home/adam/prod/_inne/sqlfluff/src/sqlfluff/core/parser/helpers.py", line 30, in check_still_complete
    raise RuntimeError(
RuntimeError: Dropped elements in sequence matching! 'select id from tbl;;' != ';'

```
## Steps to Reproduce
Run 
```console
echo "select id from tbl;;" | sqlfluff lint -
```
## Dialect
default (ansi)
## Version
```
sqlfluff, version 0.6.6
Python 3.9.5
```
## Configuration
None



## Hints

Sounds similar to #1458 where we should handle "empty" statement/files better?
Nope, that's the different issue. I doubt that solving one of them would help in other one. I think both issues should stay, just in the case.
But what do you think @tunetheweb - should it just ignore these `;;` or raise something like `Found unparsable section:`? 
Just tested and in BigQuery it's an error.
Interestingly Oracle is fine with it.

I think it should be raised as `Found unparsable section`.

## Patch

```diff

diff --git a/src/sqlfluff/core/parser/helpers.py b/src/sqlfluff/core/parser/helpers.py
--- a/src/sqlfluff/core/parser/helpers.py
+++ b/src/sqlfluff/core/parser/helpers.py
@@ -2,6 +2,7 @@
 
 from typing import Tuple, List, Any, Iterator, TYPE_CHECKING
 
+from sqlfluff.core.errors import SQLParseError
 from sqlfluff.core.string_helpers import curtail_string
 
 if TYPE_CHECKING:
@@ -26,11 +27,11 @@ def check_still_complete(
     """Check that the segments in are the same as the segments out."""
     initial_str = join_segments_raw(segments_in)
     current_str = join_segments_raw(matched_segments + unmatched_segments)
-    if initial_str != current_str:  # pragma: no cover
-        raise RuntimeError(
-            "Dropped elements in sequence matching! {!r} != {!r}".format(
-                initial_str, current_str
-            )
+
+    if initial_str != current_str:
+        raise SQLParseError(
+            f"Could not parse: {current_str}",
+            segment=unmatched_segments[0],
         )
     return True
 


```

## Test Patch

```diff
diff --git a/test/dialects/ansi_test.py b/test/dialects/ansi_test.py
--- a/test/dialects/ansi_test.py
+++ b/test/dialects/ansi_test.py
@@ -3,7 +3,7 @@
 import pytest
 import logging
 
-from sqlfluff.core import FluffConfig, Linter
+from sqlfluff.core import FluffConfig, Linter, SQLParseError
 from sqlfluff.core.parser import Lexer
 
 
@@ -214,3 +214,29 @@ def test__dialect__ansi_parse_indented_joins(sql_string, indented_joins, meta_lo
         idx for idx, raw_seg in enumerate(parsed.tree.iter_raw_seg()) if raw_seg.is_meta
     )
     assert res_meta_locs == meta_loc
+
+
+@pytest.mark.parametrize(
+    "raw,expected_message",
+    [
+        (";;", "Line 1, Position 1: Found unparsable section: ';;'"),
+        ("select id from tbl;", ""),
+        ("select id from tbl;;", "Could not parse: ;"),
+        ("select id from tbl;;;;;;", "Could not parse: ;;;;;"),
+        ("select id from tbl;select id2 from tbl2;", ""),
+        (
+            "select id from tbl;;select id2 from tbl2;",
+            "Could not parse: ;select id2 from tbl2;",
+        ),
+    ],
+)
+def test__dialect__ansi_multiple_semicolons(raw: str, expected_message: str) -> None:
+    """Multiple semicolons should be properly handled."""
+    lnt = Linter()
+    parsed = lnt.parse_string(raw)
+
+    assert len(parsed.violations) == (1 if expected_message else 0)
+    if expected_message:
+        violation = parsed.violations[0]
+        assert isinstance(violation, SQLParseError)
+        assert violation.desc() == expected_message

```

## Test Information

**Tests that should FAIL→PASS**: ["test/dialects/ansi_test.py::test__dialect__ansi_multiple_semicolons[select"]

**Tests that should PASS→PASS**: ["test/dialects/ansi_test.py::test__dialect__ansi__file_lex[a", "test/dialects/ansi_test.py::test__dialect__ansi__file_lex[b.c-res1]", "test/dialects/ansi_test.py::test__dialect__ansi__file_lex[abc", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[SelectKeywordSegment-select]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[NakedIdentifierSegment-online_sales]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[BareFunctionSegment-current_timestamp]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[FunctionSegment-current_timestamp()]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[NumericLiteralSegment-1000.0]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ExpressionSegment-online_sales", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[IntervalExpressionSegment-INTERVAL", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ExpressionSegment-CASE", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ExpressionSegment-CAST(ROUND(online_sales", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ExpressionSegment-name", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[SelectClauseElementSegment-MIN", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ExpressionSegment-DATE_ADD(CURRENT_DATE('America/New_York'),", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ExpressionSegment-my_array[1]]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ExpressionSegment-my_array[OFFSET(1)]]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ExpressionSegment-my_array[5:8]]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ExpressionSegment-4", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ExpressionSegment-bits[OFFSET(0)]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[SelectClauseElementSegment-(count_18_24", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ExpressionSegment-count_18_24", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[SelectStatementSegment-SELECT", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[SelectClauseElementSegment-t.val/t.id]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[SelectClauseElementSegment-CAST(num", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[SelectClauseElementSegment-a.*]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[SelectClauseElementSegment-a.b.*]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[SelectClauseElementSegment-a.b.c.*]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ObjectReferenceSegment-a..c.*]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[SelectClauseElementSegment--some_variable]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[SelectClauseElementSegment--", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ExpressionSegment-concat(left(uaid,", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ExpressionSegment-c", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[SelectClauseElementSegment-c", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[ExpressionSegment-NULL::INT]", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[SelectClauseElementSegment-NULL::INT", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_parses[TruncateStatementSegment-TRUNCATE", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_not_match[ObjectReferenceSegment-\\n", "test/dialects/ansi_test.py::test__dialect__ansi_specific_segment_not_parse[SELECT", "test/dialects/ansi_test.py::test__dialect__ansi_is_whitespace", "test/dialects/ansi_test.py::test__dialect__ansi_parse_indented_joins[select", "test/dialects/ansi_test.py::test__dialect__ansi_multiple_semicolons[;;-Line"]

**Base Commit**: 304a197829f98e7425a46d872ada73176137e5ae
**Environment Setup Commit**: 67023b85c41d23d6c6d69812a41b207c4f8a9331
