# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
