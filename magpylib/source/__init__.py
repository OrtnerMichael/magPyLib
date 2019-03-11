"""
Source Classes
==============
   
Available source types for generating magnetic fields, 
compatible with :class:`~magpylib.Collection`

.. currentmodule:: magpylib.source.magnet


Quicklist for :mod:`~magpylib.source.magnet` sources:

.. autosummary::

   Box
   Sphere
   Cylinder

.. currentmodule:: magpylib.source.current

Quicklist for :mod:`~magpylib.source.current` sources:

.. autosummary::

   Line
   Circular

.. currentmodule:: magpylib.source.moment

Quicklist for :mod:`~magpylib.source.moment` sources:

.. autosummary::

   Dipole

"""
__all__ = ["magnet","current","moment"] # This is for Sphinx


import magpylib.source.magnet as magnet
import magpylib.source.current as current
import magpylib.source.moment as moment
