(examples-force-haftkraft)=

# Magnetic Holding Force

The examples here require installaion of the [magpylib-force package](https://pypi.org/project/magpylib-force/). See also the [magpylib-force documentation](docs-magpylib-force).

With Magpylib-force it is possible to compute the holding force of a magnet attached magnetically to a soft-ferromagnetic plate. The "pull-force" is the opposing force that is required to detach the magnet from the surface.

```{figure} ../../../_static/images/examples_force_haftkraft.png
:width: 40%
:align: center
:alt: Sketch of holding force.

Sketch of holding force F that must be overcome to detach the magnet from a soft-magnetic plate.
```

For this we make use of the "magnetic mirror" effect, which is quite similar to the well-known electrostatic "mirror-charge" model. The magnetic field of a magnetic dipole moment that lies in front of a highly permeable surface is similar to the field of two dipole moments: the original one and one that is mirrored across the surface such that each "magnetic charge" that makes up the dipole moment is mirrored in both position and charge.

The following example computes the holding force of a Cuboid magnet using the magnetic mirror effect.

```{code-block} python
import magpylib as magpy
from magpylib_force import getFT

# Target magnet
m1 = magpy.magnet.Cuboid(
    dimension=(5e-3, 2.5e-3, 1e-3),
    polarization=(0, 0, 1.33),
)
m1.meshing = 100

# Mirror magnet
m2 = m1.copy(position=(0,0,1e-3))

F,T = getFT(m2, m1)
print(f"Holding Force: {round(F[2]*100)} g")
# Holding Force: 349 g
```

Magnet dimensions and material from this example are taken from the [web](https://www.supermagnete.at/quadermagnete-neodym/quadermagnet-5mm-2.5mm-1.5mm_Q-05-2.5-1.5-HN). The remanence of N45 material lies within 1.32 and 1.36 T which corresponds to the polarization, see also the ["Modeling a real magnet"](examples-tutorial-modeling-magnets) tutorial. The computation confirms what is stated on the web-page, that the holding force of this magnet is about 350 g.
