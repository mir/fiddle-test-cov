# django__django-15781

**Repository**: django/django
**Created**: 2022-06-18T19:39:34Z
**Version**: 4.2

## Problem Statement

Customizable management command formatters.
Description
	
With code like:
class Command(BaseCommand):
	help = '''
	Import a contract from tzkt.
	Example usage:
		./manage.py tzkt_import 'Tezos Mainnet' KT1HTDtMBRCKoNHjfWEEvXneGQpCfPAt6BRe
	'''
Help output is:
$ ./manage.py help tzkt_import
usage: manage.py tzkt_import [-h] [--api API] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
							 [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color]
							 [--skip-checks]
							 blockchain target
Import a contract from tzkt Example usage: ./manage.py tzkt_import 'Tezos Mainnet'
KT1HTDtMBRCKoNHjfWEEvXneGQpCfPAt6BRe
positional arguments:
 blockchain			Name of the blockchain to import into
 target				Id of the contract to import
When that was expected:
$ ./manage.py help tzkt_import
usage: manage.py tzkt_import [-h] [--api API] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
							 [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color]
							 [--skip-checks]
							 blockchain target
Import a contract from tzkt 
Example usage: 
	./manage.py tzkt_import 'Tezos Mainnet' KT1HTDtMBRCKoNHjfWEEvXneGQpCfPAt6BRe
positional arguments:
 blockchain			Name of the blockchain to import into
 target				Id of the contract to import


## Hints

This seems no fault of Django but is rather ​the default behavior of ArgumentParser ("By default, ArgumentParser objects line-wrap the description and epilog texts in command-line help messages"). This can be changed by using a custom ​formatter_class, though Django already specifies a custom one (​DjangoHelpFormatter).
It seems reasonable, to make it customizable by passing via kwargs to the ​BaseCommand.create_parser() (as documented): django/core/management/base.py diff --git a/django/core/management/base.py b/django/core/management/base.py index f0e711ac76..52407807d8 100644 a b class BaseCommand: 286286 Create and return the ``ArgumentParser`` which will be used to 287287 parse the arguments to this command. 288288 """ 289 kwargs.setdefault("formatter_class", DjangoHelpFormatter) 289290 parser = CommandParser( 290291 prog="%s %s" % (os.path.basename(prog_name), subcommand), 291292 description=self.help or None, 292 formatter_class=DjangoHelpFormatter, 293293 missing_args_message=getattr(self, "missing_args_message", None), 294294 called_from_command_line=getattr(self, "_called_from_command_line", None), 295295 **kwargs, What do you think?
Looks good but I don't see a reason for keeping a default that swallows newlines because PEP257 forbids having a multiline sentence on the first line anyway: Multi-line docstrings consist of a summary line just like a one-line docstring, followed by a blank line, followed by a more elaborate description. As such, the default formater which purpose is to unwrap the first sentence encourages breaking PEP 257. And users who are naturally complying with PEP257 will have to override the formatter, it should be the other way around.
Also, the not-unwraping formater will also look fine with existing docstrings, it will work for both use cases, while the current one only works for one use case and breaks the other. The default formater should work for both
Replying to James Pic: Also, the not-unwraping formater will also look fine with existing docstrings, it will work for both use cases, while the current one only works for one use case and breaks the other. The default formater should work for both It seems you think that Python's (not Django's) default behavior should be changed according to PEP 257. I'd recommend to start a discussion in Python's bugtracker. As far as I'm aware the proposed solution will allow users to freely change a formatter, which should be enough from the Django point of view.
No, I think that Django's default behavior should match Python's PEP 257, and at the same time, have a default that works in all use cases. I think my report and comments are pretty clear, I fail to understand how you could get my comment completely backward, so, unless you have any specific question about this statement, I'm going to give up on this.
So as part of this issue, do we make changes to allow a user to override the formatter through kwargs and also keep DjangoHelpFormatter as the default?
Replying to Subhankar Hotta: So as part of this issue, do we make changes to allow a user to override the formatter through kwargs and also keep DjangoHelpFormatter as the default? Yes, see comment.

## Patch

```diff

diff --git a/django/core/management/base.py b/django/core/management/base.py
--- a/django/core/management/base.py
+++ b/django/core/management/base.py
@@ -286,10 +286,10 @@ def create_parser(self, prog_name, subcommand, **kwargs):
         Create and return the ``ArgumentParser`` which will be used to
         parse the arguments to this command.
         """
+        kwargs.setdefault("formatter_class", DjangoHelpFormatter)
         parser = CommandParser(
             prog="%s %s" % (os.path.basename(prog_name), subcommand),
             description=self.help or None,
-            formatter_class=DjangoHelpFormatter,
             missing_args_message=getattr(self, "missing_args_message", None),
             called_from_command_line=getattr(self, "_called_from_command_line", None),
             **kwargs,


```

## Test Patch

```diff
diff --git a/tests/user_commands/tests.py b/tests/user_commands/tests.py
--- a/tests/user_commands/tests.py
+++ b/tests/user_commands/tests.py
@@ -1,4 +1,5 @@
 import os
+from argparse import ArgumentDefaultsHelpFormatter
 from io import StringIO
 from unittest import mock
 
@@ -408,8 +409,14 @@ def test_subparser_invalid_option(self):
     def test_create_parser_kwargs(self):
         """BaseCommand.create_parser() passes kwargs to CommandParser."""
         epilog = "some epilog text"
-        parser = BaseCommand().create_parser("prog_name", "subcommand", epilog=epilog)
+        parser = BaseCommand().create_parser(
+            "prog_name",
+            "subcommand",
+            epilog=epilog,
+            formatter_class=ArgumentDefaultsHelpFormatter,
+        )
         self.assertEqual(parser.epilog, epilog)
+        self.assertEqual(parser.formatter_class, ArgumentDefaultsHelpFormatter)
 
     def test_outputwrapper_flush(self):
         out = StringIO()

```

## Test Information

**Tests that should FAIL→PASS**: ["BaseCommand.create_parser() passes kwargs to CommandParser."]

**Tests that should PASS→PASS**: ["test_get_random_secret_key (user_commands.tests.UtilsTests)", "test_is_ignored_path_false (user_commands.tests.UtilsTests)", "test_is_ignored_path_true (user_commands.tests.UtilsTests)", "test_no_existent_external_program (user_commands.tests.UtilsTests)", "test_normalize_path_patterns_truncates_wildcard_base (user_commands.tests.UtilsTests)", "By default, call_command should not trigger the check framework, unless", "When passing the long option name to call_command, the available option", "It should be possible to pass non-string arguments to call_command.", "test_call_command_unrecognized_option (user_commands.tests.CommandTests)", "test_call_command_with_required_parameters_in_mixed_options (user_commands.tests.CommandTests)", "test_call_command_with_required_parameters_in_options (user_commands.tests.CommandTests)", "test_calling_a_command_with_no_app_labels_and_parameters_raise_command_error (user_commands.tests.CommandTests)", "test_calling_a_command_with_only_empty_parameter_should_ends_gracefully (user_commands.tests.CommandTests)", "test_calling_command_with_app_labels_and_parameters_should_be_ok (user_commands.tests.CommandTests)", "test_calling_command_with_parameters_and_app_labels_at_the_end_should_be_ok (user_commands.tests.CommandTests)", "test_check_migrations (user_commands.tests.CommandTests)", "test_command (user_commands.tests.CommandTests)", "test_command_add_arguments_after_common_arguments (user_commands.tests.CommandTests)", "test_command_style (user_commands.tests.CommandTests)", "Management commands can also be loaded from Python eggs.", "An unknown command raises CommandError", "find_command should still work when the PATH environment variable", "test_language_preserved (user_commands.tests.CommandTests)", "test_mutually_exclusive_group_required_const_options (user_commands.tests.CommandTests)", "test_mutually_exclusive_group_required_options (user_commands.tests.CommandTests)", "test_mutually_exclusive_group_required_with_same_dest_args (user_commands.tests.CommandTests)", "test_mutually_exclusive_group_required_with_same_dest_options (user_commands.tests.CommandTests)", "When the Command handle method is decorated with @no_translations,", "test_output_transaction (user_commands.tests.CommandTests)", "test_outputwrapper_flush (user_commands.tests.CommandTests)", "test_required_const_options (user_commands.tests.CommandTests)", "test_required_list_option (user_commands.tests.CommandTests)", "test_requires_system_checks_empty (user_commands.tests.CommandTests)", "test_requires_system_checks_invalid (user_commands.tests.CommandTests)", "test_requires_system_checks_specific (user_commands.tests.CommandTests)", "test_subparser (user_commands.tests.CommandTests)", "test_subparser_dest_args (user_commands.tests.CommandTests)", "test_subparser_dest_required_args (user_commands.tests.CommandTests)", "test_subparser_invalid_option (user_commands.tests.CommandTests)", "Exception raised in a command should raise CommandError with", "To avoid conflicts with custom options, commands don't allow", "test_script_prefix_set_in_commands (user_commands.tests.CommandRunTests)", "test_skip_checks (user_commands.tests.CommandRunTests)"]

**Base Commit**: 8d160f154f0240a423e83ffe0690e472f837373c
**Environment Setup Commit**: 0fbdb9784da915fce5dcc1fe82bac9b4785749e5
