# matplotlib__matplotlib-23299

**Repository**: matplotlib/matplotlib
**Created**: 2022-06-18T01:34:39Z
**Version**: 3.5

## Problem Statement

[Bug]: get_backend() clears figures from Gcf.figs if they were created under rc_context
### Bug summary

calling `matplotlib.get_backend()` removes all figures from `Gcf` if the *first* figure in `Gcf.figs` was created in an `rc_context`.

### Code for reproduction

```python
import matplotlib.pyplot as plt
from matplotlib import get_backend, rc_context

# fig1 = plt.figure()  # <- UNCOMMENT THIS LINE AND IT WILL WORK
# plt.ion()            # <- ALTERNATIVELY, UNCOMMENT THIS LINE AND IT WILL ALSO WORK
with rc_context():
    fig2 = plt.figure()
before = f'{id(plt._pylab_helpers.Gcf)} {plt._pylab_helpers.Gcf.figs!r}'
get_backend()
after = f'{id(plt._pylab_helpers.Gcf)} {plt._pylab_helpers.Gcf.figs!r}'

assert before == after, '\n' + before + '\n' + after
```


### Actual outcome

```
---------------------------------------------------------------------------
AssertionError                            Traceback (most recent call last)
<ipython-input-1-fa4d099aa289> in <cell line: 11>()
      9 after = f'{id(plt._pylab_helpers.Gcf)} {plt._pylab_helpers.Gcf.figs!r}'
     10 
---> 11 assert before == after, '\n' + before + '\n' + after
     12 

AssertionError: 
94453354309744 OrderedDict([(1, <matplotlib.backends.backend_qt.FigureManagerQT object at 0x7fb33e26c220>)])
94453354309744 OrderedDict()
```

### Expected outcome

The figure should not be missing from `Gcf`.  Consequences of this are, e.g, `plt.close(fig2)` doesn't work because `Gcf.destroy_fig()` can't find it.

### Additional information

_No response_

### Operating system

Xubuntu

### Matplotlib Version

3.5.2

### Matplotlib Backend

QtAgg

### Python version

Python 3.10.4

### Jupyter version

n/a

### Installation

conda


## Hints

My knee-jerk guess is that  :  

 - the `rcParams['backend']` in the auto-sentinel
 - that is stashed by rc_context
 - if you do the first thing to force the backend to be resolved in the context manager it get changes
 - the context manager sets it back to the sentinel an the way out
 - `get_backend()` re-resolves the backend which because it changes the backend it closes all of the figures


This is probably been a long standing latent bug, but was brought to the front when we made the backend resolution lazier.

## Patch

```diff

diff --git a/lib/matplotlib/__init__.py b/lib/matplotlib/__init__.py
--- a/lib/matplotlib/__init__.py
+++ b/lib/matplotlib/__init__.py
@@ -1059,6 +1059,8 @@ def rc_context(rc=None, fname=None):
     """
     Return a context manager for temporarily changing rcParams.
 
+    The :rc:`backend` will not be reset by the context manager.
+
     Parameters
     ----------
     rc : dict
@@ -1087,7 +1089,8 @@ def rc_context(rc=None, fname=None):
              plt.plot(x, y)  # uses 'print.rc'
 
     """
-    orig = rcParams.copy()
+    orig = dict(rcParams.copy())
+    del orig['backend']
     try:
         if fname:
             rc_file(fname)


```

## Test Patch

```diff
diff --git a/lib/matplotlib/tests/test_rcparams.py b/lib/matplotlib/tests/test_rcparams.py
--- a/lib/matplotlib/tests/test_rcparams.py
+++ b/lib/matplotlib/tests/test_rcparams.py
@@ -496,6 +496,13 @@ def test_keymaps():
         assert isinstance(mpl.rcParams[k], list)
 
 
+def test_no_backend_reset_rccontext():
+    assert mpl.rcParams['backend'] != 'module://aardvark'
+    with mpl.rc_context():
+        mpl.rcParams['backend'] = 'module://aardvark'
+    assert mpl.rcParams['backend'] == 'module://aardvark'
+
+
 def test_rcparams_reset_after_fail():
     # There was previously a bug that meant that if rc_context failed and
     # raised an exception due to issues in the supplied rc parameters, the

```

## Test Information

**Tests that should FAIL→PASS**: ["lib/matplotlib/tests/test_rcparams.py::test_no_backend_reset_rccontext"]

**Tests that should PASS→PASS**: ["lib/matplotlib/tests/test_rcparams.py::test_rcparams", "lib/matplotlib/tests/test_rcparams.py::test_RcParams_class", "lib/matplotlib/tests/test_rcparams.py::test_Bug_2543", "lib/matplotlib/tests/test_rcparams.py::test_legend_colors[same", "lib/matplotlib/tests/test_rcparams.py::test_legend_colors[inherited", "lib/matplotlib/tests/test_rcparams.py::test_legend_colors[different", "lib/matplotlib/tests/test_rcparams.py::test_mfc_rcparams", "lib/matplotlib/tests/test_rcparams.py::test_mec_rcparams", "lib/matplotlib/tests/test_rcparams.py::test_axes_titlecolor_rcparams", "lib/matplotlib/tests/test_rcparams.py::test_Issue_1713", "lib/matplotlib/tests/test_rcparams.py::test_animation_frame_formats", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-t-True]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-y-True]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-yes-True]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-on-True]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-true-True]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-1-True0]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-1-True1]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-True-True]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-f-False]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-n-False]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-no-False]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-off-False]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-false-False]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-0-False0]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-0-False1]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_bool-False-False]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_strlist--target16]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_strlist-a,b-target17]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_strlist-aardvark-target18]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_strlist-aardvark,", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_strlist-arg21-target21]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_strlist-arg22-target22]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_strlist-arg23-target23]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_strlist-arg24-target24]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_intlist-1,", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_intlist-arg26-target26]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_intlist-arg27-target27]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_intlist-arg28-target28]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_intlist-arg29-target29]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_floatlist-1.5,", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_floatlist-arg31-target31]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_floatlist-arg32-target32]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_floatlist-arg33-target33]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_floatlist-arg34-target34]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_cycler-cycler(\"color\",", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_cycler-arg36-target36]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_cycler-(cycler(\"color\",", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_cycler-cycler(c='rgb',", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_cycler-cycler('c',", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_cycler-arg40-target40]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_cycler-arg41-target41]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_hatch---|---|]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_hatch-\\\\oO-\\\\oO]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_hatch-/+*/.x-/+*/.x]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_hatch--]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_colorlist-r,g,b-target46]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_colorlist-arg47-target47]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_colorlist-r,", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_colorlist-arg49-target49]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_colorlist-arg50-target50]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_colorlist-arg51-target51]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_color-None-none]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_color-none-none]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_color-AABBCC-#AABBCC]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_color-AABBCC00-#AABBCC00]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_color-tab:blue-tab:blue]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_color-C12-C12]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_color-(0,", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_color-arg59-target59]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_color-arg61-target61]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_color_or_linecolor-linecolor-linecolor]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_color_or_linecolor-markerfacecolor-markerfacecolor]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_color_or_linecolor-mfc-markerfacecolor]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_color_or_linecolor-markeredgecolor-markeredgecolor]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_color_or_linecolor-mec-markeredgecolor]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_hist_bins-auto-auto]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_hist_bins-fd-fd]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_hist_bins-10-10]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_hist_bins-1,", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_hist_bins-arg71-target71]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_hist_bins-arg72-target72]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_markevery-None-None]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_markevery-1-1]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_markevery-0.1-0.1]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_markevery-arg76-target76]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_markevery-arg77-target77]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_markevery-arg78-target78]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_markevery-arg79-target79]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[validate_markevery-arg80-target80]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle----]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle-solid-solid]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle------]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle-dashed-dashed]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle--.--.]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle-dashdot-dashdot]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle-:-:]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle-dotted-dotted]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle--]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle-", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle-None-none]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle-none-none]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle-DoTtEd-dotted]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle-1,", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle-arg95-target95]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle-arg96-target96]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle-arg97-target97]", "lib/matplotlib/tests/test_rcparams.py::test_validator_valid[_validate_linestyle-arg98-target98]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_bool-aardvark-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_bool-2-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_bool--1-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_bool-arg3-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_strlist-arg4-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_strlist-1-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_strlist-arg6-MatplotlibDeprecationWarning]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_strlist-arg7-MatplotlibDeprecationWarning]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_intlist-aardvark-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_intlist-arg9-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_intlist-arg10-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_floatlist-aardvark-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_floatlist-arg12-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_floatlist-arg13-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_floatlist-arg14-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_floatlist-None-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_cycler-4-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_cycler-cycler(\"bleh,", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_cycler-Cycler(\"linewidth\",", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_cycler-cycler('c',", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_cycler-1", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_cycler-os.system(\"echo", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_cycler-import", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_cycler-def", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_cycler-cycler(\"waka\",", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_cycler-cycler(c=[1,", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_cycler-cycler(lw=['a',", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_cycler-arg31-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_cycler-arg32-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_hatch---_-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_hatch-8-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_hatch-X-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_colorlist-fish-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_color-tab:veryblue-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_color-(0,", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[_validate_color_or_linecolor-line-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[_validate_color_or_linecolor-marker-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_hist_bins-aardvark-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-arg45-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-arg46-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-arg47-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-arg48-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-arg49-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-arg50-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-arg51-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-arg52-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-arg53-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-abc-TypeError0]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-arg55-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-arg56-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-arg57-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-arg58-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-abc-TypeError1]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-a-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[validate_markevery-arg61-TypeError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[_validate_linestyle-aardvark-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[_validate_linestyle-dotted-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[_validate_linestyle-\\xff\\xfed\\x00o\\x00t\\x00t\\x00e\\x00d\\x00-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[_validate_linestyle-arg65-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[_validate_linestyle-1.23-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[_validate_linestyle-arg67-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[_validate_linestyle-arg68-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[_validate_linestyle-arg69-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validator_invalid[_validate_linestyle-arg70-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontweight[bold-bold]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontweight[BOLD-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontweight[100-100_0]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontweight[100-100_1]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontweight[weight4-100]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontweight[20.6-20]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontweight[20.6-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontweight[weight7-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontstretch[expanded-expanded]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontstretch[EXPANDED-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontstretch[100-100_0]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontstretch[100-100_1]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontstretch[stretch4-100]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontstretch[20.6-20]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontstretch[20.6-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_validate_fontstretch[stretch7-ValueError]", "lib/matplotlib/tests/test_rcparams.py::test_keymaps", "lib/matplotlib/tests/test_rcparams.py::test_rcparams_reset_after_fail", "lib/matplotlib/tests/test_rcparams.py::test_backend_fallback_headless", "lib/matplotlib/tests/test_rcparams.py::test_deprecation"]

**Base Commit**: 3eadeacc06c9f2ddcdac6ae39819faa9fbee9e39
**Environment Setup Commit**: de98877e3dc45de8dd441d008f23d88738dc015d
