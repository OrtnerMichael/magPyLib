(examples-tutorial-modeling-magnets)=

# Modeling a real magnet

Whenever you wish to compare Magpylib simulations with experimental data obtained using a real permanent magnet, you might wonder how to properly set up a Magpylib magnet object to reflect the physical permanent magnet in question. The goal of this tutorial is to explain how to extract this information from respective datasheets, to provide better understanding of permanent magnets, and show how to align Magpylib simulations with experimental measurements.

This tutorial was supported by [BOMATEC](https://www.bomatec.com/de) by providing excellent data sheets and by supplying magnets for the experimental demonstration below.

## Short summary

In a magnet data sheet, you should find B-H curves and J-H curves. These curves coincide at H=0, which gives the intrinsic material remanence $B_r$. As a result of material response and self-interaction, the magnet "demagnetizes" itself so that the mean magnetic polarization of a real magnet is always below the remanence. How much below depends strongly on the shape of the magnet and is expressed in the data sheet through the permeance coefficient lines (grey lines). The numbers at the end indicate the typical magnet length to diameter ratio (L/D).

To obtain the correct magnetic polarization of a magnet from the data sheet, one must find the crossing between B-H curve and respective permeance coefficient line. This gives the "working point" which corresponds to the mean demagnetizing H-field inside the magnet. The correct polarization to use in the Magpylib simulation is the J-value at the working point which can be read off from the J-H curve.

![data sheet snippet](../../../_static/images/examples_tutorial_magnet_datasheet2.png)

The following sections provide further explanation on the matter.

## Hysteresis loop

If you've worked with magnetism, chances are very high that you have seen a magnetic hysteresis loop. Hysteresis loops describe the connection between the **mean values** of an externally applied H-field and the resulting B-field, polarization J or magnetization M **within a defined volume**. This connection depends strongly on the size and shape of this volume and what is inside and what is outside.

The B-H curve is called the "normal loop", while J-H and M-H curves are called "intrinsic loops". Hereon we only make use of the J-H loops, but the discussion is similar for M-H. Normal and intrinsic loops are connected via $B = \mu_0 H + J$. In free space the B-H connection is just a straight line defined via $B = \mu_0 H$. When the whole space is filled with magnetic material you will see something like this within an arbitrary volume:

::::{grid} 2
:::{grid-item}
:columns: 3
:::
:::{grid-item}
:columns: 6
![hysteresis loops](../../../_static/images/examples_tutorial_magnet_hysteresis.png)
:::
::::

**1st quadrant**: Initially we have $J=0$ and $H=0$. The magnetic material is not magnetized, and no external H-field is applied. When increasing the H-field, the material polarization will follow the "virgin curve" and will increase until it reaches its maximum possible value, the saturation polarization $J_S$. Higher values of $H$ will not affect $J$, while $B$ will keep increasing linearly. Now we are on the "major loop" - we will never return to the virgin curve. After reaching a large H-value we slowly turn the H-field off. As it drops to zero the material will retain its strong polarization at saturation level while the resulting $B$ decreases. At $H = 0$ the B-field then approaches the "remanence field" $B_r$, and its only contribution is $J_S$.

**2nd quadrant**: Now the H-field becomes negative. Its amplitude increases but it is oriented opposite to the initial direction. Therefore, it is also opposite to the magnetic polarization. In the 2nd quadrant we are now trying to actively demagnetize the material. This part of the hysteresis loop is often referred to as the "demagnetization curve". With increasing negative H, the B-field continues to become smaller until it reaches zero at the "coercive field" $H_c$. At this point the net B-field inside the volume is zero, however, the material is still magnetized! In the example loop above, the polarization at $H_c$ is still at the $J_S$ level. By increasing the H-field further, a point will be reached where the material will start to demagnetize. This can be seen by the non-linear drop of $J$. The point where $J$ reaches zero is called the "intrinsic coercive field" $H_{ci}$. At this point the net polarization in the observed volume is zero. The material is demagnetized. The intrinsic coercive field is a measure of how well a magnetized material can resist a demagnetizing field. Having large values of $H_{ci}$ is a property of "hard magnets", as they can keep their magnetization $J$ even for strong external fields in the opposite direction.

**3rd and 4th quadrants**: Moving to the third quadrant the behavior is now mirrored. As $H$ increases past $H_{ci}$, polarization quickly aligns with the external field and the material becomes saturated $J=-J_S$. By turning the field around again, we move through the fourth quadrant to complete the hysteresis loop.

Hysteresis in magnetism as presented here is a macroscopic model that is the result of a complex interplay between dipole and exchange interaction, material texture and resulting domain formation at a microscopic level. Details can be found, for example, in Aharoni's classical textbook "Introduction to the Theory of Ferromagnetism".

## The demagnetizing field

If in an application the applied external H-field is zero, it seems intuitive to use the remanence $B_r$ for the magnetic polarization in the Magpylib simulation. It is a value that you will find in the data sheet.

![data sheet snippet](../../../_static/images/examples_tutorial_magnet_table.png)

However, if considering $J=B_r$, you will quickly see that the experimental results are up to ~30 % below of what you would expect. The reason for this is the self-induced demagnetizing field of the magnet which is generated by the magnetic polarization itself. Just like $J$ generates an H-field on the outside of the magnet, it also generates an H-field inside the magnet, along the opposite direction of the polarization. The H-field outside the magnet is known as the stray field, and the H-field inside the magnet is called the demagnetizing field (as it opposes the magnetic polarization). This is demonstrated by the following figure:

![demagnetization field simulation](../../../_static/images/examples_tutorial_magnet_fieldcomparison.png)

Making use of the [streamplot example](examples-vis-mpl-streamplot), on the left side we show the cross-section of a Cuboid magnet and its homogeneous polarization. And on the right, we see the H-field generated by it. Inside the magnet the generated H-field opposes the polarization. As a result, the polarization of a magnet will not be $B_r$, but instead will be some value of $J$ in the 2nd quadrant of the J-H loop that corresponds to the mean H-field inside the magnet. This H-value is often referred to as the "working point".

## Finding the correct polarization

As explained above, the hysteresis loop depends strongly on the chosen observation volume geometry, the material inside, and what is outside of the volume. Magnet manufacturers provide such loops (usually only the 2nd quadrant) for their magnets, meaning that the observation volume is the whole magnet with air outside.

To obtain the correct mean polarization of a magnet we simply must compute the mean demagnetizing field (= working point) and read the resulting $J$ off the provided J-H loop. Computing the mean demagnetizing field, however, is not a simple task. In addition to the material response (permeability), it depends strongly on the magnet geometry. Fortunately, the working points can be read off from well written data sheets.

![data sheet snippet](../../../_static/images/examples_tutorial_magnet_datasheet.png)

This datasheet snippet shows the second quadrant of the B-H and J-H loops, even for two different temperatures. The working point is given by the intersection between the "permeance coefficient" lines (gray) and the B-H curve. The number at the end of these lines indicate the length to diameter ratio (L/D) of the magnet, which is the critical geometric factor. Different lines are for different L/D values, which allows one to select the correct working point for different magnets made from this specific material. Once the working point is found, the correct magnetic polarization, here denoted by $J_W$ (the magnetic polarization at the working point), can be read off. The following figure exemplifies the changes in $J_W$ for different L/D values, considering a cylinder magnet:

![finding the working point](../../../_static/images/examples_tutorial_magnet_LDratio.png)

Permanent magnets with different geometries, such as a parallelepiped shape, will have different behavior in terms of L/D values. Make sure you are reading the data from the correct part number.
## Warning

Keep in mind that there are still many reasons why your simulation might not fit well to your experiment. Here are some of the most common problems:

1. Small position errors of less than 100 um can have a large impact on the measurement result. The reference should be the sensitive element inside a sensor package. These elements can be displaced by 10-100 um and even rotated by a few degrees. The sensor might also not be well calibrated.
2. There are external stray fields, like the earth magnetic field, that influence the measurements. Those might also come from other nearby electronic equipment or magnetic parts.
3. Off-the-shelf magnets often do not hold what is promised in the datasheet
    - Magnetic polarization amplitude can be off by 5-10 %.
    - The direction of polarization often varies by up to a few degrees.
    - Worst-case: the polarization can be inhomogeneous which is often a problem in injection-mold magnets.

## Example

::::{grid} 2
:::{grid-item}
:columns: 3
:::
:::{grid-item}
:columns: 6
![](../../../_static/images/examples_icon_WIP.png)
:::
::::

coming soon:
1. Magpylib simulation code
2. Experimental data
3. Comparison and discussion

**Exterior reference**
G. Martinek, S. Ruoho and U. Wyss. (2021). *Magnetic Properties of Permanents Magnets & Measuring Techniques* [White paper]. Arnold Magnetic Technologies. https://www.arnoldmagnetics.com/blog/measuring-permanent-magnets-white-paper/