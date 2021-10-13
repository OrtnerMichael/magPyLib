""" plolty draw-functionalities"""

import plotly.graph_objects as go
import numpy as np
from scipy.spatial.transform import Rotation as RotScipy
from magpylib import _lib
from magpylib._lib.config import Config

# Defaults
SENSORSIZE = 1
DIPOLESIZEREF = 5
DISCRETESOURCE_OPACITY = 0.05
VIRTUALFIELD_OPACITY = 0.05

_UNIT_PREFIX = {
    -24: 'y',  # yocto
    -21: 'z',  # zepto
    -18: 'a',  # atto
    -15: 'f',  # femto
    -12: 'p',  # pico
     -9: 'n',  # nano
     -6: 'µ',  # micro
     -3: 'm',   # milli
      0: '',
      3: 'k',    # kilo
      6: 'M',    # mega
      9: 'G',    # giga
     12: 'T',   # tera
     15: 'P',   # peta
     18: 'E',   # exa
     21: 'Z',   # zetta
     24: 'Y',    # yotta
}

def unit_prefix(number, unit='', precision=3, char_between=''):
    from math import log10
    digits = int(log10(abs(number)))//3*3 if number!=0 else 0
    prefix = _UNIT_PREFIX.get(digits,'')
    if prefix!='':
        new_number_str = '{:.{}g}'.format(number/10**digits, precision)  
    else:
        new_number_str = '{:.{}g}'.format(number, precision)
    return f'{new_number_str}{char_between}{prefix}{unit}'

def _getIntensity(vertices, mag, pos):
    '''vertices: [x,y,z] array'''
    if not all(m==0 for m in mag):
        p = np.array(vertices)
        pos = np.array(pos)
        m = np.array(mag) /   np.linalg.norm(mag)
        a = ((p[0]-pos[0])*m[0] + (p[1]-pos[1])*m[1] + (p[2]-pos[2])*m[2])
        b = (p[0]-pos[0])**2 + (p[1]-pos[1])**2 + (p[2]-pos[2])**2
        return a /  np.sqrt(b)
    else:
        return vertices[0]*0

def _getColorscale(color_transition=0.1, north_color=None, south_color=None):
    if north_color is None:
        north_color = Config.NORTH_COLOR
    if south_color is None:
        south_color = Config.SOUTH_COLOR
    return [
        [0, south_color], 
        [0.5*(1-color_transition), south_color],
        [0.5*(1+color_transition), north_color], 
        [1, north_color]
    ]

def makeBaseCuboid(dim=(1.,1.,1.), pos=(0.,0.,0.)):
    return dict(
        i = np.array([7, 0, 0, 0, 4, 4, 2, 6, 4, 0, 3, 7]),
        j = np.array([3, 4, 1, 2, 5, 6, 5, 5, 0, 1, 2, 2]),
        k = np.array([0, 7, 2, 3, 6, 7, 1, 2, 5, 5, 7, 6]),
        x = np.array([-1, -1, 1, 1, -1, -1, 1, 1])*0.5*dim[0]+pos[0],
        y = np.array([-1, 1, 1, -1, -1, 1, 1, -1])*0.5*dim[1]+pos[1],
        z = np.array([-1, -1, -1, -1, 1, 1, 1, 1])*0.5*dim[2]+pos[2]
    )

def make_BasePrism(base_vertices=3, diameter=1, height=1, pos=(0.,0.,0.)):
    N=base_vertices
    t = np.linspace(0, 2*np.pi, N, endpoint=False)
    c1 = np.array([1*np.cos(t), 1*np.sin(t), t*0-1])*0.5
    c2 = np.array([1*np.cos(t), 1*np.sin(t), t*0+1])*0.5
    c3 = np.array([[0,0],[0,0],[-1,1]])*0.5
    c = np.concatenate([c1,c2,c3], axis=1)
    c = c.T*np.array([diameter, diameter, height]) + np.array(pos)
    i1 = np.arange(N)
    j1 = i1+1; j1[-1]=0
    k1 = i1+N
    
    i2 = i1+N
    j2 = j1+N; j2[-1]=N
    k2 = i1+1; k2[-1]=0

    i3 = i1
    j3 = j1
    k3 = i1*0+2*N

    i4 = i2
    j4 = j2
    k4 = k3+1

    #k2&j2 and k3&j3 inverted because of face orientation
    i = np.concatenate([i1,i2,i3,i4])
    j = np.concatenate([j1,k2,k3,j4]) 
    k = np.concatenate([k1,j2,j3,k4])

    x,y,z = c.T
    return dict(x=x, y=y, z=z, i=i, j=j, k=k)

def make_Ellipsoid(dim=(1.,1.,1.), pos=(0.,0.,0.), Nvert=40):
    phi = np.linspace(0, 2*np.pi, Nvert, endpoint=False)
    theta = np.linspace(-np.pi/2, np.pi/2, Nvert)
    phi, theta=np.meshgrid(phi, theta)

    x = np.cos(theta) * np.sin(phi)*dim[0]*0.5 + pos[0]
    y = np.cos(theta) * np.cos(phi)*dim[1]*0.5 + pos[1]
    z = np.sin(theta)*dim[2]*0.5 + pos[2]

    x,y,z = x.flatten(), y.flatten(), z.flatten()
    return dict(x=x, y=y ,z=z, alphahull=0)

def make_Cuboid(mag=(0.,0.,1000.),  dim=(1.,1.,1.), pos=(0.,0.,0.), orientation=None, color_transition=0., name=None, name_suffix=None, north_color=None, south_color=None, **kwargs):
    name = 'Cuboid' if name is None else name
    name_suffix = " ({}mx{}mx{}m)".format(*(unit_prefix(d/1000) for d in dim)) if name_suffix is None else f' ({name_suffix})'
    cuboid = makeBaseCuboid(dim=dim, pos=pos)
    vertices = np.array([cuboid[k] for k in ('x','y','z')])
    if color_transition>=0:
        cuboid['colorscale'] = _getColorscale(color_transition, north_color=north_color, south_color=south_color)
        cuboid['intensity'] = _getIntensity(vertices=vertices, mag=mag, pos=pos)
    x, y, z = orientation.apply(vertices.T).T
    cuboid.update(
        x=x, y=y, z=z, 
        showscale=False,
        name=f'''{name}{name_suffix}''', **kwargs
    )
    return go.Mesh3d(**cuboid)

def make_Cylinder(mag=(0.,0.,1000.),  base_vertices=50, diameter=1, height=1., pos=(0.,0.,0.), orientation=None, color_transition=0., name=None, name_suffix=None, north_color=None, south_color=None, **kwargs):
    name = 'Cylinder' if name is None else name
    name_suffix = " (d={}m, h={}m)".format(*(unit_prefix(d/1000) for d in (diameter, height)))  if name_suffix is None else f' ({name_suffix})'
    cylinder = make_BasePrism(base_vertices=base_vertices, diameter=diameter, height=height, pos=pos)
    vertices = np.array([cylinder[k] for k in ('x','y','z')])
    if color_transition>=0:
        cylinder['colorscale'] = _getColorscale(color_transition, north_color=north_color, south_color=south_color)
        cylinder['intensity'] = _getIntensity(vertices=vertices, mag=mag, pos=pos)
    x, y, z = orientation.apply(vertices.T).T
    cylinder.update(
        x=x, y=y, z=z, 
        showscale=False,
        name=f'''{name}{name_suffix}''', **kwargs
    )
    return go.Mesh3d(**cylinder)

def make_Sphere(mag=(0.,0.,1000.),  Nvert=50, diameter=1, height=1., pos=(0.,0.,0.), orientation=None, color_transition=0., name=None, name_suffix=None, north_color=None, south_color=None, **kwargs):
    name = 'Sphere' if name is None else name
    name_suffix = " (d={}m)".format(unit_prefix(diameter/1000)) if name_suffix is None else f' ({name_suffix})' 
    sphere = make_Ellipsoid(Nvert=Nvert, dim=[diameter]*3, pos=pos)
    vertices = np.array([sphere[k] for k in ('x','y','z')])
    if color_transition>=0:
        sphere['colorscale'] = _getColorscale(color_transition, north_color=north_color, south_color=south_color)
        sphere['intensity'] = _getIntensity(vertices=vertices, mag=mag, pos=pos)
    x, y, z = orientation.apply(vertices.T).T
    sphere.update(
        x=x, y=y, z=z, 
        showscale=False,
        name=f'''{name}{name_suffix}''', **kwargs
    )
    return go.Mesh3d(**sphere)

def getTrace(input_obj, sensorsources=None, color_transition=0., color=None, Nver=40, maxpos=None,
             showhoverdata=True, dipolesizeref=DIPOLESIZEREF, 
             opacity='default',
             sensorsize=SENSORSIZE, visible=None, **kwargs):
             
    Cuboid = _lib.obj_classes.Cuboid
    Cylinder = _lib.obj_classes.Cylinder
    Sphere = _lib.obj_classes.Sphere
    Sensor = _lib.obj_classes.Sensor
    Dipole = _lib.obj_classes.Dipole
    Circular = _lib.obj_classes.Circular
    Line = _lib.obj_classes.Line

    if opacity == 'default':
        opacity = 1
    kwargs['opacity'] = opacity

    if isinstance(input_obj, Cuboid):
        trace = make_Cuboid(mag=input_obj.magnetization, dim=input_obj.dimension, 
                pos=input_obj.position, orientation=input_obj.orientation,
                color_transition=color_transition,
                **kwargs)
    elif isinstance(input_obj, Cylinder):
        base_vertices = min(50, Config.ITER_CYLINDER) # no need to render more than 50 vertices
        trace = make_Cylinder(mag=input_obj.magnetization, base_vertices=base_vertices, diameter=input_obj.dimension[0], height=input_obj.dimension[0], 
                pos=input_obj.position, orientation=input_obj.orientation,
                color_transition=color_transition,
                **kwargs)
    elif isinstance(input_obj, Sphere):
        trace = make_Sphere(mag=input_obj.magnetization, diameter=input_obj.diameter, 
                pos=input_obj.position, orientation=input_obj.orientation,
                color_transition=color_transition,
                **kwargs)
    return trace


def display_plotly(*objs, fig=None, **kwargs):
    show_fig=False
    if fig is None:
        show_fig = True
        fig = go.Figure(layout_title_text = getattr(objs[0],'name',None) if len(objs)==1 else None)
    traces = [getTrace(obj, **kwargs) for obj in objs]
    with fig.batch_update():
        fig.add_traces(traces)
        fig.update_scenes(
            xaxis_title='x [mm]',
            yaxis_title='y [mm]',
            zaxis_title='z [mm]',
            aspectmode='data')
    if show_fig:
        fig.show()