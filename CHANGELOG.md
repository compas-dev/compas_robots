# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

* Update all artists to the new `SceneObject` system.

### Changed

* Changed minimum requirements to `COMPAS 2.x`.
* Moved `RobotModel`, `ToolModel` and `Configuration` to the top-level package of this library.
* Moved `URDF` parsing from core into this library.
* Changed urdf parsing to use `compas.colors.Color` instead of a robot-specific color class.
* Changed `ToolModel.link_name` to `ToolModel.connected_to`.
* Fixed data serialization for `RobotModel` and `ToolModel`.
* Update all data serialization to `COMPAS 2.0` convention

### Removed

* Removed deprecated aliases `Origin`, `Cylinder`, `Box`, `Sphere`, `Capsule`.
* Removed deprecated method `load_mesh` of resource loaders.
