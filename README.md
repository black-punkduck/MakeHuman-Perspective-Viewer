# MakeHuman-Perspective-Viewer
A user plugin to allow perspective view in MakeHuman Version 1.2

Navigation can be done in perspective view

* using the mouse-wheel for focus angle
* using mouse drag (push middle mouse button on character and move mouse) to change camera transition

In orthogonal mode the normal movement will be done.

x and y coordinates of camera and focus angle are displayed.


# BVH Viewer

Simply load a BVH file with more than one frime. Then you can move the different poses by either using the slider or the buttons.


# Compatibility

If you want to use this code in MakeHuman 1.1 change:

`#!/usr/bin/env python3`

to

`#!/usr/bin/python2.7`

in 

`__init__.py` and `perspective.py`


also change:

`from PyQt5 import QtGui`

in perspective.py to

`from PyQt4 import QtGui`

