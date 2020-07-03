#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 12:02:00 2020

@author: steven
"""


import volmdlr as vm

primitives = vm.Step('iso4162M16x55.step').to_shells3d('screw')
screw = vm.VolumeModel(primitives, name='screw')
screw.babylonjs()