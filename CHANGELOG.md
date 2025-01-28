# Changelog

## [Unreleased] - YYYY-MM-DD
- Improved docstrings by adding examples where missing and by using rounding in all examples to avoid doctest fails
- Fixed a bug where a core getH would return the B-field
- Input `in_out` is by default set to `"auto"` for collections to avoiding ambiguities.
- Improve documentation ([#829](https://github.com/magpylib/magpylib/issues/829))

## [5.1.1] - 2024-10-31
- Included magpylib-force version 0.3.1 in documentation
- Removed unused issue templates and improved PR template

## [5.1.0] - 2024-10-09
- Fixed a bug where the magnetization arrow graphical representation would be anchored badly after rotation ([#805](https://github.com/magpylib/magpylib/issues/805))
- Added `units_length` input to the `show` function to allow displaying axes with different length units. This parameter can be set individually for each subplot. ([#786](https://github.com/magpylib/magpylib/pull/786))
- Small documentation and Readme improvement. Change naming from "explicit expression" to "analytical expression" as described in ([#794](https://github.com/magpylib/magpylib/issues/794)).
- Fixed Pvyvista plot bounds not fitting on animation. Also enables `zoom` feature which was not working until now. ([#798](https://github.com/magpylib/magpylib/pull/798))
- Fixed canvas layout being modified even when user-provided. Also added a new `canvas_update` parameter to choose the layout behavior (by default `"auto"`) ([#799](https://github.com/magpylib/magpylib/pull/799))
- Improved documentation ([#766](https://github.com/magpylib/magpylib/issues/766), [#802](https://github.com/magpylib/magpylib/issues/802))
- Documentation now includes force computation, which is still in a separate package "magpylib-force", but which will be integrated into Magplyib in the coming months. ([#787](https://github.com/magpylib/magpylib/issues/787))

## [5.0.4] - 2024-06-18
- Added support for Numpy 2.0 ([#795](https://github.com/magpylib/magpylib/pull/789))
- Fixed markers legend not being suppressible ([#795](https://github.com/magpylib/magpylib/pull/789))

## [5.0.3] - 2024-06-03
- Fixed subplot object properties propagation ([#780](https://github.com/magpylib/magpylib/pull/780))
- Migrate to pydata-sphinx-theme and fix docs search function ([#762](https://github.com/magpylib/magpylib/pull/762))
- Fixed docs version-switcher ([#782](https://github.com/magpylib/magpylib/pull/782))

## [5.0.2] - 2024-05-21
- Fixed a display issue causing incorrect calculation of view box limits ([#772](https://github.com/magpylib/magpylib/pull/772))
- Removed support for python 3.8 and 3.9 by now following the scientific-python.org support timelines ([#773](https://github.com/magpylib/magpylib/pull/773))
- Fixed CI testing with newer backend versions ([#774](https://github.com/magpylib/magpylib/pull/774))
- Updated site notice to mention the awarded "small development grant" by NumFocus. ([#758](https://github.com/magpylib/magpylib/pull/758))
- Fixed inaccurate citation year for Yang publication ([#764](https://github.com/magpylib/magpylib/pull/764), with thanks to @feldnerd for the contribution!)

## [5.0.1] - 2024-04-12
- Fixed a bug where `getBHJM` of a Collection would produce one extra dimension ([#753](https://github.com/magpylib/magpylib/issues/753))
- Fixed a bug where the legend of a deeply nested Collection would be wrong ([#756](https://github.com/magpylib/magpylib/issues/756))

## [5.0.0] - 2024-03-13
### ⚠️ Breaking Changes ⚠️
- The Magpylib inputs and outputs are now in **SI Units**.
- The `magnetization` parameter has also been redefined to reflect the true physical magnetization quantity in units of A/m.
### Other Improvements
- The `magnetization` parameter is now codependent with the new `polarization` parameter that is the physical magnetic polarization ([#712](https://github.com/magpylib/magpylib/issues/712)) in units of Tesla
- Added `getM` (magnetization) and `getJ` (polarization) top level functions and class methods reminiscent of `getB` and `getH`.
- The `in_out` (inside/outside) parameter is added to all field functions (`getBHJM`) to specify the location of the observers relative to the magnet body in order to increase performance ([#717](https://github.com/magpylib/magpylib/issues/717), [#608](https://github.com/magpylib/magpylib/issues/608))
- Review of documentation and adding a few requested things ([#685](https://github.com/magpylib/magpylib/issues/685), some of [#659](https://github.com/magpylib/magpylib/issues/659))
- Added mu0 at top level as `magpylib.mu_0`. The value of mu0 is taken from scipy and follows the 2019 redefinition. All internal computations now include this new value. ([#714](https://github.com/magpylib/magpylib/issues/714), [#731](https://github.com/magpylib/magpylib/issues/731))
- The core level now includes only the true bottom level implementations. ([#727](https://github.com/magpylib/magpylib/issues/727))
- As Matplotlib graphic representation of 3D objects is terrible, we decided to go back to "arrow" graphic default mode when graphic backend is "Matplotlib".([#735](https://github.com/magpylib/magpylib/issues/735))

## [4.5.1] - 2023-12-28
- Fixed a field computation issue where H-field resulting from axial magnetization is computed incorrectly inside of Cylinders ([#703](https://github.com/magpylib/magpylib/issues/703))

## [4.5.0] - 2023-12-13
- Added optional handedness parameter for Sensors ([#687](https://github.com/magpylib/magpylib/pull/687))
- Renaming classes: `Line`→`Polyline`, `Loop`→`Circle`. Old names are still valid but will issue a `DeprecationWarning` and will eventually be removed in the next major version ([#690](https://github.com/magpylib/magpylib/pull/690))
- Rework CI/CD workflows ([#686](https://github.com/magpylib/magpylib/pull/686))

## [4.4.1] - 2023-11-09
- Fixed deployment release ([#682](https://github.com/magpylib/magpylib/pull/682))
- Fixed axis mismatch on show/hide of sensor arrows ([#679](https://github.com/magpylib/magpylib/pull/679))
- Documentation improvements ([#673](https://github.com/magpylib/magpylib/pull/673))


## [4.4.0] - 2023-09-03
- Included self-intersection check in `TriangularMesh` ([#622](https://github.com/magpylib/magpylib/pull/622))
- Fixed incorrect edge case of TriangularMesh reorientation ([#644](https://github.com/magpylib/magpylib/pull/644))
- Discontinuous segments in `current.Line` are now accepted and correctly treated as separate lines ([#632](https://github.com/magpylib/magpylib/pull/632), [#642](https://github.com/magpylib/magpylib/pull/642))
- Objects can now be displayed with missing dimension and/or excitation ([#640](https://github.com/magpylib/magpylib/pull/640))
- Added magnetization and current arrows `sizemode` styling option (absolute or scaled) ([#639](https://github.com/magpylib/magpylib/pull/639))
- `Collection` objects now also have a default description when displayed (number of children) ([#634](https://github.com/magpylib/magpylib/pull/634))
- Many minor graphic improvements ([#663](https://github.com/magpylib/magpylib/pull/663), [#649](https://github.com/magpylib/magpylib/issues/649), [#653](https://github.com/magpylib/magpylib/issues/653))
- `legend` style option ([#650](https://github.com/magpylib/magpylib/issues/650))
- Changed unit naming in text to comply with DIN Norm 641 ([#614](https://github.com/magpylib/magpylib/issues/614))
- Improved documentation now boasting a contribution guide, a news-blog, an example and tutorial gallery, a getting started section and many other improvements ([#621](https://github.com/magpylib/magpylib/issues/621), [#596](https://github.com/magpylib/magpylib/issues/596), [#580](https://github.com/magpylib/magpylib/issues/580))
- Improved numerical stability of `CylinderSegment`, ([#648](https://github.com/magpylib/magpylib/issues/648), [#651](https://github.com/magpylib/magpylib/issues/651))


## [4.3.0] - 2023-06-25
- New `TriangularMesh` magnet class added to conveniently work with triangular surface meshes instead of large collections of individual `Triangle` objects. The `TriangularMesh` class performs important checks (closed, connected, oriented) and can directly import Pyvista objects and for convex hull bodies. ([#569](https://github.com/magpylib/magpylib/issues/569), [#598](https://github.com/magpylib/magpylib/pull/598)).
- Added magnetization coloring for `matplotlib` backend ([#597](https://github.com/magpylib/magpylib/pull/597))
- New automatic backend behavior, set to a dynamic default `auto` depending on the current environment and the given `canvas`, if provided. ([#617](https://github.com/magpylib/magpylib/pull/617))
- Drop python 3.7 support, following python life cycle. ([#616](https://github.com/magpylib/magpylib/pull/616))

## [4.2.0] - 2023-01-27
- (Re)introducing the powerful `misc.Triangle` class that can be used to compute magnetic fields of arbitrarily shaped bodies by approximating their surface with triangular faces. ([#568](https://github.com/magpylib/magpylib/issues/568))
- Introducing the `magnet.Tetrahedron` class as a derivate of the Triangle class. ([#289](https://github.com/magpylib/magpylib/issues/289))
- Change Pyvista plotting defaults when using `show(backend='pyvista')` to fit better with other libraries. ([#551](https://github.com/magpylib/magpylib/issues/551))
- Added code of conduct attempting to align with NumFocus standards ([#558](https://github.com/magpylib/magpylib/issues/558))
- Improved Loop field computation in terms of performance and numerical stability ([#374](https://github.com/magpylib/magpylib/issues/374))
- Added `magnetization.mode` style to allow showing magnetization direction for any backend ([#576](https://github.com/magpylib/magpylib/pull/576))
- Documentation changes:
    - Correct conda install command
    - Integration of Triangle and Tetrahedron
    - Changed example gallery substructure
    - Rewritten and added some passages
- Fixed some bugs, minor performance increase, internal refactoring

## [4.1.2] - 2023-01-15
- Fixed wrong magnetization arrow direction for some edge cases ([#570](https://github.com/magpylib/magpylib/discussions/570), [#571](https://github.com/magpylib/magpylib/issues/571), [#572](https://github.com/magpylib/magpylib/pull/572))
- Fixed cryptic `getB`/`getH` error message ([#562](https://github.com/magpylib/magpylib/issues/562), [#563](https://github.com/magpylib/magpylib/pull/563))

## [4.1.1] - 2022-08-11
- Fixed inverted y and z axes colors for sensor representations ([#556](https://github.com/magpylib/magpylib/pull/556))

## [4.1.0] - 2022-08-08
- Field computation `getB`/`getH` now supports 2D [pandas](https://pandas.pydata.org/).[dataframe](https://pandas.pydata.org/docs/user_guide/dsintro.html#dataframe) in addition to the `numpy.ndarray` as output type. ([#523](https://github.com/magpylib/magpylib/pull/523))
- Internal `getB`/`getH` refactoring. The direct interface with `'Line'` source argument now also accepts `'vertices'` as argument. ([#540](https://github.com/magpylib/magpylib/pull/540))
- Complete plotting backend rework to prepare for easy implementation of new backends, with minimal maintenance. ([#539](https://github.com/magpylib/magpylib/pull/539))
- New [Pyvista](https://docs.pyvista.org/) plotting backend ([#548](https://github.com/magpylib/magpylib/pull/548))
- Improvements on the [documentation](https://magpylib.readthedocs.io/en/latest/)

## [4.0.4] - 2022-06-09

- Exclude redundant properties with `_all` suffix in the `.describe()` method ([#534](https://github.com/magpylib/magpylib/pull/534))
- Docstring improvements ([#535](https://github.com/magpylib/magpylib/pull/535))

## [4.0.3] - 2022-05-13

- Fixed copy order Bug ([#530](https://github.com/magpylib/magpylib/issues/530))

## [4.0.2] - 2022-05-04

- Fixed magnetization coloring with mesh grouping (Plotly) ([#526](https://github.com/magpylib/magpylib/pull/526))
- Allow float color quadruples ([#529](https://github.com/magpylib/magpylib/pull/529))

## [4.0.1] - 2022-04-29

- Graphic performance update for Plotly when showing a large number of objects. ([#524](https://github.com/magpylib/magpylib/pull/524))

## [4.0.0] - 2022-04-14

This is a major update that includes

- API changes
- New features
- Improved internal workings

### Magpylib class changes/fixes:
- `Box` class renamed to `Cuboid`. ([#350](https://github.com/magpylib/magpylib/issues/350))
- `Circular` class renamed to `Loop`. ([#402](https://github.com/magpylib/magpylib/pull/402))
- New `CylinderSegment` class with dimension `(r1,r2,h,phi1,phi2)` with the inner radius `r1`, the outer radius `r2` the height `h` and the cylinder section angles `phi1 < phi2`. ([#386](https://github.com/magpylib/magpylib/issues/386), [#385](https://github.com/magpylib/magpylib/issues/385), [#484](https://github.com/magpylib/magpylib/pull/484), [#480](https://github.com/magpylib/magpylib/issues/480))
- New `CustomSource` class for user defined field functions ([#349](https://github.com/magpylib/magpylib/issues/349), [#409](https://github.com/magpylib/magpylib/issues/409), [#411](https://github.com/magpylib/magpylib/pull/411), [#506](https://github.com/magpylib/magpylib/pull/506))
- All Magpylib objects can now be initialized without excitation and dimension attributes.
- All classes now have the `parent` attribute to reference to a collection they are part of. Any object can only have a single parent.
- All classes have the `describe` method which gives a quick object property overview.

### Field computation changes/fixes:
- New computation core. Added top level subpackage `magpylib.core` where all field implementations can be accessed directly without the position/orientation interface. ([#376](https://github.com/magpylib/magpylib/issues/376))
- Direct interface functions `getBdict` and `getHdict` (previously `getBv` and `getHv`) are now integrated into `getB` and `getH`. See docs for details ([#449](https://github.com/magpylib/magpylib/pull/449))
- Generally improved field expressions: ([#374](https://github.com/magpylib/magpylib/issues/374))
  - Negative dimension input taken as absolute when only positive dimensions are allowed.
  - Scale invariant field evaluations.
  - Special cases caught within 1e-15 rtol and atol to account for numerical imprecision with positioning (e.g. object rotation).
  - Suppress Numpy divide/invalid warnings. return `np.nan` as `(0,0,0)` (e.g. on magnet edges or on line currents) and allow return of `np.inf`.
  - New closed form implementation for `Cylinder` with diametral magnetization is much faster (100-1000x) and numerically stable for small `r`. ([#404](https://github.com/magpylib/magpylib/issues/404), [#370](https://github.com/magpylib/magpylib/issues/370))
  - Improved numerical stability of current loop field. Now 12-14 correct digits everywhere. ([#374](https://github.com/magpylib/magpylib/issues/374))
  - Fixed `Collection` of `Lines` field computation error. ([#368](https://github.com/magpylib/magpylib/issues/368))
- Object oriented interface fixes and modifications:
  - Improved performance of `getB` and `getH`.
  - Fixed array dimension wrongly reduced when `sumup=True` and `squeeze=False` in `getB` and `getH` functions ([#425](https://github.com/magpylib/magpylib/issues/425), [#426](https://github.com/magpylib/magpylib/pull/426))
  - Minimal non-squeeze output shape is (1,1,1,1,3), meaning that a single pixel is now also represented. ([#493](https://github.com/magpylib/magpylib/pull/493))
- With the new kwarg `pixel_agg` it is now possible to apply a Numpy function with reducing functionality (like `mean`, `min`, `average`) to the pixel output. In this case, it is allowed to provide `getB` and `getH` with different observer input shapes. ([#503](https://github.com/magpylib/magpylib/pull/503))

### Major graphic output overhaul:
- Styles:
  - All object now have the `style` attribute for graphical output customization. Arguments can be passed as dictionaries, class attributes or with underscore magic.
  - Style defaults stored in `magpylib.defaults.display`. ([#291](https://github.com/magpylib/magpylib/issues/291), [#396](https://github.com/magpylib/magpylib/pull/396))
  - Possibility to add a custom 3D-model to any object. ([#416](https://github.com/magpylib/magpylib/pull/416))
- `display` now called `show`, to be more in-line with standard graphic backends. Functionality completely overhauled to function with styles. ([#453](https://github.com/magpylib/magpylib/pull/453), [#451](https://github.com/magpylib/magpylib/issues/451))
  - New `show` arguments replace previous ones. Some are now handed over through styles.
    - `axis` ➡️ `canvas`
    - `show_direction` ➡️ `style_magnetization_show`
    - `show_path` ➡️ `style_path_show` ([#453](https://github.com/magpylib/magpylib/pull/453))
    - `size_sensors`&`size_dipoles` ➡️ `style_size`
    - `size_direction` ➡️ `style_magnetization_size`
    - new `zoom` option
- Plotly as new optional graphic backend. 🚀 ([#396](https://github.com/magpylib/magpylib/pull/396), [#353](https://github.com/magpylib/magpylib/issues/353))
  - `plotly` is now automatically installed with Magpylib. ([#395](https://github.com/magpylib/magpylib/issues/395))
  - Interactive path `animation` option in `show`. ([#453](https://github.com/magpylib/magpylib/pull/453))
  - Automatic Matplotlib <-> Plotly style input translations ([#452](https://github.com/magpylib/magpylib/issues/452), [#454](https://github.com/magpylib/magpylib/pull/454))
- Misc:
  - Added `matplotlib` pixel display ([#279](https://github.com/magpylib/magpylib/issues/279))
  - Sensors have their own color now ([#483](https://github.com/magpylib/magpylib/pull/483))
  - UI fix empty display ([#401](https://github.com/magpylib/magpylib/issues/401))
  - Error msg when `show` is called without argument ([#448](https://github.com/magpylib/magpylib/issues/448))

### New documentation:
- Completely new structure and layout. ([#399](https://github.com/magpylib/magpylib/issues/399), [#294](https://github.com/magpylib/magpylib/issues/294))
- Binder links and live code. ([#389](https://github.com/magpylib/magpylib/issues/389))
- Example galleries with practical user examples
- Guidelines for advanced subclassing of `Collection` to form complex dynamic compound objects that seamlessly integrate into the Magpylib interface.

### Geometry interface modification
- Added all Scipy Rotation forms as rotation object methods. ([#427](https://github.com/magpylib/magpylib/pull/427))
- `move` and `rotate` inputs differentiate between scalar and vector input. Scalar input is applied to the whole path vector input is merged. ([#438](https://github.com/magpylib/magpylib/discussions/438), [#444](https://github.com/magpylib/magpylib/issues/444), [#442](https://github.com/magpylib/magpylib/issues/443))
- `move` and `rotate` methods have default `start='auto'` (scalar input: `start=0`-> applied to whole path, vector input: `start=len_path`-> append) instead of `start=-1`.
- `move` and `rotate` methods maintain collection geometry when applied to a collection.
- Improved `position` and `orientation` setter methods in line with `move` and `rotate` functionality and maintain `Collection` geometry.
- Removed `increment` argument from `move` and `rotate` functions ([#438](https://github.com/magpylib/magpylib/discussions/438), [#444](https://github.com/magpylib/magpylib/issues/444))

### Modifications to the `Collection` class
- Collections can now contain `Source`, `Sensor` and other `Collection` objects and can function as source and observer inputs in `getB` and `getH`. ([#502](https://github.com/magpylib/magpylib/pull/502), [#410](https://github.com/magpylib/magpylib/issues/410), [#415](https://github.com/magpylib/magpylib/pull/415), [#297](https://github.com/magpylib/magpylib/issues/297))
- Instead of the property `Collection.sources` there are now the `Collection.children`, `Collection.sources`, `Collection.sensors` and `Collection.collections` properties. Setting these collection properties will automatically override parents. ([#446](https://github.com/magpylib/magpylib/issues/446), [#502](https://github.com/magpylib/magpylib/pull/502))
- `Collection` has it's own `position`, `orientation` and `style`. ([#444](https://github.com/magpylib/magpylib/issues/444), [#461](https://github.com/magpylib/magpylib/issues/461))
- All methods applied to a collection maintain relative child-positions in the local reference frame.
- Added `__len__` dunder for `Collection`, so that `Collection.children` length is returned. ([#383](https://github.com/magpylib/magpylib/issues/383))
- `-` operation was removed.
- `+` operation now functions as `a + b = Collection(a, b)`. Warning: `a + b + c` now creates a nested collection !
- Allowed `Collection`, `add` and  `remove` input is now only `*args` or a single flat list or tuple of Magpylib objects.
- `add` and `remove` have some additional functionality related to child-parent relations.
- The `describe` method gives a great Collection tree overview.

### Other changes/fixes:
- Magpylib error message improvement. Msg will now tell you what input is expected.
- Magpylib object `copy` method now works properly ([#477](https://github.com/magpylib/magpylib/pull/477), [#470](https://github.com/magpylib/magpylib/pull/470), [#476](https://github.com/magpylib/magpylib/issues/476))
- Defaults and input checks ([#406](https://github.com/magpylib/magpylib/issues/406))
  - `magpylib.Config` parameters are now in `magpylib.defaults`. ([#387](https://github.com/magpylib/magpylib/issues/387))
  - `config.ITERCYLINDER` is now obsolete. The iterative solution replaced by a new analytical expression.
  - `config.inputchecks` is removed - input checks are always performed.

---
## [3.0.5] - 2022-04-26

- fix docs build
---
## [3.0.4] - 2022-02-17

- fix `Collection` operation tests

---
## [3.0.3] - 2022-02-17

### Fixed
- When adding with `Source + Collection` to create a new `Collection`, the original now remains unaffected ([#472](https://github.com/magpylib/magpylib/issues/472))

---

## [3.0.2] - 2021-06-27
- Update release version and license year ([#343](https://github.com/magpylib/magpylib/pull/343), [#344](https://github.com/magpylib/magpylib/pull/344))

---

## [3.0.1] - 2021-06-27

- Added deployment automation ([#260](https://github.com/magpylib/magpylib/issues/260), [#296](https://github.com/magpylib/magpylib/issues/296), [#341](https://github.com/magpylib/magpylib/pull/341), [#342](https://github.com/magpylib/magpylib/pull/342))


---
## [3.0.0] - 2021-06-27

This is a major update that includes

- API changes
- New features
- Improved internal workings
### Added

- New `orientation` property:
  - The `orientation` attribute stores the relative rotation of an object with respect to the reference orientation (defined in each class docstring).
  - The default (`orientation=None`) corresponds to a unit rotation.
  - `orientation` is stored as a `scipy.spatial.transform.Rotation` object.
  - Calling the attribute `source.orientation` returns a Scipy Rotation object `R`.
  - Make use of all advantages of this great Scipy package:
    - define `R.from_rotvec()` or `R.from_quat()` or ...
    - view with `R.as_rotvec()` or `R.as_quat()` or ...
    - combine subsequent rotations `R1 * R2 * R3`
- Sensor pixel:
  - The new `Sensor(position, pixel, orientation)` class has the argument `pixel` which is `(0,0,0)` by default and refers to pixel positions inside the Sensor (in the Sensor local CS). `pixel` is an arbitrary array_like of the shape (N1, N2, ..., 3).
- Geometry paths:
  - The `position` and `orientation` attributes can now store paths in the global CS. For a path of length M the attribute `position` is an array of the shape (M,3) and `orientation` is a Rotation object with length M. Each path position is associated with a respective rotation.
  - Field computations `getB()` and `getH()` will evaluate the field for all source path positions.
  - Paths can be set by hand `position = X`, `orientation = Y`, but they can also conveniently be generated using the `rotate` and `move` methods.
  - Paths can be shown via the `show_path=True` kwarg in `display()`. By setting `show_path=x` the object will be displayed at every `x`'th path step. This helps to follow up on object rotation along the path.
  - All objects have a `reset_path()` method defined to set their paths to `position=(0,0,0)` and `orientation=None`.

- Streamlining operation with all Magpylib objects:
  - All objects (Sensors, Sources, Collections) have additional direct access to
    - `.display()` method for quick self-inspection.
    - `getB()` and `getH()` methods for fast field computations
    - `__repr__` attribute defined and will return their type and their `id`.
- Other new features:
  - The top-level `Config` allows users to access and edit Magpylib default values.
### Changed
- Renamed modules:
  - `.magnet` and `.current` sub-packages were moved to the top level.
  - The `.moment` sub-package was renamed to `.misc` and was moved to the top level.
  - The `.vector` sub-package was completely removed. Functionalities are mostly replaced by new top-level function `getBv()`.
  - The `.math` sub-package was removed. Functionalities are mostly provided by the `scipy - Rotation` package.
- Renamed functions:
  - The top level function `displaySystem()` was renamed to `display()`.
- Renamed attributes (parameters cannot be initialized in their short forms anymore):
    - `angle` and `axis` are replaced by `orientation`
    - `dimension` is replaced by `diameter` for Loop and Sphere classes.
    - `angle`&`axis` are replaced by `orientation`.

- Modified rotate methods:
  - The class methods `.rotate(angle, axis, anchor)` have been replaced by a new `.rotate(rotation, anchor, increment, start)` method where `rotation` ist a scipy `Rotation` object.
  - The original angle-axis-anchor rotation is now provided by the new method `.rotate_from_angax(angle, axis, anchor, increment, start, degrees)`.
    - The argument `axis` can now easily be set to the global CS axes with `"x"`, `"y"`, `"z"`.
    - The anchor argument `anchor=0` represents the origin `(0,0,0)`.
    - `angle` argument is in units of deg by default. It can now be set to rad using the `degrees` argument.
  - The "move"-class method is now `.move(displacement, increment, start)`
  - Rotation and move methods can now be used to generate paths using vector input and the `increment` and `start` arguments.
  - All operations can now be chained (e.g. `.move_by().rotate().move_to()`)
- Miscellaneous:
  - `getB(pos)` now takes single AND vector position arguments. If a vector is handed to getB it will automatically execute vectorized code from the vector module.
  - In a finite region (size defined by `Config.EDGESIZE`) about magnet edges and line currents the field evaluates to `(0,0,0)` instead of `(NaN, NaN, NaN)`. Special case catching reduces performance slightly.
### Updated
- Improved Computation:
  - The Box field is now more stable. Numerical instabilities in the outfield were completely removed.
- Updated Field computation interface
  - There are two fundamental arguments for field computation:
    - The argument `sources` refers to a source/Collection or to a 1D list of L sources and/or Collections.
    - The argument `observers` refers to a set of positions of shape (N1, N2, ..., 3) or a Sensor with `pixel` shape (N1, N2, ..., 3) or a 1D list of K Sensors.
  - With Magpylib3 there are several ways to compute the field:
    1. `source.getB(*observers)`
    2. `sensor.getB(*sources)`
    3. `magpylib.getB(sources, observers)`
      - The output shape is always (L, M, K, N1, N2, ..., 3) with L sources, M path positions, K sensors and N (pixel) positions.
      - Objects with shorter paths will be considered as static once their path ends while other paths continue.
    4. `magpylib.getBv(**kwargs)` gives direct access to the field formulas and mostly replaces the `getBv_XXX()` functionality of v2. All inputs must be arrays of length N or of length 1 (statics will be tiled).
  - While `getBv` is the fastest way to compute the fields it is much more convenient to use `getB()` which mostly provides the same performance. Specifically,the new `getB()` automatically groups all inputs for combined vectorized evaluation. This leads to a massive speedup when dealing with large Collections of similar sources.
  - In addition to `getB`, the new `getH` returns the field in kA/m.

### Removed
- the kwarg `niter=50` does not exist anymore for the Cylinder field computation. The functionality was completely replaced by the config setting `Config.ITER_CYLINDER=50`.

---
## [2.3.0b] - 2020-01-17

### Changed
- Improved performance of `getB` for diametral magnetized Cylinders by 20%.
- `getB` of Line current now uses vectorized code which leads to massive performance enhancement.
- **IMPORTANT:** position arguments of `getBv` functions have been flipped! First comes the source position POSm THEN the observer position POSo!


### Added
- completed the library vector functionality adding magnet Cylinder, moment Dipole, current Loop and Line. This includes adding several private vectorized functions (e.g. ellipticV) to mathLib_vector, adding respective tests and docs examples.

---

## [2.1.0b] - 2019-12-06

### Added
- Docstrings for vector functions.
- `displaySystem` kwarg `figsize`
- bringing documentation up to speed

### Fixed
- init file bug

---

## [2.0.0b] - 2019-11-29
This is a major update that includes

API changes
New features
Improved internal workings
### Changed
- Restructuring
  - displaySystem is now a top-level function, not a Collection method anymore.
  - getBsweep and multiprocessing options have been completely removed, this functionality
    should be overtaken by the new vector functionality which uses the numpy native vectorized
    code paradigm. If mkl library is set (test by numpy.show_config()) numpy will also
    automatically use multiprocessing. Code parallelization at magpylib level should be done
    by hand.
- Docstrings are adjusted to work better with intellisense. (Problems with *.rst code)
- public rotatePosition() is now called angleAxisRotation(), former private angleAxisRotation
    is now called angleAxisRotation_priv().
- Major rework of the documentation and examples.

### Added
- Performance computation trough vector functionality included in new top-level subpackage "vector"
- Vectorized versions of math functions added to "math" subpackage

---

## [1.2.1b0] - 2019-07-31
### Changed
- Optimized `getB` call (utility integrated)
- Improved Documentation (added Sensor class v1)

---

## [1.2.0b0] - 2019-07-16
### Added
- Sensor Class
  - This allows users to create a coordinate system-enabled Sensor object, which can be placed, rotated, moved, and oriented.
  - This object can take the B-Field of a system (be it single source or a Collection) with the added functionality of having its own reference in the coordinate space, allowing users to easily acquire relative B-Field measurements of a system from an arbitrarily placed sensor object.
  - Sensors in a list may be displayed in the `Collection.displaySystem()` by using the `sensors` keyword argument.
- Added content to the `__repr__` built-in to all source classes for quick console evaluations, simply call a defined object in your Python shell to print out its attributes.
### Changed
- Edge cases in field calculations now return a proper [RuntimeWarning](https://docs.python.org/3/library/exceptions.html#RuntimeWarning) instead of console prints
### Fixed
- Unused imports and variables

---

## [1.1.1b0] - 2019-06-25
### Added
- Changelog
### Changed
- Change `Collection.displaySystem()` not having the `block=False` setting for matplotlib's `pyplot.show()` by default, this meant that outside interactive mode calling this function would hang the script until the plot was closed.
  - If for some reason you want to block the application, you may still use `Collection.displaySystem()`'s `suppress=True` kwarg then call pyplot.show() normally.
  - This should cause no API changes, if you have problems please notify us.

### Fixed
- Fixed multiprocessing enabled `Collection.getBsweep()` for lots of objects with few positions causing great performance loss. This functionality now behaves as expected for the use case.
- Fixed `Collection.displaySystem()`'s drawing of Dipole objects in external axes (plots) using the `subplotAx` kwarg crashing the application. This functionality now behaves as expected for the use case.

---

## [1.1.0b0] - 2019-06-14
### Added
- Implemented one new kwarg for `Collection.displaySystem()`:

    > `subplotAx=None`
        Draw into a subplot axe that already exists. The subplot needs to be 3D projected

  This allows for creating side-by-side plots using `displaySystem`.
  Figure information must be set manually in pyplot.figure() in order to not squash the plots upon sub plotting.


    <details>
    <summary> Click here for Example </summary>

    Code: https://gist.github.com/lucasgcb/77d55f2fda688e2fb8e1e4a68bb830b8

    **Output:**
    ![image](https://user-images.githubusercontent.com/7332704/58973138-86b4a600-87bf-11e9-9e63-35892b7a6713.png)

    </details>

### Changed

- `getBsweep()` for Collections and Sources now always returns a Numpy array
- Zero-length segments in Line sources now return `[0,0,0]` and a warning, making it easier to draw spirals without letting users do this unaware.

### Fixed
- Added a workaround fix for a rotation bug we are still working on.

---

## [1.0.2b0] - 2019-05-29

### Added

- `MANIFEST.in` file containing the LICENSE for bundling in PyPI

---

## [1.0.1b0] - 2019-05-28

### Added

- Issue and Pull Request Templates to Repository
- Continuous Integration settings (Azure and Appveyor)
- Code Coverage Reports with Codecov



### Removed

- Support for Python 3.5 and under.

---

## [1.0.0b0] - 2019-05-21

The first official release of the Magpylib library.

### Added

- Source classes:
   - Box
   - Cylinder
   - Sphere
   - Loop Current
   - Current Line
   - Dipole
- Collection class

---

[Unreleased]:https://github.com/magpylib/magpylib/compare/5.1.1...HEAD
[5.1.1]:https://github.com/magpylib/magpylib/compare/5.1.0...5.1.1
[5.1.0]:https://github.com/magpylib/magpylib/compare/5.0.4...5.1.0
[5.0.4]:https://github.com/magpylib/magpylib/compare/5.0.3...5.0.4
[5.0.3]:https://github.com/magpylib/magpylib/compare/5.0.2...5.0.3
[5.0.2]:https://github.com/magpylib/magpylib/compare/5.0.1...5.0.2
[5.0.1]:https://github.com/magpylib/magpylib/compare/5.0.0...5.0.1
[5.0.0]:https://github.com/magpylib/magpylib/compare/4.5.1...5.0.0
[4.5.1]:https://github.com/magpylib/magpylib/compare/4.5.0...4.5.1
[4.5.0]:https://github.com/magpylib/magpylib/compare/4.4.0...4.5.0
[4.4.1]:https://github.com/magpylib/magpylib/compare/4.4.0...4.4.1
[4.4.0]:https://github.com/magpylib/magpylib/compare/4.3.0...4.4.0
[4.3.0]:https://github.com/magpylib/magpylib/compare/4.2.0...4.3.0
[4.2.0]:https://github.com/magpylib/magpylib/compare/4.1.2...4.2.0
[4.1.2]:https://github.com/magpylib/magpylib/compare/4.1.1...4.1.2
[4.1.1]:https://github.com/magpylib/magpylib/compare/4.1.0...4.1.1
[4.1.0]:https://github.com/magpylib/magpylib/compare/4.0.4...4.1.0
[4.0.4]:https://github.com/magpylib/magpylib/compare/4.0.3...4.0.4
[4.0.3]:https://github.com/magpylib/magpylib/compare/4.0.2...4.0.3
[4.0.2]:https://github.com/magpylib/magpylib/compare/4.0.1...4.0.2
[4.0.1]:https://github.com/magpylib/magpylib/compare/4.0.0...4.0.1
[4.0.0]:https://github.com/magpylib/magpylib/compare/3.0.4...4.0.0
[3.0.5]:https://github.com/magpylib/magpylib/compare/3.0.4...3.0.5
[3.0.4]:https://github.com/magpylib/magpylib/compare/3.0.3...3.0.4
[3.0.3]:https://github.com/magpylib/magpylib/compare/3.0.2...3.0.3
[3.0.2]:https://github.com/magpylib/magpylib/compare/3.0.1...3.0.2
[3.0.1]:https://github.com/magpylib/magpylib/compare/3.0.0...3.0.1
[3.0.0]:https://github.com/magpylib/magpylib/compare/2.3.0-beta...3.0.0
[2.3.0b]:https://github.com/magpylib/magpylib/compare/2.1.0-beta...2.3.0-beta
[2.1.0b]:https://github.com/magpylib/magpylib/compare/2.0.0-beta...2.1.0-beta
[2.0.0b]:https://github.com/magpylib/magpylib/compare/1.2.1-beta...2.0.0-beta
[1.2.1b0]: https://github.com/magpylib/magpylib/compare/1.2.0-beta...1.2.1-beta
[1.2.0b0]: https://github.com/magpylib/magpylib/compare/1.1.1-beta...1.2.0-beta
[1.1.1b0]: https://github.com/magpylib/magpylib/compare/1.1.0-beta...1.1.1-beta
[1.1.0b0]: https://github.com/magpylib/magpylib/compare/1.0.1-beta...1.1.0-beta
[1.0.2b0]: https://github.com/magpylib/magpylib/compare/1.0.1-beta...1.0.2-beta
[1.0.1b0]: https://github.com/magpylib/magpylib/compare/1.0.0-beta...1.0.1-beta
[1.0.0b0]: https://github.com/magpylib/magpylib/releases/tag/1.0.0-beta


The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
