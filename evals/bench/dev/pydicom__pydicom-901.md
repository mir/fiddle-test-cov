# pydicom__pydicom-901

**Repository**: pydicom/pydicom
**Created**: 2019-07-27T00:18:11Z
**Version**: 1.3

## Problem Statement

pydicom should not define handler, formatter and log level.
The `config` module (imported when pydicom is imported) defines a handler and set the log level for the pydicom logger. This should not be the case IMO. It should be the responsibility of the client code of pydicom to configure the logging module to its convenience. Otherwise one end up having multiple logs record as soon as pydicom is imported:

Example:
```
Could not import pillow
2018-03-25 15:27:29,744 :: DEBUG :: pydicom 
  Could not import pillow
Could not import jpeg_ls
2018-03-25 15:27:29,745 :: DEBUG :: pydicom 
  Could not import jpeg_ls
Could not import gdcm
2018-03-25 15:27:29,745 :: DEBUG :: pydicom 
  Could not import gdcm
``` 
Or am I missing something?


## Hints

In addition, I don't understand what the purpose of the `config.debug` function since the default behavor of the logging module in absence of configuartion seems to already be the one you want.

From https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library:

> If the using application does not use logging, and library code makes logging calls, then (as described in the previous section) events of severity WARNING and greater will be printed to sys.stderr. This is regarded as the best default behaviour.

and

>**It is strongly advised that you do not add any handlers other than NullHandler to your library’s loggers.** This is because the configuration of handlers is the prerogative of the application developer who uses your library. The application developer knows their target audience and what handlers are most appropriate for their application: if you add handlers ‘under the hood’, you might well interfere with their ability to carry out unit tests and deliver logs which suit their requirements. 

I think you make good points here.  I support changing the logging to comply with python's suggested behavior.

> In addition, I don't understand what the purpose of the config.debug function

One reason is that the core loop in pydicom (data_element_generator in filereader.py) is extremely optimized for speed - it checks the `debugging` flag set by config.debug, to avoid composing messages and doing function calls to logger when not needed.

## Patch

```diff

diff --git a/pydicom/config.py b/pydicom/config.py
--- a/pydicom/config.py
+++ b/pydicom/config.py
@@ -62,10 +62,7 @@ def DS_decimal(use_Decimal_boolean=True):
 
 # Logging system and debug function to change logging level
 logger = logging.getLogger('pydicom')
-handler = logging.StreamHandler()
-formatter = logging.Formatter("%(message)s")
-handler.setFormatter(formatter)
-logger.addHandler(handler)
+logger.addHandler(logging.NullHandler())
 
 
 import pydicom.pixel_data_handlers.numpy_handler as np_handler  # noqa
@@ -110,16 +107,29 @@ def get_pixeldata(ds):
 """
 
 
-def debug(debug_on=True):
-    """Turn debugging of DICOM file reading and writing on or off.
+def debug(debug_on=True, default_handler=True):
+    """Turn on/off debugging of DICOM file reading and writing.
+
     When debugging is on, file location and details about the
     elements read at that location are logged to the 'pydicom'
     logger using python's logging module.
 
-    :param debug_on: True (default) to turn on debugging,
-    False to turn off.
+    Parameters
+    ----------
+    debug_on : bool, optional
+        If True (default) then turn on debugging, False to turn off.
+    default_handler : bool, optional
+        If True (default) then use ``logging.StreamHandler()`` as the handler
+        for log messages.
     """
     global logger, debugging
+
+    if default_handler:
+        handler = logging.StreamHandler()
+        formatter = logging.Formatter("%(message)s")
+        handler.setFormatter(formatter)
+        logger.addHandler(handler)
+
     if debug_on:
         logger.setLevel(logging.DEBUG)
         debugging = True
@@ -129,4 +139,4 @@ def debug(debug_on=True):
 
 
 # force level=WARNING, in case logging default is set differently (issue 103)
-debug(False)
+debug(False, False)


```

## Test Patch

```diff
diff --git a/pydicom/tests/test_config.py b/pydicom/tests/test_config.py
new file mode 100644
--- /dev/null
+++ b/pydicom/tests/test_config.py
@@ -0,0 +1,107 @@
+# Copyright 2008-2019 pydicom authors. See LICENSE file for details.
+"""Unit tests for the pydicom.config module."""
+
+import logging
+import sys
+
+import pytest
+
+from pydicom import dcmread
+from pydicom.config import debug
+from pydicom.data import get_testdata_files
+
+
+DS_PATH = get_testdata_files("CT_small.dcm")[0]
+PYTEST = [int(x) for x in pytest.__version__.split('.')]
+
+
+@pytest.mark.skipif(PYTEST[:2] < [3, 4], reason='no caplog')
+class TestDebug(object):
+    """Tests for config.debug()."""
+    def setup(self):
+        self.logger = logging.getLogger('pydicom')
+
+    def teardown(self):
+        # Reset to just NullHandler
+        self.logger.handlers = [self.logger.handlers[0]]
+
+    def test_default(self, caplog):
+        """Test that the default logging handler is a NullHandler."""
+        assert 1 == len(self.logger.handlers)
+        assert isinstance(self.logger.handlers[0], logging.NullHandler)
+
+        with caplog.at_level(logging.DEBUG, logger='pydicom'):
+            ds = dcmread(DS_PATH)
+
+            assert "Call to dcmread()" not in caplog.text
+            assert "Reading File Meta Information preamble..." in caplog.text
+            assert "Reading File Meta Information prefix..." in caplog.text
+            assert "00000080: 'DICM' prefix found" in caplog.text
+
+    def test_debug_on_handler_null(self, caplog):
+        """Test debug(True, False)."""
+        debug(True, False)
+        assert 1 == len(self.logger.handlers)
+        assert isinstance(self.logger.handlers[0], logging.NullHandler)
+
+        with caplog.at_level(logging.DEBUG, logger='pydicom'):
+            ds = dcmread(DS_PATH)
+
+            assert "Call to dcmread()" in caplog.text
+            assert "Reading File Meta Information preamble..." in caplog.text
+            assert "Reading File Meta Information prefix..." in caplog.text
+            assert "00000080: 'DICM' prefix found" in caplog.text
+            msg = (
+                "00009848: fc ff fc ff 4f 42 00 00 7e 00 00 00    "
+                "(fffc, fffc) OB Length: 126"
+            )
+            assert msg in caplog.text
+
+    def test_debug_off_handler_null(self, caplog):
+        """Test debug(False, False)."""
+        debug(False, False)
+        assert 1 == len(self.logger.handlers)
+        assert isinstance(self.logger.handlers[0], logging.NullHandler)
+
+        with caplog.at_level(logging.DEBUG, logger='pydicom'):
+            ds = dcmread(DS_PATH)
+
+            assert "Call to dcmread()" not in caplog.text
+            assert "Reading File Meta Information preamble..." in caplog.text
+            assert "Reading File Meta Information prefix..." in caplog.text
+            assert "00000080: 'DICM' prefix found" in caplog.text
+
+    def test_debug_on_handler_stream(self, caplog):
+        """Test debug(True, True)."""
+        debug(True, True)
+        assert 2 == len(self.logger.handlers)
+        assert isinstance(self.logger.handlers[0], logging.NullHandler)
+        assert isinstance(self.logger.handlers[1], logging.StreamHandler)
+
+        with caplog.at_level(logging.DEBUG, logger='pydicom'):
+            ds = dcmread(DS_PATH)
+
+            assert "Call to dcmread()" in caplog.text
+            assert "Reading File Meta Information preamble..." in caplog.text
+            assert "Reading File Meta Information prefix..." in caplog.text
+            assert "00000080: 'DICM' prefix found" in caplog.text
+            msg = (
+                "00009848: fc ff fc ff 4f 42 00 00 7e 00 00 00    "
+                "(fffc, fffc) OB Length: 126"
+            )
+            assert msg in caplog.text
+
+    def test_debug_off_handler_stream(self, caplog):
+        """Test debug(False, True)."""
+        debug(False, True)
+        assert 2 == len(self.logger.handlers)
+        assert isinstance(self.logger.handlers[0], logging.NullHandler)
+        assert isinstance(self.logger.handlers[1], logging.StreamHandler)
+
+        with caplog.at_level(logging.DEBUG, logger='pydicom'):
+            ds = dcmread(DS_PATH)
+
+            assert "Call to dcmread()" not in caplog.text
+            assert "Reading File Meta Information preamble..." in caplog.text
+            assert "Reading File Meta Information prefix..." in caplog.text
+            assert "00000080: 'DICM' prefix found" in caplog.text

```

## Test Information

**Tests that should FAIL→PASS**: ["pydicom/tests/test_config.py::TestDebug::test_default", "pydicom/tests/test_config.py::TestDebug::test_debug_on_handler_null", "pydicom/tests/test_config.py::TestDebug::test_debug_off_handler_null", "pydicom/tests/test_config.py::TestDebug::test_debug_on_handler_stream", "pydicom/tests/test_config.py::TestDebug::test_debug_off_handler_stream"]

**Tests that should PASS→PASS**: []

**Base Commit**: 3746878d8edf1cbda6fbcf35eec69f9ba79301ca
**Environment Setup Commit**: 7241f5d9db0de589b230bb84212fbb643a7c86c3
