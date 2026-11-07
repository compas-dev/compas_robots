import bpy
from compas.scene import Scene

from compas_robots import RobotModel

model = RobotModel.ur5e(load_geometry=True)

N_STEPS = 60
START_POSE = model.random_configuration()
END_POSE = model.random_configuration()

scene = Scene()
scene_object = scene.add(model)
scene_object.draw_visual()

state = {"step": 0}


def tick():
    if state["step"] > N_STEPS:
        return None  # returning None unregisters the timer
    t = state["step"] / N_STEPS
    config = model.zero_configuration()
    for joint in START_POSE:
        config[joint] = START_POSE[joint] + (END_POSE[joint] - START_POSE[joint]) * t
    scene_object.update(config)
    state["step"] += 1
    return 1 / 30  # call again in 1/30 s


bpy.app.timers.register(tick)
