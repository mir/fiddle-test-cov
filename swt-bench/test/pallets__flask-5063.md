# pallets__flask-5063

**Repository**: pallets/flask
**Created**: 2023-04-14T16:36:54Z
**Version**: 2.3

## Problem Statement

Flask routes to return domain/sub-domains information
Currently when checking **flask routes** it provides all routes but **it is no way to see which routes are assigned to which subdomain**.

**Default server name:**
SERVER_NAME: 'test.local'

**Domains (sub-domains):**
test.test.local
admin.test.local
test.local

**Adding blueprints:**
app.register_blueprint(admin_blueprint,url_prefix='',subdomain='admin')
app.register_blueprint(test_subdomain_blueprint,url_prefix='',subdomain='test')


```
$ flask routes
 * Tip: There are .env or .flaskenv files present. Do "pip install python-dotenv" to use them.
Endpoint                                                 Methods    Rule
-------------------------------------------------------  ---------  ------------------------------------------------
admin_blueprint.home                                      GET        /home
test_subdomain_blueprint.home                             GET        /home
static                                                    GET        /static/<path:filename>
...
```


**Feature request**
It will be good to see something like below (that will make more clear which route for which subdomain, because now need to go and check configuration).
**If it is not possible to fix routes**, can you add or tell which method(s) should be used to get below information from flask? 

```
$ flask routes
 * Tip: There are .env or .flaskenv files present. Do "pip install python-dotenv" to use them.
Domain                Endpoint                                             Methods    Rule
-----------------   ----------------------------------------------------  ----------  ------------------------------------------------
admin.test.local     admin_blueprint.home                                  GET        /home
test.test.local      test_subdomain_blueprint.home                         GET        /home
test.local           static                                                GET        /static/<path:filename>
...
```



## Patch

```diff

diff --git a/src/flask/cli.py b/src/flask/cli.py
--- a/src/flask/cli.py
+++ b/src/flask/cli.py
@@ -9,7 +9,7 @@
 import traceback
 import typing as t
 from functools import update_wrapper
-from operator import attrgetter
+from operator import itemgetter
 
 import click
 from click.core import ParameterSource
@@ -989,49 +989,62 @@ def shell_command() -> None:
 @click.option(
     "--sort",
     "-s",
-    type=click.Choice(("endpoint", "methods", "rule", "match")),
+    type=click.Choice(("endpoint", "methods", "domain", "rule", "match")),
     default="endpoint",
     help=(
-        'Method to sort routes by. "match" is the order that Flask will match '
-        "routes when dispatching a request."
+        "Method to sort routes by. 'match' is the order that Flask will match routes"
+        " when dispatching a request."
     ),
 )
 @click.option("--all-methods", is_flag=True, help="Show HEAD and OPTIONS methods.")
 @with_appcontext
 def routes_command(sort: str, all_methods: bool) -> None:
     """Show all registered routes with endpoints and methods."""
-
     rules = list(current_app.url_map.iter_rules())
+
     if not rules:
         click.echo("No routes were registered.")
         return
 
-    ignored_methods = set(() if all_methods else ("HEAD", "OPTIONS"))
+    ignored_methods = set() if all_methods else {"HEAD", "OPTIONS"}
+    host_matching = current_app.url_map.host_matching
+    has_domain = any(rule.host if host_matching else rule.subdomain for rule in rules)
+    rows = []
 
-    if sort in ("endpoint", "rule"):
-        rules = sorted(rules, key=attrgetter(sort))
-    elif sort == "methods":
-        rules = sorted(rules, key=lambda rule: sorted(rule.methods))  # type: ignore
+    for rule in rules:
+        row = [
+            rule.endpoint,
+            ", ".join(sorted((rule.methods or set()) - ignored_methods)),
+        ]
 
-    rule_methods = [
-        ", ".join(sorted(rule.methods - ignored_methods))  # type: ignore
-        for rule in rules
-    ]
+        if has_domain:
+            row.append((rule.host if host_matching else rule.subdomain) or "")
 
-    headers = ("Endpoint", "Methods", "Rule")
-    widths = (
-        max(len(rule.endpoint) for rule in rules),
-        max(len(methods) for methods in rule_methods),
-        max(len(rule.rule) for rule in rules),
-    )
-    widths = [max(len(h), w) for h, w in zip(headers, widths)]
-    row = "{{0:<{0}}}  {{1:<{1}}}  {{2:<{2}}}".format(*widths)
+        row.append(rule.rule)
+        rows.append(row)
+
+    headers = ["Endpoint", "Methods"]
+    sorts = ["endpoint", "methods"]
+
+    if has_domain:
+        headers.append("Host" if host_matching else "Subdomain")
+        sorts.append("domain")
+
+    headers.append("Rule")
+    sorts.append("rule")
+
+    try:
+        rows.sort(key=itemgetter(sorts.index(sort)))
+    except ValueError:
+        pass
 
-    click.echo(row.format(*headers).strip())
-    click.echo(row.format(*("-" * width for width in widths)))
+    rows.insert(0, headers)
+    widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
+    rows.insert(1, ["-" * w for w in widths])
+    template = "  ".join(f"{{{i}:<{w}}}" for i, w in enumerate(widths))
 
-    for rule, methods in zip(rules, rule_methods):
-        click.echo(row.format(rule.endpoint, methods, rule.rule).rstrip())
+    for row in rows:
+        click.echo(template.format(*row))
 
 
 cli = FlaskGroup(


```

## Test Patch

```diff
diff --git a/tests/test_cli.py b/tests/test_cli.py
--- a/tests/test_cli.py
+++ b/tests/test_cli.py
@@ -433,16 +433,12 @@ class TestRoutes:
     @pytest.fixture
     def app(self):
         app = Flask(__name__)
-        app.testing = True
-
-        @app.route("/get_post/<int:x>/<int:y>", methods=["GET", "POST"])
-        def yyy_get_post(x, y):
-            pass
-
-        @app.route("/zzz_post", methods=["POST"])
-        def aaa_post():
-            pass
-
+        app.add_url_rule(
+            "/get_post/<int:x>/<int:y>",
+            methods=["GET", "POST"],
+            endpoint="yyy_get_post",
+        )
+        app.add_url_rule("/zzz_post", methods=["POST"], endpoint="aaa_post")
         return app
 
     @pytest.fixture
@@ -450,17 +446,6 @@ def invoke(self, app, runner):
         cli = FlaskGroup(create_app=lambda: app)
         return partial(runner.invoke, cli)
 
-    @pytest.fixture
-    def invoke_no_routes(self, runner):
-        def create_app():
-            app = Flask(__name__, static_folder=None)
-            app.testing = True
-
-            return app
-
-        cli = FlaskGroup(create_app=create_app)
-        return partial(runner.invoke, cli)
-
     def expect_order(self, order, output):
         # skip the header and match the start of each row
         for expect, line in zip(order, output.splitlines()[2:]):
@@ -493,11 +478,31 @@ def test_all_methods(self, invoke):
         output = invoke(["routes", "--all-methods"]).output
         assert "GET, HEAD, OPTIONS, POST" in output
 
-    def test_no_routes(self, invoke_no_routes):
-        result = invoke_no_routes(["routes"])
+    def test_no_routes(self, runner):
+        app = Flask(__name__, static_folder=None)
+        cli = FlaskGroup(create_app=lambda: app)
+        result = runner.invoke(cli, ["routes"])
         assert result.exit_code == 0
         assert "No routes were registered." in result.output
 
+    def test_subdomain(self, runner):
+        app = Flask(__name__, static_folder=None)
+        app.add_url_rule("/a", subdomain="a", endpoint="a")
+        app.add_url_rule("/b", subdomain="b", endpoint="b")
+        cli = FlaskGroup(create_app=lambda: app)
+        result = runner.invoke(cli, ["routes"])
+        assert result.exit_code == 0
+        assert "Subdomain" in result.output
+
+    def test_host(self, runner):
+        app = Flask(__name__, static_folder=None, host_matching=True)
+        app.add_url_rule("/a", host="a", endpoint="a")
+        app.add_url_rule("/b", host="b", endpoint="b")
+        cli = FlaskGroup(create_app=lambda: app)
+        result = runner.invoke(cli, ["routes"])
+        assert result.exit_code == 0
+        assert "Host" in result.output
+
 
 def dotenv_not_available():
     try:

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/test_cli.py::TestRoutes::test_subdomain", "tests/test_cli.py::TestRoutes::test_host"]

**Tests that should PASS→PASS**: ["tests/test_cli.py::test_cli_name", "tests/test_cli.py::test_find_best_app", "tests/test_cli.py::test_prepare_import[test-path0-test]", "tests/test_cli.py::test_prepare_import[test.py-path1-test]", "tests/test_cli.py::test_prepare_import[a/test-path2-test]", "tests/test_cli.py::test_prepare_import[test/__init__.py-path3-test]", "tests/test_cli.py::test_prepare_import[test/__init__-path4-test]", "tests/test_cli.py::test_prepare_import[value5-path5-cliapp.inner1]", "tests/test_cli.py::test_prepare_import[value6-path6-cliapp.inner1.inner2]", "tests/test_cli.py::test_prepare_import[test.a.b-path7-test.a.b]", "tests/test_cli.py::test_prepare_import[value8-path8-cliapp.app]", "tests/test_cli.py::test_prepare_import[value9-path9-cliapp.message.txt]", "tests/test_cli.py::test_locate_app[cliapp.app-None-testapp]", "tests/test_cli.py::test_locate_app[cliapp.app-testapp-testapp]", "tests/test_cli.py::test_locate_app[cliapp.factory-None-app]", "tests/test_cli.py::test_locate_app[cliapp.factory-create_app-app]", "tests/test_cli.py::test_locate_app[cliapp.factory-create_app()-app]", "tests/test_cli.py::test_locate_app[cliapp.factory-create_app2(\"foo\",", "tests/test_cli.py::test_locate_app[cliapp.factory-", "tests/test_cli.py::test_locate_app_raises[notanapp.py-None]", "tests/test_cli.py::test_locate_app_raises[cliapp/app-None]", "tests/test_cli.py::test_locate_app_raises[cliapp.app-notanapp]", "tests/test_cli.py::test_locate_app_raises[cliapp.factory-create_app2(\"foo\")]", "tests/test_cli.py::test_locate_app_raises[cliapp.factory-create_app(]", "tests/test_cli.py::test_locate_app_raises[cliapp.factory-no_app]", "tests/test_cli.py::test_locate_app_raises[cliapp.importerrorapp-None]", "tests/test_cli.py::test_locate_app_raises[cliapp.message.txt-None]", "tests/test_cli.py::test_locate_app_suppress_raise", "tests/test_cli.py::test_get_version", "tests/test_cli.py::test_scriptinfo", "tests/test_cli.py::test_app_cli_has_app_context", "tests/test_cli.py::test_with_appcontext", "tests/test_cli.py::test_appgroup_app_context", "tests/test_cli.py::test_flaskgroup_app_context", "tests/test_cli.py::test_flaskgroup_debug[True]", "tests/test_cli.py::test_flaskgroup_debug[False]", "tests/test_cli.py::test_flaskgroup_nested", "tests/test_cli.py::test_no_command_echo_loading_error", "tests/test_cli.py::test_help_echo_loading_error", "tests/test_cli.py::test_help_echo_exception", "tests/test_cli.py::TestRoutes::test_simple", "tests/test_cli.py::TestRoutes::test_sort", "tests/test_cli.py::TestRoutes::test_all_methods", "tests/test_cli.py::TestRoutes::test_no_routes", "tests/test_cli.py::test_load_dotenv", "tests/test_cli.py::test_dotenv_path", "tests/test_cli.py::test_dotenv_optional", "tests/test_cli.py::test_disable_dotenv_from_env", "tests/test_cli.py::test_run_cert_path", "tests/test_cli.py::test_run_cert_adhoc", "tests/test_cli.py::test_run_cert_import", "tests/test_cli.py::test_run_cert_no_ssl", "tests/test_cli.py::test_cli_blueprints", "tests/test_cli.py::test_cli_empty"]

**Base Commit**: 182ce3dd15dfa3537391c3efaf9c3ff407d134d4
**Environment Setup Commit**: 182ce3dd15dfa3537391c3efaf9c3ff407d134d4
