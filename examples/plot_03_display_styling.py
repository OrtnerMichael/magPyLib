"""
=================
Display styling
=================
"""

# %%
# Displaying objects may not yield by default the visual representation the user wants. For these
# cases, the library includes a variety of styling options that can be applied at multiple levels
# in the user's code.

# %%
# Hierarchy of arguments
# ----------------------
# from **lowest** to **highest** precedence
#
# - library ``defaults``
# - individual object ``style`` or at ``Collection`` level
# - in the ``display`` function

# %%
# Examples
# --------

#%%
import magpylib as magpy
import plotly.graph_objects as go

from magpylib._src.style import Dipole

magpy.defaults.reset()

cuboid = magpy.magnet.Cuboid(
    magnetization=(1, 0, 0), dimension=(1, 1, 1), position=(0, 0, 0)
)
cylinder = magpy.magnet.Cylinder(
    magnetization=(0, 1, 0), dimension=(1, 1), position=(2, 0, 0)
)
sphere = magpy.magnet.Sphere(magnetization=(0, 1, 1), diameter=1, position=(4, 0, 0))
col = magpy.Collection(cuboid, cylinder, sphere)

#%%
# **Setting library defaults**:
#
# Display styles can be set at the library default level at ``magpy.defaults.display.style``. The
# default styles are separated into the following object families:
#
# - **base** : common properties for all families
# - **magnet**: ``Cuboid, Cylinder, Sphere, CylinderSegment``
# - **current**: ``Line, Loop``
# - **sensor**: ``Sensor``
# - **markers**: ``display`` markers
#
# Nested properties can be set with directly by accessing style attributes with the dot notation, or
# by assigning a dictionary with equivalent keys.

# %%
# with
magnet_style = magpy.defaults.display.style.magnet

# %%
# the following examples are equivalent
magnet_style.magnetization.show = True
magnet_style.magnetization.color.middle = "grey"
magnet_style.magnetization.color.mode = "tricolor"

# %%
magnet_style = {"show": True, "color": {"middle": "grey", "mode": "tricolor"}}

# %%
# To make it easier to work with nested properties, style constructors and object style method
# support magic underscore notation. This allows you to reference nested properties by joining
# together multiple nested property names with underscores.This feature mainly helps reduce the code
# verbosity and is heavily inspired by the ``plotly`` implementation
# (see https://plotly.com/python/creating-and-updating-figures/#magic-underscore-notation). The
# previous examples can also be written as:
magnet_style = {"show": True, "color_middle": "grey", "color_mode": "tricolor"}

# %%
# Additionally, instead of overriding the whole style constructor, style properties can be updated.
# The underscore notation is also supported here:
magnet_style.update(show=True, color_middle="grey", color_mode="tricolor")

# %%
# a practical example:
my_default_magnetization_style = {
    "show": True,
    "color": {
        "transition": 1,
        "mode": "tricolor",
        "middle": "white",
        "north": "magenta",
        "south": "turquoise",
    },
}
magpy.defaults.display.style.magnet.magnetization = my_default_magnetization_style

fig = go.Figure()
magpy.display(col, canvas=fig, backend="plotly")
fig

#%%
# **Setting style via** ``Collection``:
#
# .. note::
#   The ``Collection`` object does not hold any ``style`` attribute on its own but the helper method
#   ``set_styles`` allows setting the styles of all its children where the set arguments match
#   existing child style attributes.

col.set_styles(magnetization_color_south="blue")

fig = go.Figure()
magpy.display(col, canvas=fig, backend="plotly")
fig

#%%
# **Setting individual styles**:
cylinder.style.update(magnetization_color_mode="bicolor")
cuboid.style.magnetization.color = dict(mode="tricycle")

fig = go.Figure()
magpy.display(col, canvas=fig, backend="plotly")
fig

#%%
# **Overriding style at display time**:
#
# .. note::
#   Setting style parameters in the ``display`` function does not change the default styles nor the
#   set object style. It only affects the current representation to be displayed.
#
# The provided styling properties as function arguments will override temporarily the styles set by
# any of the aforementioned methods. All styling properties need to start with ``style`` and
# underscore magic is supported. The object family must be omitted since the style properties set at
# display time will apply accross object families. Only matching properties to a specific object
# will be applied.

fig = go.Figure()
magpy.display(col, canvas=fig, backend="plotly", style_magnetization_show=False)
fig

# %%
# In the following example, both ``sensor`` and ``dipole`` have a ``size`` object level style
# property.
import magpylib as magpy
import plotly.graph_objects as go

magpy.defaults.reset()

cuboid = magpy.magnet.Cuboid(
    magnetization=(1, 0, 0), dimension=(1, 1, 1), position=(0, 0, 0)
)
sensor = magpy.Sensor(position=((-2, 0, 0)), style=dict(size=1))
sensor2 = magpy.Sensor(position=((2, 0, 0)), style=dict(size=10))
dipole = magpy.misc.Dipole(moment=(1, 1, 1), position=(0, 0, 2), style=dict(size=2))

magpy.display(cuboid, dipole, sensor, sensor2, zoom=1)

# %%
# The size property can be overridden at display time with ``style_size=5``
magpy.display(cuboid, dipole, sensor, sensor2, style_size=1, zoom=1)

# %%
# List of available styles
# ------------------------
style = magpy.defaults.display.style.as_dict(flatten=True)
print("\n".join(f"{k!r}: {v!r}" for k, v in style.items()))

# %%
# .. warning::
#   Even if both ``matplotlib`` and ``plotly`` backends can display all object of the library, there
#   is no 100% feature parity between them. Some of the differences include (non-exhaustive list):
#
#   - ``magnetization.size`` -> ``matplotlib`` only
#   - ``magnetization.color`` -> ``plotly`` only
