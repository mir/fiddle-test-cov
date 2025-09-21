# pylint-dev__pylint-5859

**Repository**: pylint-dev/pylint
**Created**: 2022-03-04T00:01:54Z
**Version**: 2.13

## Problem Statement

"--notes" option ignores note tags that are entirely punctuation
### Bug description

If a note tag specified with the `--notes` option is entirely punctuation, pylint won't report a fixme warning (W0511).

```python
# YES: yes
# ???: no
```

`pylint test.py --notes="YES,???"` will return a fixme warning (W0511) for the first line, but not the second.

### Configuration

```ini
Default
```


### Command used

```shell
pylint test.py --notes="YES,???"
```


### Pylint output

```shell
************* Module test
test.py:1:1: W0511: YES: yes (fixme)
```


### Expected behavior

```
************* Module test
test.py:1:1: W0511: YES: yes (fixme)
test.py:2:1: W0511: ???: no (fixme)
```

### Pylint version

```shell
pylint 2.12.2
astroid 2.9.0
Python 3.10.2 (main, Feb  2 2022, 05:51:25) [Clang 13.0.0 (clang-1300.0.29.3)]
```


### OS / Environment

macOS 11.6.1

### Additional dependencies

_No response_


## Hints

Did a little investigation, this is we're actually converting this option in a regular expression pattern (thereby making it awfully similar to the `notes-rgx` option). Since `?` is a special character in regex this doesn't get picked up. Using `\?\?\?` in either `notes` or `notes-rgx` should work.

## Patch

```diff

diff --git a/pylint/checkers/misc.py b/pylint/checkers/misc.py
--- a/pylint/checkers/misc.py
+++ b/pylint/checkers/misc.py
@@ -121,9 +121,9 @@ def open(self):
 
         notes = "|".join(re.escape(note) for note in self.config.notes)
         if self.config.notes_rgx:
-            regex_string = rf"#\s*({notes}|{self.config.notes_rgx})\b"
+            regex_string = rf"#\s*({notes}|{self.config.notes_rgx})(?=(:|\s|\Z))"
         else:
-            regex_string = rf"#\s*({notes})\b"
+            regex_string = rf"#\s*({notes})(?=(:|\s|\Z))"
 
         self._fixme_pattern = re.compile(regex_string, re.I)
 


```

## Test Patch

```diff
diff --git a/tests/checkers/unittest_misc.py b/tests/checkers/unittest_misc.py
--- a/tests/checkers/unittest_misc.py
+++ b/tests/checkers/unittest_misc.py
@@ -68,6 +68,16 @@ def test_without_space_fixme(self) -> None:
         ):
             self.checker.process_tokens(_tokenize_str(code))
 
+    @set_config(notes=["???"])
+    def test_non_alphanumeric_codetag(self) -> None:
+        code = """a = 1
+                #???
+                """
+        with self.assertAddsMessages(
+            MessageTest(msg_id="fixme", line=2, args="???", col_offset=17)
+        ):
+            self.checker.process_tokens(_tokenize_str(code))
+
     @set_config(notes=[])
     def test_absent_codetag(self) -> None:
         code = """a = 1

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/checkers/unittest_misc.py::TestFixme::test_non_alphanumeric_codetag"]

**Tests that should PASS→PASS**: ["tests/checkers/unittest_misc.py::TestFixme::test_fixme_with_message", "tests/checkers/unittest_misc.py::TestFixme::test_todo_without_message", "tests/checkers/unittest_misc.py::TestFixme::test_xxx_without_space", "tests/checkers/unittest_misc.py::TestFixme::test_xxx_middle", "tests/checkers/unittest_misc.py::TestFixme::test_without_space_fixme", "tests/checkers/unittest_misc.py::TestFixme::test_absent_codetag", "tests/checkers/unittest_misc.py::TestFixme::test_other_present_codetag", "tests/checkers/unittest_misc.py::TestFixme::test_issue_2321_should_not_trigger", "tests/checkers/unittest_misc.py::TestFixme::test_issue_2321_should_trigger", "tests/checkers/unittest_misc.py::TestFixme::test_dont_trigger_on_todoist"]

**Base Commit**: 182cc539b8154c0710fcea7e522267e42eba8899
**Environment Setup Commit**: 3b2fbaec045697d53bdd4435e59dbfc2b286df4b
