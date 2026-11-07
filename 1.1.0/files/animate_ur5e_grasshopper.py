"""Animate a UR5e in Grasshopper using a self-rescheduling component.

Paste this script into a GhPython component. The component re-triggers itself
every ~33 ms (≈ 30 fps) via compas_ghpython.timer.update_component while `run` is True.
State is kept in scriptcontext.sticky so it survives between re-evaluations.

Inputs
------
run  : bool
    Connect a Toggle. Flip to True to start, False to stop.
reset : bool
    Connect a Button. Press to pick new random start/end poses and restart.
"""

from compas.scene import Scene
from compas_ghpython.timer import update_component
from scriptcontext import sticky  # type: ignore

from compas_robots import RobotModel

N_STEPS = 60
INTERVAL_MS = 33  # ≈ 30 fps

# ---- one-time initialisation ------------------------------------------------

if "model" not in sticky or reset:
    model = RobotModel.ur5e(load_geometry=True)
    scene = Scene()
    scene_object = scene.add(model)

    sticky["model"] = model
    sticky["scene_object"] = scene_object
    sticky["start"] = model.random_configuration()
    sticky["end"] = model.random_configuration()
    sticky["step"] = 0

model = sticky["model"]
scene_object = sticky["scene_object"]

# ---- per-tick update --------------------------------------------------------

step = sticky["step"]

if run:
    t = (step % N_STEPS) / N_STEPS
    start = sticky["start"]
    end = sticky["end"]

    config = model.zero_configuration()
    for joint in start:
        config[joint] = start[joint] + (end[joint] - start[joint]) * t

    scene_object.update(config)
    a = scene_object.draw_visual()
    sticky["step"] = step + 1

    update_component(ghenv, INTERVAL_MS)  # noqa: F821  (ghenv is injected by GhPython)
