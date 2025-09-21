# sympy__sympy-20049

**Repository**: sympy/sympy
**Created**: 2020-09-05T09:37:44Z
**Version**: 1.7

## Problem Statement

Point.vel() should calculate the velocity if possible
If you specify the orientation of two reference frames and then ask for the angular velocity between the two reference frames the angular velocity will be calculated. But if you try to do the same thing with velocities, this doesn't work. See below:

```
In [1]: import sympy as sm                                                                               

In [2]: import sympy.physics.mechanics as me                                                             

In [3]: A = me.ReferenceFrame('A')                                                                       

In [5]: q = me.dynamicsymbols('q')                                                                       

In [6]: B = A.orientnew('B', 'Axis', (q, A.x))                                                           

In [7]: B.ang_vel_in(A)                                                                                  
Out[7]: q'*A.x

In [9]: P = me.Point('P')                                                                                

In [10]: Q = me.Point('Q')                                                                               

In [11]: r = q*A.x + 2*q*A.y                                                                             

In [12]: Q.set_pos(P, r)                                                                                 

In [13]: Q.vel(A)                                                                                        
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
<ipython-input-13-0fc8041904cc> in <module>
----> 1 Q.vel(A)

~/miniconda3/lib/python3.6/site-packages/sympy/physics/vector/point.py in vel(self, frame)
    453         if not (frame in self._vel_dict):
    454             raise ValueError('Velocity of point ' + self.name + ' has not been'
--> 455                              ' defined in ReferenceFrame ' + frame.name)
    456         return self._vel_dict[frame]
    457 

ValueError: Velocity of point Q has not been defined in ReferenceFrame A
```

The expected result of the `Q.vel(A)` should be:

```
In [14]: r.dt(A)                                                                                         
Out[14]: q'*A.x + 2*q'*A.y
```

I think that this is possible. Maybe there is a reason it isn't implemented. But we should try to implement it because it is confusing why this works for orientations and not positions.




## Hints

Hi @moorepants, I think I could fix this. It would be implemented as a part of `ReferenceFrame` in `sympy/physics/vector/frame.py`, right?
No, it is part of Point. There are some nuances here and likely not a trivial PR to tackle. I'd recommend some simpler ones first if you are new to sympy and dynamics.
Sure, understood. Thank you @moorepants .
> No, it is part of Point. There are some nuances here and likely not a trivial PR to tackle. I'd recommend some simpler ones first if you are new to sympy and dynamics.

I would like to work on this issue.

The current Point.vel() returns velocity already defined in a reference frame , it doesn't calculate velocity between two points , so it would require a new function to calculate velocity between two points this would make it fully automatic.

So I propose , a change in vel() function to set  velocity of particle from r and a new function to which calculates and returns velocity by calculating displacement vector , this function wouldn't set the velocity of particle but would return it on being called.
The idea is that if there is sufficient information about the relative position of points, that Point.vel() can determine there is sufficient information and calculate the velocity. You should study how ReferenceFrame does this with ang_vel().
> The idea is that if there is sufficient information about the relative position of points, that Point.vel() can determine there is sufficient information and calculate the velocity. You should study how ReferenceFrame does this with ang_vel().

Okay on it!!

## Patch

```diff

diff --git a/sympy/physics/vector/point.py b/sympy/physics/vector/point.py
--- a/sympy/physics/vector/point.py
+++ b/sympy/physics/vector/point.py
@@ -483,19 +483,49 @@ def vel(self, frame):
         Examples
         ========
 
-        >>> from sympy.physics.vector import Point, ReferenceFrame
+        >>> from sympy.physics.vector import Point, ReferenceFrame, dynamicsymbols
         >>> N = ReferenceFrame('N')
         >>> p1 = Point('p1')
         >>> p1.set_vel(N, 10 * N.x)
         >>> p1.vel(N)
         10*N.x
 
+        Velocities will be automatically calculated if possible, otherwise a ``ValueError`` will be returned. If it is possible to calculate multiple different velocities from the relative points, the points defined most directly relative to this point will be used. In the case of inconsistent relative positions of points, incorrect velocities may be returned. It is up to the user to define prior relative positions and velocities of points in a self-consistent way.
+
+        >>> p = Point('p')
+        >>> q = dynamicsymbols('q')
+        >>> p.set_vel(N, 10 * N.x)
+        >>> p2 = Point('p2')
+        >>> p2.set_pos(p, q*N.x)
+        >>> p2.vel(N)
+        (Derivative(q(t), t) + 10)*N.x
+
         """
 
         _check_frame(frame)
         if not (frame in self._vel_dict):
-            raise ValueError('Velocity of point ' + self.name + ' has not been'
+            visited = []
+            queue = [self]
+            while queue: #BFS to find nearest point
+                node = queue.pop(0)
+                if node not in visited:
+                    visited.append(node)
+                    for neighbor, neighbor_pos in node._pos_dict.items():
+                        try:
+                            neighbor_pos.express(frame) #Checks if pos vector is valid
+                        except ValueError:
+                            continue
+                        try :
+                            neighbor_velocity = neighbor._vel_dict[frame] #Checks if point has its vel defined in req frame
+                        except KeyError:
+                            queue.append(neighbor)
+                            continue
+                        self.set_vel(frame, self.pos_from(neighbor).dt(frame) + neighbor_velocity)
+                        return self._vel_dict[frame]
+            else:
+                raise ValueError('Velocity of point ' + self.name + ' has not been'
                              ' defined in ReferenceFrame ' + frame.name)
+
         return self._vel_dict[frame]
 
     def partial_velocity(self, frame, *gen_speeds):


```

## Test Patch

```diff
diff --git a/sympy/physics/vector/tests/test_point.py b/sympy/physics/vector/tests/test_point.py
--- a/sympy/physics/vector/tests/test_point.py
+++ b/sympy/physics/vector/tests/test_point.py
@@ -126,3 +126,107 @@ def test_point_partial_velocity():
     assert p.partial_velocity(N, u1) == A.x
     assert p.partial_velocity(N, u1, u2) == (A.x, N.y)
     raises(ValueError, lambda: p.partial_velocity(A, u1))
+
+def test_point_vel(): #Basic functionality
+    q1, q2 = dynamicsymbols('q1 q2')
+    N = ReferenceFrame('N')
+    B = ReferenceFrame('B')
+    Q = Point('Q')
+    O = Point('O')
+    Q.set_pos(O, q1 * N.x)
+    raises(ValueError , lambda: Q.vel(N)) # Velocity of O in N is not defined
+    O.set_vel(N, q2 * N.y)
+    assert O.vel(N) == q2 * N.y
+    raises(ValueError , lambda : O.vel(B)) #Velocity of O is not defined in B
+
+def test_auto_point_vel():
+    t = dynamicsymbols._t
+    q1, q2 = dynamicsymbols('q1 q2')
+    N = ReferenceFrame('N')
+    B = ReferenceFrame('B')
+    O = Point('O')
+    Q = Point('Q')
+    Q.set_pos(O, q1 * N.x)
+    O.set_vel(N, q2 * N.y)
+    assert Q.vel(N) == q1.diff(t) * N.x + q2 * N.y  # Velocity of Q using O
+    P1 = Point('P1')
+    P1.set_pos(O, q1 * B.x)
+    P2 = Point('P2')
+    P2.set_pos(P1, q2 * B.z)
+    raises(ValueError, lambda : P2.vel(B)) # O's velocity is defined in different frame, and no
+    #point in between has its velocity defined
+    raises(ValueError, lambda: P2.vel(N)) # Velocity of O not defined in N
+
+def test_auto_point_vel_multiple_point_path():
+    t = dynamicsymbols._t
+    q1, q2 = dynamicsymbols('q1 q2')
+    B = ReferenceFrame('B')
+    P = Point('P')
+    P.set_vel(B, q1 * B.x)
+    P1 = Point('P1')
+    P1.set_pos(P, q2 * B.y)
+    P1.set_vel(B, q1 * B.z)
+    P2 = Point('P2')
+    P2.set_pos(P1, q1 * B.z)
+    P3 = Point('P3')
+    P3.set_pos(P2, 10 * q1 * B.y)
+    assert P3.vel(B) == 10 * q1.diff(t) * B.y + (q1 + q1.diff(t)) * B.z
+
+def test_auto_vel_dont_overwrite():
+    t = dynamicsymbols._t
+    q1, q2, u1 = dynamicsymbols('q1, q2, u1')
+    N = ReferenceFrame('N')
+    P = Point('P1')
+    P.set_vel(N, u1 * N.x)
+    P1 = Point('P1')
+    P1.set_pos(P, q2 * N.y)
+    assert P1.vel(N) == q2.diff(t) * N.y + u1 * N.x
+    assert P.vel(N) == u1 * N.x
+    P1.set_vel(N, u1 * N.z)
+    assert P1.vel(N) == u1 * N.z
+
+def test_auto_point_vel_if_tree_has_vel_but_inappropriate_pos_vector():
+    q1, q2 = dynamicsymbols('q1 q2')
+    B = ReferenceFrame('B')
+    S = ReferenceFrame('S')
+    P = Point('P')
+    P.set_vel(B, q1 * B.x)
+    P1 = Point('P1')
+    P1.set_pos(P, S.y)
+    raises(ValueError, lambda : P1.vel(B)) # P1.pos_from(P) can't be expressed in B
+    raises(ValueError, lambda : P1.vel(S)) # P.vel(S) not defined
+
+def test_auto_point_vel_shortest_path():
+    t = dynamicsymbols._t
+    q1, q2, u1, u2 = dynamicsymbols('q1 q2 u1 u2')
+    B = ReferenceFrame('B')
+    P = Point('P')
+    P.set_vel(B, u1 * B.x)
+    P1 = Point('P1')
+    P1.set_pos(P, q2 * B.y)
+    P1.set_vel(B, q1 * B.z)
+    P2 = Point('P2')
+    P2.set_pos(P1, q1 * B.z)
+    P3 = Point('P3')
+    P3.set_pos(P2, 10 * q1 * B.y)
+    P4 = Point('P4')
+    P4.set_pos(P3, q1 * B.x)
+    O = Point('O')
+    O.set_vel(B, u2 * B.y)
+    O1 = Point('O1')
+    O1.set_pos(O, q2 * B.z)
+    P4.set_pos(O1, q1 * B.x + q2 * B.z)
+    assert P4.vel(B) == q1.diff(t) * B.x + u2 * B.y + 2 * q2.diff(t) * B.z
+
+def test_auto_point_vel_connected_frames():
+    t = dynamicsymbols._t
+    q, q1, q2, u = dynamicsymbols('q q1 q2 u')
+    N = ReferenceFrame('N')
+    B = ReferenceFrame('B')
+    O = Point('O')
+    O.set_vel(N, u * N.x)
+    P = Point('P')
+    P.set_pos(O, q1 * N.x + q2 * B.y)
+    raises(ValueError, lambda: P.vel(N))
+    N.orient(B, 'Axis', (q, B.x))
+    assert P.vel(N) == (u + q1.diff(t)) * N.x + q2.diff(t) * B.y - q2 * q.diff(t) * B.z

```

## Test Information

**Tests that should FAIL→PASS**: ["test_auto_point_vel", "test_auto_point_vel_multiple_point_path", "test_auto_vel_dont_overwrite", "test_auto_point_vel_shortest_path"]

**Tests that should PASS→PASS**: ["test_point_v1pt_theorys", "test_point_a1pt_theorys", "test_point_v2pt_theorys", "test_point_a2pt_theorys", "test_point_funcs", "test_point_pos", "test_point_partial_velocity", "test_point_vel", "test_auto_point_vel_if_tree_has_vel_but_inappropriate_pos_vector"]

**Base Commit**: d57aaf064041fe52c0fa357639b069100f8b28e1
**Environment Setup Commit**: cffd4e0f86fefd4802349a9f9b19ed70934ea354
