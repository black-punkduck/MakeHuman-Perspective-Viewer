#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman Perspective Viewer

**Product Home Page:** http://www.makehumancommunity.org/

**Code Home Page:**    https://github.com/black-punkduck/MakeHuman-Perspective-Viewer

**Authors:**           Jonas Hauquier, punkduck, Avanuvir

**Copyright(c):**      MakeHuman Team 2001-2019

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehumancommunity.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


Abstract
--------

Experimental plugin based on 3_library_animation.py, which allows to show bvh files
frame by frame and is able to switch between orthogonal and  perspective view.
"""

import mh
import math
import gui
import gui3d
import os
import qtgui
from core import G
from qtui import supportsSVG
from PyQt5 import QtGui

class PerspectiveTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Perspective')
        self.isOrthoView = True
        self.createShortCut()

        self.human = gui3d.app.selectedHuman
        self.currentframe = 0
        self.framesloaded = 0
        self.fov = self.fovangle_loaded = G.app.modelCamera.getFovAngle()

        projbox = self.addLeftWidget(gui.GroupBox('BVH Viewer'))

        self.avFramesText = projbox.addWidget(gui.TextView('Available frames: 0'))

        self.playbackSlider = projbox.addWidget(gui.Slider(label=['Current frame', ': %d']))
        self.playbackSlider.setMin(0)
        self.invMouseWheel = G.app.getSetting('invertMouseWheel')

        @self.playbackSlider.mhEvent
        def onChange(value):
            self.currentframe = int(value)
            self.updateFrame()
        
        self.nextframeButton = projbox.addWidget(gui.Button('Next frame'))

        @self.nextframeButton.mhEvent
        def onClicked(event):
            anim = self.human.getActiveAnimation()
            if anim:
                if self.currentframe >= anim.nFrames-1:
                    self.currentframe = 0
                else:
                    self.currentframe += 1

                self.updateFrame()
                self.playbackSlider.setValue(self.currentframe)

        self.prevframeButton = projbox.addWidget(gui.Button('Previous frame'))

        @self.prevframeButton.mhEvent
        def onClicked(event):
            anim = self.human.getActiveAnimation()
            if anim:
                if self.currentframe <= 0:
                    self.currentframe = anim.nFrames-1
                else:
                    self.currentframe -= 1

                self.updateFrame()
                self.playbackSlider.setValue(self.currentframe)

        projbox = self.addLeftWidget(gui.GroupBox('Projection'))

        self.projRadioButtonGroup = []

        self.persButton = projbox.addWidget(gui.RadioButton(self.projRadioButtonGroup, 'Perspective',selected=G.app.modelCamera.projection))

        @self.persButton.mhEvent
        def onClicked(event):
            self.toggleView()

        self.orthButton = projbox.addWidget(gui.RadioButton(self.projRadioButtonGroup, 'Orthogonal',selected=not G.app.modelCamera.projection))

        @self.orthButton.mhEvent
        def onClicked(event):
            self.toggleView()

        self.focalDistanceLbl = projbox.addWidget(gui.TextView('Focal distance= '))
        self.updateFocalDistance(self.fov)
        self.fovslider = projbox.addWidget(gui.Slider(label=['Focus angle', '= %.2f'], min=1.0, max=90.0, value=self.fov))

        @self.fovslider.mhEvent
        def onChange(value):
            for cam in G.cameras:
                cam.setFovAngle(value)
                cam.changed()
            self.updateFocalDistance(value)

        self.trans= G.cameras[0].getPosition()
        posbox = self.addLeftWidget(gui.GroupBox('Camera Translation'))

        self.xposslider = posbox.addWidget(gui.Slider(label=['X-translation', '= %.2f'], min=-1.0, max=1.0, value=self.trans[0]))

        @self.xposslider.mhEvent
        def onChange(value):
            for cam in G.cameras:
                self.trans[0] = value
                cam.setPosition (self.trans)
                cam.changed()
      
        self.yposslider = posbox.addWidget(gui.Slider(label=['Y-translation', '= %.2f'], min=-1.0, max=1.0, value=self.trans[1]))

        @self.yposslider.mhEvent
        def onChange(value):
            for cam in G.cameras:
                cam.translation[1] = value
                cam.setPosition (self.trans)
                cam.changed()

        self.resetButton = posbox.addWidget(gui.Button('Reset translation'))

        @self.resetButton.mhEvent
        def onClicked(event):
            for cam in G.cameras:
                cam.translation = [0.0, 0.0, 0.0]
                cam.pickedPos = cam.translation
                cam.changed()
            self.xposslider.setValue (0.0)
            self.yposslider.setValue (0.0)
            self.updateFrame()

        @self.mhEvent
        def onMouseWheel(event):
            if self.isOrthoView == True:
                G.app.onMouseWheel(event)
            else:
                zoomOut = event.wheelDelta > 0
                if self.invMouseWheel:
                    zoomOut = not zoomOut
                
                if zoomOut:
                    if self.fov <= 1:
                        return
                    self.fov -= 1
                else:
                    if self.fov >=90:
                        return
                    self.fov += 1
                for cam in G.cameras:
                    cam.setFovAngle(self.fov)
                    cam.changed()
                self.updateFocalDistance(self.fov)
                self.fovslider.setValue (self.fov)

        @self.mhEvent
        def onMouseDragged(event):
            G.app.onMouseDragged(event)
            self.updateCoords()

    def toggleView(self):
        if self.isOrthoView:
            self.fov = 25
            for cam in G.cameras:
                cam.setFovAngle(self.fov)
                cam.switchToPerspective()
            if G.app.backgroundGradient:
                G.app.removeObject(G.app.backgroundGradient)
                G.app.backgroundGradient = None
            self.persButton.setSelected(True)
            self.orthButton.setSelected(False)
            self.isOrthoView = False
        else:
            self.fov = self.fovangle_loaded
            for cam in G.cameras:
                cam.setFovAngle(self.fovangle_loaded)
                cam.switchToOrtho()
            if not G.app.backgroundGradient:
                G.app.loadBackgroundGradient()
            self.persButton.setSelected(False)
            self.orthButton.setSelected(True)
            self.isOrthoView = True
        self.fovslider.setValue (self.fov)
        self.updateFocalDistance (self.fov)
        self.updateCoords()
        self.action.setChecked(not self.isOrthoView)


    def updateFocalDistance(self, value):
        self.fov = value
        fd = 15 / (2 * math.tan(math.radians(value/2)))
        self.focalDistanceLbl.setTextFormat(["Focal distance","= %f"], fd)

    def updateFrame(self):
        self.human.setToFrame(self.currentframe)
        self.human.refreshPose()

    def updateCoords(self):
        self.trans= G.cameras[0].getPosition()
        self.xposslider.setValue (self.trans[0])
        self.yposslider.setValue (self.trans[1])

    def onShow(self, event):
        self.currentframe = 0
        gui3d.TaskView.onShow(self, event)
        if gui3d.app.getSetting('cameraAutoZoom'):
            gui3d.app.setGlobalCamera()

        self.playbackSlider.setEnabled(False)
        self.prevframeButton.setEnabled(False)
        self.nextframeButton.setEnabled(False)
        if self.human.getSkeleton():
            if self.human.getActiveAnimation():
                maxframes = self.human.getActiveAnimation().nFrames
                if  maxframes > 1:
                    self.avFramesText.setText('Available frames: ' + str(maxframes))
                    self.playbackSlider.setEnabled(True)
                    self.playbackSlider.setMax(maxframes -1)
                    self.prevframeButton.setEnabled(True)
                    self.nextframeButton.setEnabled(True)
                    self.playbackSlider.setValue(self.currentframe)
                    self.updateFrame()
                elif  maxframes == 1:
                    self.avFramesText.setText('Available frames: 1')
        self.persButton.setSelected(G.app.modelCamera.projection)
        self.orthButton.setSelected(not G.app.modelCamera.projection)

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

    def onHumanChanged(self, event):
        human = event.human
        if event.change == 'reset':
            if self.isShown():
                # Refresh onShow status
                self.onShow(event)

    def createShortCut(self):
        path = os.path.dirname(__file__)
        if supportsSVG:
            path = os.path.join(path, 'tglview.svg')
        else:
            path = os.path.join(path, 'tglview.png')

        self.action = gui.Action('tglview', "Toggle view mode", self.toggleView, toggle=True)
        self.action.setIcon(QtGui.QIcon(path))
        mh.setShortcut(mh.Modifiers.CTRL, mh.Keys.p, self.action)
        G.app.mainwin.addAction(self.action)
        toolbar = G.app.camera_toolbar
        toolbar.addAction(self.action)



