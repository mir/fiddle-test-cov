# pyvista__pyvista-4315

**Repository**: pyvista/pyvista
**Created**: 2023-04-21T13:47:31Z
**Version**: 0.39

## Problem Statement

Rectilinear grid does not allow Sequences as inputs
### Describe the bug, what's wrong, and what you expected.

Rectilinear grid gives an error when `Sequence`s are passed in, but `ndarray` are ok.

### Steps to reproduce the bug.

This doesn't work
```python
import pyvista as pv
pv.RectilinearGrid([0, 1], [0, 1], [0, 1])
```

This works
```py
import pyvista as pv
import numpy as np
pv.RectilinearGrid(np.ndarray([0, 1]), np.ndarray([0, 1]), np.ndarray([0, 1]))
```
### System Information

```shell
--------------------------------------------------------------------------------
  Date: Wed Apr 19 20:15:10 2023 UTC

                OS : Linux
            CPU(s) : 2
           Machine : x86_64
      Architecture : 64bit
       Environment : IPython
        GPU Vendor : Mesa/X.org
      GPU Renderer : llvmpipe (LLVM 11.0.1, 256 bits)
       GPU Version : 4.5 (Core Profile) Mesa 20.3.5

  Python 3.11.2 (main, Mar 23 2023, 17:12:29) [GCC 10.2.1 20210110]

           pyvista : 0.38.5
               vtk : 9.2.6
             numpy : 1.24.2
           imageio : 2.27.0
            scooby : 0.7.1
             pooch : v1.7.0
        matplotlib : 3.7.1
           IPython : 8.12.0
--------------------------------------------------------------------------------
```


### Screenshots

_No response_


## Patch

```diff

diff --git a/pyvista/core/grid.py b/pyvista/core/grid.py
--- a/pyvista/core/grid.py
+++ b/pyvista/core/grid.py
@@ -135,23 +135,30 @@ def __init__(self, *args, check_duplicates=False, deep=False, **kwargs):
                     self.shallow_copy(args[0])
             elif isinstance(args[0], (str, pathlib.Path)):
                 self._from_file(args[0], **kwargs)
-            elif isinstance(args[0], np.ndarray):
-                self._from_arrays(args[0], None, None, check_duplicates)
+            elif isinstance(args[0], (np.ndarray, Sequence)):
+                self._from_arrays(np.asanyarray(args[0]), None, None, check_duplicates)
             else:
                 raise TypeError(f'Type ({type(args[0])}) not understood by `RectilinearGrid`')
 
         elif len(args) == 3 or len(args) == 2:
-            arg0_is_arr = isinstance(args[0], np.ndarray)
-            arg1_is_arr = isinstance(args[1], np.ndarray)
+            arg0_is_arr = isinstance(args[0], (np.ndarray, Sequence))
+            arg1_is_arr = isinstance(args[1], (np.ndarray, Sequence))
             if len(args) == 3:
-                arg2_is_arr = isinstance(args[2], np.ndarray)
+                arg2_is_arr = isinstance(args[2], (np.ndarray, Sequence))
             else:
                 arg2_is_arr = False
 
             if all([arg0_is_arr, arg1_is_arr, arg2_is_arr]):
-                self._from_arrays(args[0], args[1], args[2], check_duplicates)
+                self._from_arrays(
+                    np.asanyarray(args[0]),
+                    np.asanyarray(args[1]),
+                    np.asanyarray(args[2]),
+                    check_duplicates,
+                )
             elif all([arg0_is_arr, arg1_is_arr]):
-                self._from_arrays(args[0], args[1], None, check_duplicates)
+                self._from_arrays(
+                    np.asanyarray(args[0]), np.asanyarray(args[1]), None, check_duplicates
+                )
             else:
                 raise TypeError("Arguments not understood by `RectilinearGrid`.")
 


```

## Test Patch

```diff
diff --git a/tests/test_grid.py b/tests/test_grid.py
--- a/tests/test_grid.py
+++ b/tests/test_grid.py
@@ -735,6 +735,21 @@ def test_create_rectilinear_grid_from_specs():
     assert grid.n_cells == 9 * 3 * 19
     assert grid.n_points == 10 * 4 * 20
     assert grid.bounds == (-10.0, 8.0, -10.0, 5.0, -10.0, 9.0)
+
+    # with Sequence
+    xrng = [0, 1]
+    yrng = [0, 1, 2]
+    zrng = [0, 1, 2, 3]
+    grid = pyvista.RectilinearGrid(xrng)
+    assert grid.n_cells == 1
+    assert grid.n_points == 2
+    grid = pyvista.RectilinearGrid(xrng, yrng)
+    assert grid.n_cells == 2
+    assert grid.n_points == 6
+    grid = pyvista.RectilinearGrid(xrng, yrng, zrng)
+    assert grid.n_cells == 6
+    assert grid.n_points == 24
+
     # 2D example
     cell_spacings = np.array([1.0, 1.0, 2.0, 2.0, 5.0, 10.0])
     x_coordinates = np.cumsum(cell_spacings)

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/test_grid.py::test_create_rectilinear_grid_from_specs"]

**Tests that should PASS→PASS**: ["tests/test_grid.py::test_volume", "tests/test_grid.py::test_init_from_polydata", "tests/test_grid.py::test_init_from_structured", "tests/test_grid.py::test_init_from_unstructured", "tests/test_grid.py::test_init_from_numpy_arrays", "tests/test_grid.py::test_init_bad_input", "tests/test_grid.py::test_init_from_arrays[False]", "tests/test_grid.py::test_init_from_arrays[True]", "tests/test_grid.py::test_init_from_dict[False-False]", "tests/test_grid.py::test_init_from_dict[False-True]", "tests/test_grid.py::test_init_from_dict[True-False]", "tests/test_grid.py::test_init_from_dict[True-True]", "tests/test_grid.py::test_init_polyhedron", "tests/test_grid.py::test_cells_dict_hexbeam_file", "tests/test_grid.py::test_cells_dict_variable_length", "tests/test_grid.py::test_cells_dict_empty_grid", "tests/test_grid.py::test_cells_dict_alternating_cells", "tests/test_grid.py::test_destructor", "tests/test_grid.py::test_surface_indices", "tests/test_grid.py::test_extract_feature_edges", "tests/test_grid.py::test_triangulate_inplace", "tests/test_grid.py::test_save[.vtu-True]", "tests/test_grid.py::test_save[.vtu-False]", "tests/test_grid.py::test_save[.vtk-True]", "tests/test_grid.py::test_save[.vtk-False]", "tests/test_grid.py::test_pathlib_read_write", "tests/test_grid.py::test_init_bad_filename", "tests/test_grid.py::test_save_bad_extension", "tests/test_grid.py::test_linear_copy", "tests/test_grid.py::test_linear_copy_surf_elem", "tests/test_grid.py::test_extract_cells[True]", "tests/test_grid.py::test_extract_cells[False]", "tests/test_grid.py::test_merge", "tests/test_grid.py::test_merge_not_main", "tests/test_grid.py::test_merge_list", "tests/test_grid.py::test_merge_invalid", "tests/test_grid.py::test_init_structured_raise", "tests/test_grid.py::test_init_structured", "tests/test_grid.py::test_no_copy_polydata_init", "tests/test_grid.py::test_no_copy_polydata_points_setter", "tests/test_grid.py::test_no_copy_structured_mesh_init", "tests/test_grid.py::test_no_copy_structured_mesh_points_setter", "tests/test_grid.py::test_no_copy_pointset_init", "tests/test_grid.py::test_no_copy_pointset_points_setter", "tests/test_grid.py::test_no_copy_unstructured_grid_points_setter", "tests/test_grid.py::test_no_copy_rectilinear_grid", "tests/test_grid.py::test_grid_repr", "tests/test_grid.py::test_slice_structured", "tests/test_grid.py::test_invalid_init_structured", "tests/test_grid.py::test_save_structured[.vtk-True]", "tests/test_grid.py::test_save_structured[.vtk-False]", "tests/test_grid.py::test_save_structured[.vts-True]", "tests/test_grid.py::test_save_structured[.vts-False]", "tests/test_grid.py::test_load_structured_bad_filename", "tests/test_grid.py::test_instantiate_by_filename", "tests/test_grid.py::test_create_rectilinear_after_init", "tests/test_grid.py::test_create_rectilinear_grid_from_file", "tests/test_grid.py::test_read_rectilinear_grid_from_file", "tests/test_grid.py::test_read_rectilinear_grid_from_pathlib", "tests/test_grid.py::test_raise_rectilinear_grid_non_unique", "tests/test_grid.py::test_cast_rectilinear_grid", "tests/test_grid.py::test_create_uniform_grid_from_specs", "tests/test_grid.py::test_uniform_grid_invald_args", "tests/test_grid.py::test_uniform_setters", "tests/test_grid.py::test_create_uniform_grid_from_file", "tests/test_grid.py::test_read_uniform_grid_from_file", "tests/test_grid.py::test_read_uniform_grid_from_pathlib", "tests/test_grid.py::test_cast_uniform_to_structured", "tests/test_grid.py::test_cast_uniform_to_rectilinear", "tests/test_grid.py::test_uniform_grid_to_tetrahedra", "tests/test_grid.py::test_fft_and_rfft", "tests/test_grid.py::test_fft_low_pass", "tests/test_grid.py::test_fft_high_pass", "tests/test_grid.py::test_save_rectilinear[.vtk-True]", "tests/test_grid.py::test_save_rectilinear[.vtk-False]", "tests/test_grid.py::test_save_rectilinear[.vtr-True]", "tests/test_grid.py::test_save_rectilinear[.vtr-False]", "tests/test_grid.py::test_save_uniform[.vtk-True]", "tests/test_grid.py::test_save_uniform[.vtk-False]", "tests/test_grid.py::test_save_uniform[.vti-True]", "tests/test_grid.py::test_save_uniform[.vti-False]", "tests/test_grid.py::test_grid_points", "tests/test_grid.py::test_grid_extract_selection_points", "tests/test_grid.py::test_gaussian_smooth", "tests/test_grid.py::test_remove_cells[ind0]", "tests/test_grid.py::test_remove_cells[ind1]", "tests/test_grid.py::test_remove_cells[ind2]", "tests/test_grid.py::test_remove_cells_not_inplace[ind0]", "tests/test_grid.py::test_remove_cells_not_inplace[ind1]", "tests/test_grid.py::test_remove_cells_not_inplace[ind2]", "tests/test_grid.py::test_remove_cells_invalid", "tests/test_grid.py::test_hide_cells[ind0]", "tests/test_grid.py::test_hide_cells[ind1]", "tests/test_grid.py::test_hide_cells[ind2]", "tests/test_grid.py::test_hide_points[ind0]", "tests/test_grid.py::test_hide_points[ind1]", "tests/test_grid.py::test_hide_points[ind2]", "tests/test_grid.py::test_set_extent", "tests/test_grid.py::test_UnstructuredGrid_cast_to_explicit_structured_grid", "tests/test_grid.py::test_ExplicitStructuredGrid_init", "tests/test_grid.py::test_ExplicitStructuredGrid_cast_to_unstructured_grid", "tests/test_grid.py::test_ExplicitStructuredGrid_save", "tests/test_grid.py::test_ExplicitStructuredGrid_hide_cells", "tests/test_grid.py::test_ExplicitStructuredGrid_show_cells", "tests/test_grid.py::test_ExplicitStructuredGrid_dimensions", "tests/test_grid.py::test_ExplicitStructuredGrid_visible_bounds", "tests/test_grid.py::test_ExplicitStructuredGrid_cell_id", "tests/test_grid.py::test_ExplicitStructuredGrid_cell_coords", "tests/test_grid.py::test_ExplicitStructuredGrid_neighbors", "tests/test_grid.py::test_ExplicitStructuredGrid_compute_connectivity", "tests/test_grid.py::test_ExplicitStructuredGrid_compute_connections", "tests/test_grid.py::test_ExplicitStructuredGrid_raise_init", "tests/test_grid.py::test_copy_no_copy_wrap_object", "tests/test_grid.py::test_copy_no_copy_wrap_object_vtk9"]

**Base Commit**: db6ee8dd4a747b8864caae36c5d05883976a3ae5
**Environment Setup Commit**: 4c2d1aed10b1600d520271beba8579c71433e808
