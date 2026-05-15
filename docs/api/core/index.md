# Core

Platform-independent modules. These work everywhere `compas_robots` can be
imported and form the foundation that the integrations build on top of.

- **[compas_robots](../compas_robots.md)**: top-level package exports such as [Configuration][compas_robots.Configuration], [RobotModel][compas_robots.RobotModel], [ToolModel][compas_robots.ToolModel].
- **[compas_robots.model](../compas_robots.model.md)**: the parts that make up a robot model: [Link][compas_robots.model.Link], [Joint][compas_robots.model.Joint], [LinkGeometry][compas_robots.model.LinkGeometry], [JointType][compas_robots.model.JointType], etc.
- **[compas_robots.resources](../compas_robots.resources.md)**: loaders
  that fetch externally referenced meshes (local files, packages, GitHub).
- **[compas_robots.scene](../compas_robots.scene.md)**: scene-graph
  objects for visualizing a [RobotModel][compas_robots.RobotModel]. The integration packages provide the host-specific implementations.
- **[compas_robots.files](../compas_robots.files.md)**: URDF parsing and
  serialization.
