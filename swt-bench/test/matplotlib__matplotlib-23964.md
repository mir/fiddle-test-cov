# matplotlib__matplotlib-23964

**Repository**: matplotlib/matplotlib
**Created**: 2022-09-20T13:49:19Z
**Version**: 3.6

## Problem Statement

[Bug]: Text label with empty line causes a "TypeError: cannot unpack non-iterable NoneType object" in PostScript backend
### Bug summary

When saving a figure with the PostScript backend, a
> TypeError: cannot unpack non-iterable NoneType object

happens if the figure contains a multi-line text label with an empty line (see example).

### Code for reproduction

```python
from matplotlib.figure import Figure

figure = Figure()
ax = figure.add_subplot(111)
# ax.set_title('\nLower title')  # this would cause an error as well
ax.annotate(text='\nLower label', xy=(0, 0))
figure.savefig('figure.eps')
```


### Actual outcome

$ ./venv/Scripts/python save_ps.py
Traceback (most recent call last):
  File "C:\temp\matplotlib_save_ps\save_ps.py", line 7, in <module>
    figure.savefig('figure.eps')
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\figure.py", line 3272, in savefig
    self.canvas.print_figure(fname, **kwargs)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\backend_bases.py", line 2338, in print_figure
    result = print_method(
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\backend_bases.py", line 2204, in <lambda>
    print_method = functools.wraps(meth)(lambda *args, **kwargs: meth(
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\_api\deprecation.py", line 410, in wrapper
    return func(*inner_args, **inner_kwargs)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\backends\backend_ps.py", line 869, in _print_ps
    printer(fmt, outfile, dpi=dpi, dsc_comments=dsc_comments,
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\backends\backend_ps.py", line 927, in _print_figure
    self.figure.draw(renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\artist.py", line 74, in draw_wrapper
    result = draw(artist, renderer, *args, **kwargs)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\artist.py", line 51, in draw_wrapper
    return draw(artist, renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\figure.py", line 3069, in draw
    mimage._draw_list_compositing_images(
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\image.py", line 131, in _draw_list_compositing_images
    a.draw(renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\artist.py", line 51, in draw_wrapper
    return draw(artist, renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\axes\_base.py", line 3106, in draw
    mimage._draw_list_compositing_images(
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\image.py", line 131, in _draw_list_compositing_images
    a.draw(renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\artist.py", line 51, in draw_wrapper
    return draw(artist, renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\text.py", line 1995, in draw
    Text.draw(self, renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\artist.py", line 51, in draw_wrapper
    return draw(artist, renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\text.py", line 736, in draw
    textrenderer.draw_text(gc, x, y, clean_line,
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\backends\backend_ps.py", line 248, in wrapper
    return meth(self, *args, **kwargs)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\backends\backend_ps.py", line 673, in draw_text
    for ps_name, xs_names in stream:
TypeError: cannot unpack non-iterable NoneType object


### Expected outcome

The figure can be saved as `figure.eps` without error.

### Additional information

- seems to happen if a text label or title contains a linebreak with an empty line
- works without error for other backends such as PNG, PDF, SVG, Qt
- works with matplotlib<=3.5.3
- adding `if curr_stream:` before line 669 of `backend_ps.py` seems to fix the bug 

### Operating system

Windows

### Matplotlib Version

3.6.0

### Matplotlib Backend

_No response_

### Python version

3.9.13

### Jupyter version

_No response_

### Installation

pip


## Patch

```diff

diff --git a/lib/matplotlib/backends/backend_ps.py b/lib/matplotlib/backends/backend_ps.py
--- a/lib/matplotlib/backends/backend_ps.py
+++ b/lib/matplotlib/backends/backend_ps.py
@@ -665,8 +665,9 @@ def draw_text(self, gc, x, y, s, prop, angle, ismath=False, mtext=None):
                 curr_stream[1].append(
                     (item.x, item.ft_object.get_glyph_name(item.glyph_idx))
                 )
-            # append the last entry
-            stream.append(curr_stream)
+            # append the last entry if exists
+            if curr_stream:
+                stream.append(curr_stream)
 
         self.set_color(*gc.get_rgb())
 


```

## Test Patch

```diff
diff --git a/lib/matplotlib/tests/test_backend_ps.py b/lib/matplotlib/tests/test_backend_ps.py
--- a/lib/matplotlib/tests/test_backend_ps.py
+++ b/lib/matplotlib/tests/test_backend_ps.py
@@ -256,6 +256,15 @@ def test_linedash():
     assert buf.tell() > 0
 
 
+def test_empty_line():
+    # Smoke-test for gh#23954
+    figure = Figure()
+    figure.text(0.5, 0.5, "\nfoo\n\n")
+    buf = io.BytesIO()
+    figure.savefig(buf, format='eps')
+    figure.savefig(buf, format='ps')
+
+
 def test_no_duplicate_definition():
 
     fig = Figure()

```

## Test Information

**Tests that should FAIL→PASS**: ["lib/matplotlib/tests/test_backend_ps.py::test_empty_line"]

**Tests that should PASS→PASS**: ["lib/matplotlib/tests/test_backend_ps.py::test_savefig_to_stringio[ps-portrait]", "lib/matplotlib/tests/test_backend_ps.py::test_savefig_to_stringio[ps-landscape]", "lib/matplotlib/tests/test_backend_ps.py::test_savefig_to_stringio[ps", "lib/matplotlib/tests/test_backend_ps.py::test_savefig_to_stringio[eps-portrait]", "lib/matplotlib/tests/test_backend_ps.py::test_savefig_to_stringio[eps-landscape]", "lib/matplotlib/tests/test_backend_ps.py::test_savefig_to_stringio[eps", "lib/matplotlib/tests/test_backend_ps.py::test_patheffects", "lib/matplotlib/tests/test_backend_ps.py::test_transparency[eps]", "lib/matplotlib/tests/test_backend_ps.py::test_bbox", "lib/matplotlib/tests/test_backend_ps.py::test_failing_latex", "lib/matplotlib/tests/test_backend_ps.py::test_text_clip[eps]", "lib/matplotlib/tests/test_backend_ps.py::test_d_glyph", "lib/matplotlib/tests/test_backend_ps.py::test_fonttype[3]", "lib/matplotlib/tests/test_backend_ps.py::test_fonttype[42]", "lib/matplotlib/tests/test_backend_ps.py::test_linedash", "lib/matplotlib/tests/test_backend_ps.py::test_no_duplicate_definition"]

**Base Commit**: 269c0b94b4fcf8b1135011c1556eac29dc09de15
**Environment Setup Commit**: 73909bcb408886a22e2b84581d6b9e6d9907c813
