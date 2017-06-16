#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 14:08:23 2017

@author: steven
"""
import numpy as npy
from scipy.linalg import norm
import volmdlr.geometry as geometry
import math

import matplotlib.pyplot as plt
#import matplotlib.patches as patches
#from matplotlib.collections import PatchCollection

#from volmdlr.primitives2D import Line2D,Arc2D,Point2D
import volmdlr
import volmdlr.geometry as geometry
        
class Cylinder(volmdlr.Primitive3D):
    def __init__(self,position,axis,radius,width,name=''):
        volmdlr.Primitive3D.__init__(self,name)
        self.position=position
        self.axis=npy.array(axis)/norm(axis)
        self.radius=radius
        self.width=width
        
    def FreeCADExport(self,ip):
        name='primitive'+str(ip)
        e=str(1000*self.width)
        r=str(1000*self.radius)
        position=1000*(self.position-self.axis*self.width/2)
        x,y,z=position
        x=str(x)
        y=str(y)
        z=str(z)

        ax,ay,az=self.axis
        ax=str(ax)
        ay=str(ay)
        az=str(az)
        return name+'=Part.makeCylinder('+r+','+e+',fc.Vector('+x+','+y+','+z+'),fc.Vector('+ax+','+ay+','+az+'),360)'
  
    
    def Babylon(self):
        s='var cylinder = BABYLON.Mesh.CreateCylinder("{}", {}, {}, {}, 20, 3, scene,false, BABYLON.Mesh.DEFAULTSIDE);'.format(self.name,self.width,2*self.radius,2*self.radius)
        s+='cylinder.position = new BABYLON.Vector3({},{},{});'.format(*self.position)
        return s
    
class HollowCylinder(volmdlr.Primitive3D):
    def __init__(self,position,axis,inner_radius,outer_radius,width,name=''):
        volmdlr.Primitive3D.__init__(self,name)
        self.position=position
        self.axis=npy.array(axis)/norm(axis)
        self.inner_radius=inner_radius
        self.outer_radius=outer_radius
        self.width=width

    def FreeCADExport(self,ip):
        name='primitive'+str(ip)
        re=str(1000*self.outer_radius)
        ri=str(1000*self.inner_radius)        
        position=self.position-self.axis*self.width/2
        x,y,z=1000*position
        ax,ay,az=self.axis
        x=str(x)
        y=str(y)
        z=str(z)
        ax=str(ax)
        ay=str(ay)
        az=str(az)
#        return 'Part.makeCylinder('+r+','+e+',fc.Vector('+x+','+y+','+z+'),fc.Vector('+ox+','+oy+','+oz+'),360)'

        s='C2= Part.makeCircle('+re+',fc.Vector('+x+','+y+','+z+'),fc.Vector('+ax+','+ay+','+az+'))\n'
        s+='W2=Part.Wire(C2.Edges)\n'
        s+='F2=Part.Face(W2)\n'
        
        if self.inner_radius!=0.:
            s+='C1= Part.makeCircle('+ri+',fc.Vector('+x+','+y+','+z+'),fc.Vector('+ax+','+ay+','+az+'))\n'        
            s+='W1=Part.Wire(C1.Edges)\n'
            s+='F1=Part.Face(W1)\n'        
            s+='F2=F2.cut(F1)\n'        

        vx,vy,vz=self.axis*self.width*1000
        vx=str(vx)
        vy=str(vy)
        vz=str(vz)
        
        s+=name+'=F2.extrude(fc.Vector('+vx+','+vy+','+vz+'))\n'
        return s
    
    def Babylon(self):
        x,y,z=self.axis
        theta=math.acos(z/self.width)
        phi=math.atan(y/x)
        s='var cylinder = BABYLON.Mesh.CreateCylinder("{}", {}, {}, {}, 20, 3, scene,false, BABYLON.Mesh.DEFAULTSIDE);'.format(self.name,self.width,2*self.outer_radius,2*self.outer_radius)
        s+='cylinder.position = new BABYLON.Vector3({},{},{});\n;'.format(*self.position)
        s+='cylinder.rotation.x={}\n;'.format(theta)
        s+='cylinder.rotation.z={}\n;'.format(phi)
        return s
    
class ExtrudedProfile(volmdlr.Primitive3D):
    """

    """
    def __init__(self,plane_origin,x,y,contours2D,extrusion_vector,screw_thread=0.,name=''):
        volmdlr.Primitive3D.__init__(self,name)
        self.contours2D=contours2D
        self.extrusion_vector=extrusion_vector
        self.contours3D=[]
        self.screw_thread=screw_thread
        for contour in contours2D:
#            print(contour)
            self.contours3D.append(contour.To3D(plane_origin,x,y))
        
    def MPLPlot(self,ax):
        for contour in self.contours3D:
            for primitive in contour:
                primitive.MPLPlot(ax)
        
    def FreeCADExport(self,ip):
        name='primitive'+str(ip)
        s='W=[]\n'
        for ic,contour in enumerate(self.contours3D): 
            s+='L=[]\n'
            for ip,primitive in enumerate(contour):
                s+=primitive.FreeCADExport('L{}_{}'.format(ic,ip))
                s+='L.append(L{}_{})\n'.format(ic,ip)
            s+='S = Part.Shape(L)\n' 
            s+='W.append(Part.Wire(S.Edges))\n'
        s+='F=Part.Face(W)\n'
        e1,e2,e3=self.extrusion_vector
        e1=e1*1000
        e2=e2*1000
        e3=e3*1000
        if self.screw_thread==0:     
#            s+=name+'=S'
            s+=name+'=F.extrude(fc.Vector({},{},{}))\n'.format(e1,e2,e3)
        else:
            # Helix creation
            side=self.screw_thread/abs(self.screw_thread)
            thread=abs(self.screw_thread)
            
            s+='h=Part.MakeLongHelix()'
            e1,e2,e3=geometry.Direction2Euler(self.extrusion_vector)
            l=norm(self.extrusion_vector)
            s+='Sweep = Part.Wire(traj).makePipeShell([section],makeSolid,isFrenet)'
#            myObject.Shape = Sweep
        return s


class Sphere(volmdlr.Primitive3D):
    def __init__(self,center,radius,name=''):
        volmdlr.Primitive3D.__init__(self,name)
        self.center=center
        self.radius=radius
    
    def FreeCADExport(self,ip):
        name='primitive'+str(ip)
        r=1000*self.radius
        x,y,z=1000*self.center.vector
#        print(r,x,y,z)
        return '{}=Part.makeSphere({},fc.Vector({},{},{}))'.format(name,r,x,y,z)


class RevolvedProfile(volmdlr.Primitive3D):
    """
    
    """
    def __init__(self,plane_origin,x,y,contours2D,axis_point,axis,angle,name=''):
        volmdlr.Primitive3D.__init__(self,name)
        self.contours2D=contours2D
        self.axis_point=axis_point
        self.axis=axis
        self.angle=angle
        self.contours3D=[]
        for contour in contours2D:
#            print(contour)
            self.contours3D.append(contour.To3D(plane_origin,x,y))
        
    def MPLPlot(self,ax):
        for contour in self.contours3D:
            for primitive in contour:
                primitive.MPLPlot(ax)
        
    def FreeCADExport(self,ip):
        name='primitive'+str(ip)
        s='W=[]\n'
        for ic,contour in enumerate(self.contours3D): 
            s+='L=[]\n'
            for ip,primitive in enumerate(contour):
                s+=primitive.FreeCADExport('L{}_{}'.format(ic,ip))
                s+='L.append(L{}_{})\n'.format(ic,ip)
            s+='S = Part.Shape(L)\n' 
            s+='W.append(Part.Wire(S.Edges))\n'
        s+='F=Part.Face(W)\n'
        a1,a2,a3=self.axis.vector
        ap1,ap2,ap3=self.axis_point.vector
        ap1=ap1*1000
        ap2=ap2*1000
        ap3=ap3*1000
        angle=self.angle/math.pi*180
        s+='{}=F.revolve(fc.Vector({},{},{}),fc.Vector({},{},{}),{})\n'.format(name,ap1,ap2,ap3,a1,a2,a3,angle)

#            myObject.Shape = Sweep
        return s