# matplotlib__matplotlib-25433

**Repository**: matplotlib/matplotlib
**Created**: 2023-03-11T08:36:32Z
**Version**: 3.7

## Problem Statement

[Bug]: using clf and pyplot.draw in range slider on_changed callback blocks input to widgets
### Bug summary

When using clear figure, adding new widgets and then redrawing the current figure in the on_changed callback of a range slider the inputs to all the widgets in the figure are blocked. When doing the same in the button callback on_clicked, everything works fine.

### Code for reproduction

```python
import matplotlib.pyplot as pyplot
import matplotlib.widgets as widgets

def onchanged(values):
    print("on changed")
    print(values)
    pyplot.clf()
    addElements()
    pyplot.draw()

def onclick(e):
    print("on click")
    pyplot.clf()
    addElements()
    pyplot.draw()

def addElements():
    ax = pyplot.axes([0.1, 0.45, 0.8, 0.1])
    global slider
    slider = widgets.RangeSlider(ax, "Test", valmin=1, valmax=10, valinit=(1, 10))
    slider.on_changed(onchanged)
    ax = pyplot.axes([0.1, 0.30, 0.8, 0.1])
    global button
    button = widgets.Button(ax, "Test")
    button.on_clicked(onclick)

addElements()

pyplot.show()
```


### Actual outcome

The widgets can't receive any input from a mouse click, when redrawing in the on_changed callback of a range Slider. 
When using a button, there is no problem.

### Expected outcome

The range slider callback on_changed behaves the same as the button callback on_clicked.

### Additional information

The problem also occurred on Manjaro with:
- Python version: 3.10.9
- Matplotlib version: 3.6.2
- Matplotlib backend: QtAgg
- Installation of matplotlib via Linux package manager


### Operating system

Windows 10

### Matplotlib Version

3.6.2

### Matplotlib Backend

TkAgg

### Python version

3.11.0

### Jupyter version

_No response_

### Installation

pip


## Hints

A can confirm this behavior, but removing and recreating the objects that host the callbacks in the callbacks is definitely on the edge of the intended usage.  

Why are you doing this?  In your application can you get away with not destroying your slider?
I think there could be a way to not destroy the slider. But I don't have the time to test that currently.
My workaround for the problem was using a button to redraw everything. With that everything is working fine.

That was the weird part for me as they are both callbacks, but in one everything works fine and in the other one all inputs are blocked. If what I'm trying doing is not the intended usage, that's fine for me. 
Thanks for the answer.
The idiomatic way to destructively work on widgets that triggered an event in a UI toolkit is to do the destructive work in an idle callback:
```python
def redraw():
    pyplot.clf()
    addElements()
    pyplot.draw()
    return False

def onchanged(values):
    print("on changed")
    print(values)
    pyplot.gcf().canvas.new_timer(redraw)
```
Thanks for the answer. I tried that with the code in the original post.
The line:

```python
pyplot.gcf().canvas.new_timer(redraw)
```
doesn't work for me. After having a look at the documentation, I think the line should be:

```python
pyplot.gcf().canvas.new_timer(callbacks=[(redraw, tuple(), dict())])
```

But that still didn't work. The redraw callback doesn't seem to trigger.
Sorry, I mean to update that after testing and before posting, but forgot to. That line should be:
```
    pyplot.gcf().canvas.new_timer(callbacks=[redraw])
```
Sorry for double posting; now I see that it didn't actually get called!

That's because I forgot to call `start` as well, and the timer was garbage collected at the end of the function. It should be called as you've said, but stored globally and started:
```
import matplotlib.pyplot as pyplot
import matplotlib.widgets as widgets


def redraw():
    print("redraw")
    pyplot.clf()
    addElements()
    pyplot.draw()
    return False


def onchanged(values):
    print("on changed")
    print(values)
    global timer
    timer = pyplot.gcf().canvas.new_timer(callbacks=[(redraw, (), {})])
    timer.start()


def onclick(e):
    print("on click")
    global timer
    timer = pyplot.gcf().canvas.new_timer(callbacks=[(redraw, (), {})])
    timer.start()


def addElements():
    ax = pyplot.axes([0.1, 0.45, 0.8, 0.1])
    global slider
    slider = widgets.RangeSlider(ax, "Test", valmin=1, valmax=10, valinit=(1, 10))
    slider.on_changed(onchanged)
    ax = pyplot.axes([0.1, 0.30, 0.8, 0.1])
    global button
    button = widgets.Button(ax, "Test")
    button.on_clicked(onclick)


addElements()

pyplot.show()
```
Thanks for the answer, the code works without errors, but I'm still able to break it when using the range slider. Then it results in the same problem as my original post. It seems like that happens when triggering the onchanged callback at the same time the timer callback gets called.
Are you sure it's not working, or is it just that it got replaced by a new one that is using the same initial value again? For me, it moves, but once the callback runs, it's reset because the slider is created with `valinit=(1, 10)`.
The code redraws everything fine, but when the onchanged callback of the range slider gets called at the same time as the redraw callback of the timer, I'm not able to give any new inputs to the widgets. You can maybe reproduce that with changing the value of the slider the whole time, while waiting for the redraw.
I think what is happening is that because you are destroying the slider every time the you are also destroying the state of what value you changed it to.  When you create it you re-create it at the default value which produces the effect that you can not seem to change it.  Put another way, the state of what the current value of the slider is is in the `Slider` object.   Replacing the slider object with a new one (correctly) forgets the old value.

-----

I agree it fails in surprising ways, but I think that this is best case "undefined behavior" and worst case incorrect usage of the tools.  In either case there is not much we can do upstream to address this (as if the user _did_ want to get fresh sliders that is not a case we should prevent from happening or warn on).
The "forgetting the value" is not the problem. My problem is, that the input just blocks for every widget in the figure. When that happens, you can click on any widget, but no callback gets triggered. That problem seems to happen when a callback of an object gets called that is/has been destroyed, but I don't know for sure.

But if that is from the incorrect usage of the tools, that's fine for me. I got a decent workaround that works currently, so I just have to keep that in my code for now.

## Patch

```diff

diff --git a/lib/matplotlib/figure.py b/lib/matplotlib/figure.py
--- a/lib/matplotlib/figure.py
+++ b/lib/matplotlib/figure.py
@@ -931,6 +931,7 @@ def _break_share_link(ax, grouper):
         self._axobservers.process("_axes_change_event", self)
         self.stale = True
         self._localaxes.remove(ax)
+        self.canvas.release_mouse(ax)
 
         # Break link between any shared axes
         for name in ax._axis_names:


```

## Test Patch

```diff
diff --git a/lib/matplotlib/tests/test_backend_bases.py b/lib/matplotlib/tests/test_backend_bases.py
--- a/lib/matplotlib/tests/test_backend_bases.py
+++ b/lib/matplotlib/tests/test_backend_bases.py
@@ -95,6 +95,16 @@ def test_non_gui_warning(monkeypatch):
                 in str(rec[0].message))
 
 
+def test_grab_clear():
+    fig, ax = plt.subplots()
+
+    fig.canvas.grab_mouse(ax)
+    assert fig.canvas.mouse_grabber == ax
+
+    fig.clear()
+    assert fig.canvas.mouse_grabber is None
+
+
 @pytest.mark.parametrize(
     "x, y", [(42, 24), (None, 42), (None, None), (200, 100.01), (205.75, 2.0)])
 def test_location_event_position(x, y):

```

## Test Information

**Tests that should FAIL→PASS**: ["lib/matplotlib/tests/test_backend_bases.py::test_grab_clear"]

**Tests that should PASS→PASS**: ["lib/matplotlib/tests/test_backend_bases.py::test_uses_per_path", "lib/matplotlib/tests/test_backend_bases.py::test_canvas_ctor", "lib/matplotlib/tests/test_backend_bases.py::test_get_default_filename", "lib/matplotlib/tests/test_backend_bases.py::test_canvas_change", "lib/matplotlib/tests/test_backend_bases.py::test_non_gui_warning", "lib/matplotlib/tests/test_backend_bases.py::test_location_event_position[42-24]", "lib/matplotlib/tests/test_backend_bases.py::test_location_event_position[None-42]", "lib/matplotlib/tests/test_backend_bases.py::test_location_event_position[None-None]", "lib/matplotlib/tests/test_backend_bases.py::test_location_event_position[200-100.01]", "lib/matplotlib/tests/test_backend_bases.py::test_location_event_position[205.75-2.0]", "lib/matplotlib/tests/test_backend_bases.py::test_pick", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_zoom", "lib/matplotlib/tests/test_backend_bases.py::test_widgetlock_zoompan", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[zoom-1-expected0-vertical-imshow]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[zoom-1-expected0-vertical-contourf]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[zoom-1-expected0-horizontal-imshow]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[zoom-1-expected0-horizontal-contourf]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[zoom-3-expected1-vertical-imshow]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[zoom-3-expected1-vertical-contourf]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[zoom-3-expected1-horizontal-imshow]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[zoom-3-expected1-horizontal-contourf]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[pan-1-expected2-vertical-imshow]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[pan-1-expected2-vertical-contourf]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[pan-1-expected2-horizontal-imshow]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[pan-1-expected2-horizontal-contourf]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[pan-3-expected3-vertical-imshow]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[pan-3-expected3-vertical-contourf]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[pan-3-expected3-horizontal-imshow]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_colorbar[pan-3-expected3-horizontal-contourf]", "lib/matplotlib/tests/test_backend_bases.py::test_toolbar_zoompan", "lib/matplotlib/tests/test_backend_bases.py::test_draw[svg]", "lib/matplotlib/tests/test_backend_bases.py::test_draw[ps]", "lib/matplotlib/tests/test_backend_bases.py::test_draw[pdf]", "lib/matplotlib/tests/test_backend_bases.py::test_draw[pgf]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[None-mouseend0-expectedxlim0-expectedylim0]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[None-mouseend1-expectedxlim1-expectedylim1]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[None-mouseend2-expectedxlim2-expectedylim2]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[None-mouseend3-expectedxlim3-expectedylim3]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[None-mouseend4-expectedxlim4-expectedylim4]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[None-mouseend5-expectedxlim5-expectedylim5]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[None-mouseend6-expectedxlim6-expectedylim6]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[None-mouseend7-expectedxlim7-expectedylim7]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[shift-mouseend8-expectedxlim8-expectedylim8]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[shift-mouseend9-expectedxlim9-expectedylim9]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[shift-mouseend10-expectedxlim10-expectedylim10]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[shift-mouseend11-expectedxlim11-expectedylim11]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[shift-mouseend12-expectedxlim12-expectedylim12]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[shift-mouseend13-expectedxlim13-expectedylim13]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[x-mouseend14-expectedxlim14-expectedylim14]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[y-mouseend15-expectedxlim15-expectedylim15]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[control-mouseend16-expectedxlim16-expectedylim16]", "lib/matplotlib/tests/test_backend_bases.py::test_interactive_pan[control-mouseend17-expectedxlim17-expectedylim17]", "lib/matplotlib/tests/test_backend_bases.py::test_toolmanager_remove", "lib/matplotlib/tests/test_backend_bases.py::test_toolmanager_get_tool", "lib/matplotlib/tests/test_backend_bases.py::test_toolmanager_update_keymap"]

**Base Commit**: 7eafdd8af3c523c1c77b027d378fb337dd489f18
**Environment Setup Commit**: 0849036fd992a2dd133a0cffc3f84f58ccf1840f
