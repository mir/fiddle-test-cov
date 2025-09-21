# sqlfluff__sqlfluff-1625

**Repository**: sqlfluff/sqlfluff
**Created**: 2021-10-13T11:35:29Z
**Version**: 0.6

## Problem Statement

TSQL - L031 incorrectly triggers "Avoid using aliases in join condition" when no join present
## Expected Behaviour

Both of these queries should pass, the only difference is the addition of a table alias 'a':

1/ no alias

```
SELECT [hello]
FROM
    mytable
```

2/ same query with alias

```
SELECT a.[hello]
FROM
    mytable AS a
```

## Observed Behaviour

1/ passes
2/ fails with: L031: Avoid using aliases in join condition.

But there is no join condition :-)

## Steps to Reproduce

Lint queries above

## Dialect

TSQL

## Version

sqlfluff 0.6.9
Python 3.6.9

## Configuration

N/A


## Hints

Actually, re-reading the docs I think this is the intended behaviour... closing

## Patch

```diff

diff --git a/src/sqlfluff/rules/L031.py b/src/sqlfluff/rules/L031.py
--- a/src/sqlfluff/rules/L031.py
+++ b/src/sqlfluff/rules/L031.py
@@ -211,7 +211,7 @@ def _lint_aliases_in_join(
             violation_buff.append(
                 LintResult(
                     anchor=alias_info.alias_identifier_ref,
-                    description="Avoid using aliases in join condition",
+                    description="Avoid aliases in from clauses and join conditions.",
                     fixes=fixes,
                 )
             )


```

## Test Patch

```diff
diff --git a/test/cli/commands_test.py b/test/cli/commands_test.py
--- a/test/cli/commands_test.py
+++ b/test/cli/commands_test.py
@@ -49,7 +49,7 @@ def invoke_assert_code(
 expected_output = """== [test/fixtures/linter/indentation_error_simple.sql] FAIL
 L:   2 | P:   4 | L003 | Indentation not hanging or a multiple of 4 spaces
 L:   5 | P:  10 | L010 | Keywords must be consistently upper case.
-L:   5 | P:  13 | L031 | Avoid using aliases in join condition
+L:   5 | P:  13 | L031 | Avoid aliases in from clauses and join conditions.
 """
 
 

```

## Test Information

**Tests that should FAIL→PASS**: ["test/cli/commands_test.py::test__cli__command_directed"]

**Tests that should PASS→PASS**: ["test/cli/commands_test.py::test__cli__command_dialect", "test/cli/commands_test.py::test__cli__command_dialect_legacy", "test/cli/commands_test.py::test__cli__command_lint_stdin[command0]", "test/cli/commands_test.py::test__cli__command_lint_stdin[command1]", "test/cli/commands_test.py::test__cli__command_lint_stdin[command2]", "test/cli/commands_test.py::test__cli__command_lint_stdin[command3]", "test/cli/commands_test.py::test__cli__command_lint_parse[command0]", "test/cli/commands_test.py::test__cli__command_lint_parse[command1]", "test/cli/commands_test.py::test__cli__command_lint_parse[command2]", "test/cli/commands_test.py::test__cli__command_lint_parse[command3]", "test/cli/commands_test.py::test__cli__command_lint_parse[command4]", "test/cli/commands_test.py::test__cli__command_lint_parse[command5]", "test/cli/commands_test.py::test__cli__command_lint_parse[command6]", "test/cli/commands_test.py::test__cli__command_lint_parse[command7]", "test/cli/commands_test.py::test__cli__command_lint_parse[command8]", "test/cli/commands_test.py::test__cli__command_lint_parse[command9]", "test/cli/commands_test.py::test__cli__command_lint_parse[command10]", "test/cli/commands_test.py::test__cli__command_lint_parse[command11]", "test/cli/commands_test.py::test__cli__command_lint_parse[command12]", "test/cli/commands_test.py::test__cli__command_lint_parse[command13]", "test/cli/commands_test.py::test__cli__command_lint_parse[command14]", "test/cli/commands_test.py::test__cli__command_lint_parse[command15]", "test/cli/commands_test.py::test__cli__command_lint_parse[command16]", "test/cli/commands_test.py::test__cli__command_lint_parse[command17]", "test/cli/commands_test.py::test__cli__command_lint_parse[command18]", "test/cli/commands_test.py::test__cli__command_lint_parse[command19]", "test/cli/commands_test.py::test__cli__command_lint_parse[command20]", "test/cli/commands_test.py::test__cli__command_lint_parse[command21]", "test/cli/commands_test.py::test__cli__command_lint_parse_with_retcode[command0-1]", "test/cli/commands_test.py::test__cli__command_lint_parse_with_retcode[command1-1]", "test/cli/commands_test.py::test__cli__command_lint_parse_with_retcode[command2-1]", "test/cli/commands_test.py::test__cli__command_lint_warning_explicit_file_ignored", "test/cli/commands_test.py::test__cli__command_lint_skip_ignore_files", "test/cli/commands_test.py::test__cli__command_versioning", "test/cli/commands_test.py::test__cli__command_version", "test/cli/commands_test.py::test__cli__command_rules", "test/cli/commands_test.py::test__cli__command_dialects", "test/cli/commands_test.py::test__cli__command__fix[L001-test/fixtures/linter/indentation_errors.sql]", "test/cli/commands_test.py::test__cli__command__fix[L008-test/fixtures/linter/whitespace_errors.sql]", "test/cli/commands_test.py::test__cli__command__fix[L008-test/fixtures/linter/indentation_errors.sql]", "test/cli/commands_test.py::test__cli__command__fix[L003-test/fixtures/linter/indentation_error_hard.sql]", "test/cli/commands_test.py::test__cli__command_fix_stdin[select", "test/cli/commands_test.py::test__cli__command_fix_stdin[", "test/cli/commands_test.py::test__cli__command_fix_stdin[SELECT", "test/cli/commands_test.py::test__cli__command_fix_stdin_logging_to_stderr", "test/cli/commands_test.py::test__cli__command_fix_stdin_safety", "test/cli/commands_test.py::test__cli__command_fix_stdin_error_exit_code[create", "test/cli/commands_test.py::test__cli__command_fix_stdin_error_exit_code[select", "test/cli/commands_test.py::test__cli__command__fix_no_force[L001-test/fixtures/linter/indentation_errors.sql-y-0-0]", "test/cli/commands_test.py::test__cli__command__fix_no_force[L001-test/fixtures/linter/indentation_errors.sql-n-65-1]", "test/cli/commands_test.py::test__cli__command_parse_serialize_from_stdin[yaml]", "test/cli/commands_test.py::test__cli__command_parse_serialize_from_stdin[json]", "test/cli/commands_test.py::test__cli__command_lint_serialize_from_stdin[select", "test/cli/commands_test.py::test__cli__command_lint_serialize_from_stdin[SElect", "test/cli/commands_test.py::test__cli__command_fail_nice_not_found[command0]", "test/cli/commands_test.py::test__cli__command_fail_nice_not_found[command1]", "test/cli/commands_test.py::test__cli__command_lint_serialize_multiple_files[yaml]", "test/cli/commands_test.py::test__cli__command_lint_serialize_multiple_files[json]", "test/cli/commands_test.py::test__cli__command_lint_serialize_multiple_files[github-annotation]", "test/cli/commands_test.py::test__cli__command_lint_serialize_github_annotation", "test/cli/commands_test.py::test___main___help", "test/cli/commands_test.py::test_encoding[utf-8-ascii]", "test/cli/commands_test.py::test_encoding[utf-8-sig-UTF-8-SIG]", "test/cli/commands_test.py::test_encoding[utf-32-UTF-32]"]

**Base Commit**: 14e1a23a3166b9a645a16de96f694c77a5d4abb7
**Environment Setup Commit**: 67023b85c41d23d6c6d69812a41b207c4f8a9331
