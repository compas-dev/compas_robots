# COMPAS Robots

`compas_robots` provides basic infrastructure for working with robots in COMPAS.
It includes classes for describing robot models, kinematic chains and coordinate frames,
plus loaders for URDF resources and scene objects for visualizing robots in
Rhino, Blender, GHPython and the COMPAS viewer.

On top of this, the [COMPAS FAB](https://compas.dev/compas_fab/latest/)
extension package provides additional functionality to connect these models with planning
and execution tools and libraries.

```pycon
>>> from compas_robots import RobotModel
>>> from compas.geometry import Box, Frame
>>> model = RobotModel(name="Boxy")
>>> _ = model.add_link(name="box_link", visual_meshes=[Box(1, 2, 0.5)])
>>> print(model)
Robot name=Boxy, Links=1, Joints=0 (0 configurable)
```
