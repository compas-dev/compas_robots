# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] 2024-10-04

### Added

### Changed

* Fixed no scene object registered for `RobotModel` in context `Rhino`.
* Adapted import inside `RobotModelObject` to latest changes in `compas_ghpython`.
* Updated minimum COMPAS version to `2.4.3`.

### Removed


## [0.5.0] 2024-09-26

### Added

### Changed

* Fixed all four `RobotModelObject.__init__` to not accept `model` input.
  The model is set at `SceneObject.item` and is available from `BaseRobotModelObject.model`.
* Fixed `self.configuration` unassigned error when `RobotModelObject` is being initialized by `Scene.add()`.
* Dropped support for Python 3.8 and updated compas requirements to 2.3
* Fixed `robotmodelobject` attribute.
* Added `__deepcopy__` to `ProxyObject` to solve recursion error when RobotModel is deep copied.

### Removed


## [0.4.0] 2024-04-29

### Added

* Added support for `compas_viewer`

### Changed

### Removed


## [0.3.0] 2024-02-20

### Added

### Changed

* Moved private methods `_get_file_format` and `_mesh_import` to `compas_robots.resources` and made them public (`get_file_format` and `mesh_import`).

### Removed


## [0.2.3] 2024-02-16

### Added

### Changed

* Fixed bug in `RobotModelObject` caused by non-existent `compas_rhino.rs`. Replaced with `import rhinoscriptsyntax as rs`.
* Allow no `support_package` in `LocalPackageMeshLoader`

### Removed


## [0.2.2] 2024-02-06

### Added

### Changed

* Fixed bug in URDF serialization of colors.

### Removed


## [0.2.1] 2024-02-02

### Added

### Changed

### Removed


## [0.2.0] 2024-02-01

### Added

* Update all artists to the new `SceneObject` system.
* Added `precision` parameter to `load_geometry` method instead of relying exclusively on the global precision setting.
* Use `compas.tolerance` to format `Configuration` values.

### Changed

* Changed minimum requirements to `COMPAS 2.x`.
* Moved `RobotModel`, `ToolModel` and `Configuration` to the top-level package of this library.
* Moved `URDF` parsing from core into this library.
* Changed urdf parsing to use `compas.colors.Color` instead of a robot-specific color class.
* Changed `ToolModel.link_name` to `ToolModel.connected_to`.
* Fixed data serialization for `RobotModel` and `ToolModel`.
* Update all data serialization to `COMPAS 2.0` convention.
* Renamed `Geometry` in robot model to `LinkGeometry`.
* Fixed `data` serialization API to comply with `COMPAS 2.0` private data API.

### Removed

* Removed deprecated aliases `Origin`, `Cylinder`, `Box`, `Sphere`, `Capsule`.
* Removed deprecated method `load_mesh` of resource loaders.
* Removed deprecated support for `values` and `types` keys in `Configuration` serialization.
