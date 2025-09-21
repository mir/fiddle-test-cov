# sqlfluff__sqlfluff-1763

**Repository**: sqlfluff/sqlfluff
**Created**: 2021-10-26T17:28:28Z
**Version**: 0.6

## Problem Statement

dbt postgres fix command errors with UnicodeEncodeError and also wipes the .sql file
_If this is a parsing or linting issue, please include a minimal SQL example which reproduces the issue, along with the `sqlfluff parse` output, `sqlfluff lint` output and `sqlfluff fix` output when relevant._

## Expected Behaviour
Violation failure notice at a minimum, without wiping the file. Would like a way to ignore the known error at a minimum as --noqa is not getting past this. Actually would expect --noqa to totally ignore this.

## Observed Behaviour
Reported error: `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 120: character maps to <undefined>`

## Steps to Reproduce
SQL file:
```sql
SELECT
    reacted_table_name_right.descendant_id AS category_id,
    string_agg(redacted_table_name_left.name, ' → ' ORDER BY reacted_table_name_right.generations DESC) AS breadcrumbs -- noqa
FROM {{ ref2('redacted_schema_name', 'redacted_table_name_left') }} AS redacted_table_name_left
INNER JOIN {{ ref2('redacted_schema_name', 'reacted_table_name_right') }} AS reacted_table_name_right
    ON redacted_table_name_left.id = order_issue_category_hierarchies.ancestor_id
GROUP BY reacted_table_name_right.descendant_id
```
Running `sqlfluff fix --ignore templating,parsing,lexing -vvvv` and accepting proposed fixes for linting violations.

## Dialect
`postgres`, with `dbt` templater

## Version
`python 3.7.12`
`sqlfluff 0.7.0`
`sqlfluff-templater-dbt 0.7.0`

## Configuration
I've tried a few, here's one:
```
[sqlfluff]
verbose = 2
dialect = postgres
templater = dbt
exclude_rules = None
output_line_length = 80
runaway_limit = 10
ignore_templated_areas = True
processes = 3
# Comma separated list of file extensions to lint.

# NB: This config will only apply in the root folder.
sql_file_exts = .sql

[sqlfluff:indentation]
indented_joins = False
indented_using_on = True
template_blocks_indent = True

[sqlfluff:templater]
unwrap_wrapped_queries = True

[sqlfluff:templater:jinja]
apply_dbt_builtins = True

[sqlfluff:templater:jinja:macros]
# Macros provided as builtins for dbt projects
dbt_ref = {% macro ref(model_ref) %}{{model_ref}}{% endmacro %}
dbt_source = {% macro source(source_name, table) %}{{source_name}}_{{table}}{% endmacro %}
dbt_config = {% macro config() %}{% for k in kwargs %}{% endfor %}{% endmacro %}
dbt_var = {% macro var(variable, default='') %}item{% endmacro %}
dbt_is_incremental = {% macro is_incremental() %}True{% endmacro %}

# Common config across rules
[sqlfluff:rules]
tab_space_size = 4
indent_unit = space
single_table_references = consistent
unquoted_identifiers_policy = all

# L001 - Remove trailing whitespace (fix)
# L002 - Single section of whitespace should not contain both tabs and spaces (fix)
# L003 - Keep consistent indentation (fix)
# L004 - We use 4 spaces for indentation just for completeness (fix)
# L005 - Remove space before commas (fix)
# L006 - Operators (+, -, *, /) will be wrapped by a single space each side (fix)

# L007 - Operators should not be at the end of a line
[sqlfluff:rules:L007]  # Keywords
operator_new_lines = after

# L008 - Always use a single whitespace after a comma (fix)
# L009 - Files will always end with a trailing newline

# L010 - All keywords will use full upper case (fix)
[sqlfluff:rules:L010]  # Keywords
capitalisation_policy = upper

# L011 - Always explicitly alias tables (fix)
[sqlfluff:rules:L011]  # Aliasing
aliasing = explicit

# L012 - Do not have to explicitly alias all columns
[sqlfluff:rules:L012]  # Aliasing
aliasing = explicit

# L013 - Always explicitly alias a column with an expression in it (fix)
[sqlfluff:rules:L013]  # Aliasing
allow_scalar = False

# L014 - Always user full lower case for 'quoted identifiers' -> column refs. without an alias (fix)
[sqlfluff:rules:L014]  # Unquoted identifiers
extended_capitalisation_policy = lower

# L015 - Always remove parenthesis when using DISTINCT to be clear that DISTINCT applies to all columns (fix)

# L016 - Lines should be 120 characters of less. Comment lines should not be ignored (fix)
[sqlfluff:rules:L016]
ignore_comment_lines = False
max_line_length = 120

# L017 - There should not be whitespace between function name and brackets (fix)
# L018 - Always align closing bracket of WITH to the WITH keyword (fix)

# L019 - Always use trailing commas / commas at the end of the line (fix)
[sqlfluff:rules:L019]
comma_style = trailing

# L020 - Table aliases will always be unique per statement
# L021 - Remove any use of ambiguous DISTINCT and GROUP BY combinations. Lean on removing the GROUP BY.
# L022 - Add blank lines after common table expressions (CTE) / WITH.
# L023 - Always add a single whitespace after AS in a WITH clause (fix)

[sqlfluff:rules:L026]
force_enable = False

# L027 - Always add references if more than one referenced table or view is used

[sqlfluff:rules:L028]
force_enable = False

[sqlfluff:rules:L029]  # Keyword identifiers
unquoted_identifiers_policy = aliases

[sqlfluff:rules:L030]  # Function names
capitalisation_policy = upper

# L032 - We prefer use of join keys rather than USING
# L034 - We prefer ordering of columns in select statements as (fix):
# 1. wildcards
# 2. single identifiers
# 3. calculations and aggregates

# L035 - Omit 'else NULL'; it is redundant (fix)
# L036 - Move select targets / identifiers onto new lines each (fix)
# L037 - When using ORDER BY, make the direction explicit (fix)

# L038 - Never use trailing commas at the end of the SELECT clause
[sqlfluff:rules:L038]
select_clause_trailing_comma = forbid

# L039 - Remove unnecessary whitespace (fix)

[sqlfluff:rules:L040]  # Null & Boolean Literals
capitalisation_policy = upper

# L042 - Join clauses should not contain subqueries. Use common tables expressions (CTE) instead.
[sqlfluff:rules:L042]
# By default, allow subqueries in from clauses, but not join clauses.
forbid_subquery_in = join

# L043 - Reduce CASE WHEN conditions to COALESCE (fix)
# L044 - Prefer a known number of columns along the path to the source data
# L045 - Remove unused common tables expressions (CTE) / WITH statements (fix)
# L046 - Jinja tags should have a single whitespace on both sides

# L047 - Use COUNT(*) instead of COUNT(0) or COUNT(1) alternatives (fix)
[sqlfluff:rules:L047]  # Consistent syntax to count all rows
prefer_count_1 = False
prefer_count_0 = False

# L048 - Quoted literals should be surrounded by a single whitespace (fix)
# L049 - Always use IS or IS NOT for comparisons with NULL (fix)
```



## Hints

I get a dbt-related error -- can you provide your project file as well? Also, what operating system are you running this on? I tested a simplified (non-dbt) version of your file on my Mac, and it worked okay.

```
dbt.exceptions.DbtProjectError: Runtime Error
  no dbt_project.yml found at expected path /Users/bhart/dev/sqlfluff/dbt_project.yml
```
Never mind the questions above -- I managed to reproduce the error in a sample dbt project. Taking a look now...
@Tumble17: Have you tried setting the `encoding` parameter in `.sqlfluff`? Do you know what encoding you're using? The default is `autodetect`, and SQLFluff "thinks" the file uses "Windows-1252" encoding, which I assume is incorrect -- that's why SQLFluff is unable to write out the updated file.
I added this line to the first section of your `.sqlfluff`, and now it seems to work. I'll look into changing the behavior of `sqlfluff fix` so it doesn't erase the file when it fails.

```
encoding = utf-8
```

## Patch

```diff

diff --git a/src/sqlfluff/core/linter/linted_file.py b/src/sqlfluff/core/linter/linted_file.py
--- a/src/sqlfluff/core/linter/linted_file.py
+++ b/src/sqlfluff/core/linter/linted_file.py
@@ -7,6 +7,8 @@
 
 import os
 import logging
+import shutil
+import tempfile
 from typing import (
     Any,
     Iterable,
@@ -493,7 +495,24 @@ def persist_tree(self, suffix: str = "") -> bool:
             if suffix:
                 root, ext = os.path.splitext(fname)
                 fname = root + suffix + ext
-            # Actually write the file.
-            with open(fname, "w", encoding=self.encoding) as f:
-                f.write(write_buff)
+            self._safe_create_replace_file(fname, write_buff, self.encoding)
         return success
+
+    @staticmethod
+    def _safe_create_replace_file(fname, write_buff, encoding):
+        # Write to a temporary file first, so in case of encoding or other
+        # issues, we don't delete or corrupt the user's existing file.
+        dirname, basename = os.path.split(fname)
+        with tempfile.NamedTemporaryFile(
+            mode="w",
+            encoding=encoding,
+            prefix=basename,
+            dir=dirname,
+            suffix=os.path.splitext(fname)[1],
+            delete=False,
+        ) as tmp:
+            tmp.file.write(write_buff)
+            tmp.flush()
+            os.fsync(tmp.fileno())
+        # Once the temp file is safely written, replace the existing file.
+        shutil.move(tmp.name, fname)


```

## Test Patch

```diff
diff --git a/test/core/linter_test.py b/test/core/linter_test.py
--- a/test/core/linter_test.py
+++ b/test/core/linter_test.py
@@ -641,3 +641,56 @@ def test__attempt_to_change_templater_warning(caplog):
         assert "Attempt to set templater to " in caplog.text
     finally:
         logger.propagate = original_propagate_value
+
+
+@pytest.mark.parametrize(
+    "case",
+    [
+        dict(
+            name="utf8_create",
+            fname="test.sql",
+            encoding="utf-8",
+            existing=None,
+            update="def",
+            expected="def",
+        ),
+        dict(
+            name="utf8_update",
+            fname="test.sql",
+            encoding="utf-8",
+            existing="abc",
+            update="def",
+            expected="def",
+        ),
+        dict(
+            name="utf8_special_char",
+            fname="test.sql",
+            encoding="utf-8",
+            existing="abc",
+            update="→",  # Special utf-8 character
+            expected="→",
+        ),
+        dict(
+            name="incorrect_encoding",
+            fname="test.sql",
+            encoding="Windows-1252",
+            existing="abc",
+            update="→",  # Not valid in Windows-1252
+            expected="abc",  # File should be unchanged
+        ),
+    ],
+    ids=lambda case: case["name"],
+)
+def test_safe_create_replace_file(case, tmp_path):
+    """Test creating or updating .sql files, various content and encoding."""
+    p = tmp_path / case["fname"]
+    if case["existing"]:
+        p.write_text(case["existing"])
+    try:
+        linter.LintedFile._safe_create_replace_file(
+            str(p), case["update"], case["encoding"]
+        )
+    except:  # noqa: E722
+        pass
+    actual = p.read_text(encoding=case["encoding"])
+    assert case["expected"] == actual

```

## Test Information

**Tests that should FAIL→PASS**: ["test/core/linter_test.py::test_safe_create_replace_file[utf8_create]", "test/core/linter_test.py::test_safe_create_replace_file[utf8_update]", "test/core/linter_test.py::test_safe_create_replace_file[utf8_special_char]"]

**Tests that should PASS→PASS**: ["test/core/linter_test.py::test__linter__path_from_paths__dir", "test/core/linter_test.py::test__linter__path_from_paths__default", "test/core/linter_test.py::test__linter__path_from_paths__exts", "test/core/linter_test.py::test__linter__path_from_paths__file", "test/core/linter_test.py::test__linter__path_from_paths__not_exist", "test/core/linter_test.py::test__linter__path_from_paths__not_exist_ignore", "test/core/linter_test.py::test__linter__path_from_paths__explicit_ignore", "test/core/linter_test.py::test__linter__path_from_paths__dot", "test/core/linter_test.py::test__linter__path_from_paths__ignore[test/fixtures/linter/sqlfluffignore]", "test/core/linter_test.py::test__linter__path_from_paths__ignore[test/fixtures/linter/sqlfluffignore/]", "test/core/linter_test.py::test__linter__path_from_paths__ignore[test/fixtures/linter/sqlfluffignore/.]", "test/core/linter_test.py::test__linter__lint_string_vs_file[test/fixtures/linter/indentation_errors.sql]", "test/core/linter_test.py::test__linter__lint_string_vs_file[test/fixtures/linter/whitespace_errors.sql]", "test/core/linter_test.py::test__linter__get_violations_filter_rules[None-7]", "test/core/linter_test.py::test__linter__get_violations_filter_rules[L010-2]", "test/core/linter_test.py::test__linter__get_violations_filter_rules[rules2-2]", "test/core/linter_test.py::test__linter__linting_result__sum_dicts", "test/core/linter_test.py::test__linter__linting_result__combine_dicts", "test/core/linter_test.py::test__linter__linting_result_check_tuples_by_path[False-list]", "test/core/linter_test.py::test__linter__linting_result_check_tuples_by_path[True-dict]", "test/core/linter_test.py::test__linter__linting_result_get_violations[1]", "test/core/linter_test.py::test__linter__linting_result_get_violations[2]", "test/core/linter_test.py::test__linter__linting_parallel_thread[False]", "test/core/linter_test.py::test__linter__linting_parallel_thread[True]", "test/core/linter_test.py::test_lint_path_parallel_wrapper_exception", "test/core/linter_test.py::test__linter__linting_unexpected_error_handled_gracefully", "test/core/linter_test.py::test__linter__raises_malformed_noqa", "test/core/linter_test.py::test__linter__empty_file", "test/core/linter_test.py::test__linter__mask_templated_violations[True-check_tuples0]", "test/core/linter_test.py::test__linter__mask_templated_violations[False-check_tuples1]", "test/core/linter_test.py::test__linter__encoding[test/fixtures/linter/encoding-utf-8.sql-autodetect-False]", "test/core/linter_test.py::test__linter__encoding[test/fixtures/linter/encoding-utf-8-sig.sql-autodetect-False]", "test/core/linter_test.py::test__linter__encoding[test/fixtures/linter/encoding-utf-8.sql-utf-8-False]", "test/core/linter_test.py::test__linter__encoding[test/fixtures/linter/encoding-utf-8-sig.sql-utf-8-True]", "test/core/linter_test.py::test__linter__encoding[test/fixtures/linter/encoding-utf-8.sql-utf-8-sig-False]", "test/core/linter_test.py::test__linter__encoding[test/fixtures/linter/encoding-utf-8-sig.sql-utf-8-sig-False]", "test/core/linter_test.py::test_parse_noqa[-None]", "test/core/linter_test.py::test_parse_noqa[noqa-expected1]", "test/core/linter_test.py::test_parse_noqa[noqa?-SQLParseError]", "test/core/linter_test.py::test_parse_noqa[noqa:-expected3]", "test/core/linter_test.py::test_parse_noqa[noqa:L001,L002-expected4]", "test/core/linter_test.py::test_parse_noqa[noqa:", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[1_violation_no_ignore]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[1_violation_ignore_specific_line]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[1_violation_ignore_different_specific_line]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[1_violation_ignore_different_specific_rule]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[1_violation_ignore_enable_this_range]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[1_violation_ignore_disable_this_range]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[1_violation_line_1_ignore_disable_specific_2_3]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[1_violation_line_2_ignore_disable_specific_2_3]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[1_violation_line_3_ignore_disable_specific_2_3]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[1_violation_line_4_ignore_disable_specific_2_3]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[1_violation_line_1_ignore_disable_all_2_3]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[1_violation_line_2_ignore_disable_all_2_3]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[1_violation_line_3_ignore_disable_all_2_3]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[1_violation_line_4_ignore_disable_all_2_3]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[4_violations_two_types_disable_specific_enable_all]", "test/core/linter_test.py::test_linted_file_ignore_masked_violations[4_violations_two_types_disable_all_enable_specific]", "test/core/linter_test.py::test_linter_noqa", "test/core/linter_test.py::test_linter_noqa_with_templating", "test/core/linter_test.py::test_delayed_exception", "test/core/linter_test.py::test__attempt_to_change_templater_warning", "test/core/linter_test.py::test_safe_create_replace_file[incorrect_encoding]"]

**Base Commit**: a10057635e5b2559293a676486f0b730981f037a
**Environment Setup Commit**: 67023b85c41d23d6c6d69812a41b207c4f8a9331
