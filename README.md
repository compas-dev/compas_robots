# COMPAS Robots

[![Made with COMPAS](https://compas.dev/badge.svg)](https://compas.dev)
 [![PyPI](https://img.shields.io/pypi/v/compas_robots)](https://pypi.org/project/compas_robots/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Robot models and visualization for the [COMPAS framework](https://compas.dev).

## Features

- Load and build robot models from URDF files or programmatically
- Visualize robots in **Rhino**, **Grasshopper**, **Blender**, and the **COMPAS Viewer**
- Forward kinematics and configuration management
- Load geometry from local files or directly from GitHub repositories
- Attach tools and meshes to robot links

## Installation

```bash
pip install compas_robots
```

## Quick start

```python
import math
from compas_robots import RobotModel
from compas_viewer import Viewer

model = RobotModel.ur5e(load_geometry=True)

config = model.zero_configuration()
config["shoulder_lift_joint"] = -math.pi / 2
config["elbow_joint"]         =  math.pi / 2
config["wrist_1_joint"]       = -math.pi / 2
config["wrist_2_joint"]       = -math.pi / 2

viewer = Viewer()
scene_object = viewer.scene.add(model)
scene_object.update(config)
viewer.show()
```

## Loading robot models

From a URDF file:

```python
from compas_robots import RobotModel

model = RobotModel.from_urdf_file("ur5e.urdf")
```

From a GitHub repository:

```python
from compas_robots import RobotModel
from compas_robots.resources import GithubPackageMeshLoader

github = GithubPackageMeshLoader("ros-industrial/abb", "abb_irb6600_support", "kinetic-devel")
model = RobotModel.from_urdf_file(github.load_urdf("irb6640.urdf"))
model.load_geometry(github)
```

## Documentation

Full documentation, tutorials, and examples at [compas.dev/compas_robots](https://compas.dev/compas_robots).

## Contributing

### Setup

```bash
git clone https://github.com/compas-dev/compas_robots
cd compas_robots
pip install -e ".[dev]"
```

### Code style

```bash
invoke lint      # check style
invoke format    # auto-format
```

### Tests

```bash
invoke test
```

### Docs

```bash
invoke docs
```

### Releases

Releases follow [semver](https://semver.org/spec/v2.0.0.html):

```bash
invoke release minor
```

## License

MIT. See [LICENSE](LICENSE).
