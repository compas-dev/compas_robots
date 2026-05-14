# Integrations

Host-specific bindings that render and interact with robot models inside
a CAD environment or viewer. Each module is only importable when its host
is available; pick the one that matches where your code runs.

- **[compas_robots.blender](../compas_robots.blender.md)**: Blender scene
  objects.
- **[compas_robots.ghpython](../compas_robots.ghpython.md)**: Grasshopper
  (GHPython) scene objects.
- **[compas_robots.rhino](../compas_robots.rhino.md)**: Rhino scene objects.
- **[compas_robots.viewer](../compas_robots.viewer.md)**: COMPAS viewer
  scene objects.

These all implement the abstractions defined in
[compas_robots.scene](../compas_robots.scene.md).
