#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman Perspective Viewer

**Product Home Page:** http://www.makehumancommunity.org

**Code Home Page:**    https://github.com/black-punkduck/MakeHuman-Perspective-Viewer

**Authors:**           punkduck

**Copyright(c):**      MakeHuman Team 2001-2019

**Licensing:**         APGL3

Abstract
--------

Experimental plugin based on 3_library_animation.py, which allows to show bvh files
frame by frame and is able to switch between orthogonal and  perspective view.
"""
from .perspective import PerspectiveTaskView

category = None

def load(app):
    category = app.getCategory('Community')
    taskview = category.addTask(PerspectiveTaskView(category))

def unload(app):
    pass

