import bpy
from compas.scene import Scene

from compas_robots import RobotModel

model = RobotModel.ur5e(load_geometry=True)

N_FRAMES = 60
START_POSE = model.random_configuration()
END_POSE = model.random_configuration()

scene = Scene()
scene_object = scene.add(model)
visual_meshes = scene_object.draw_visual()

bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = N_FRAMES

for frame in range(1, N_FRAMES + 1):
    bpy.context.scene.frame_set(frame)
    t = (frame - 1) / (N_FRAMES - 1)
    config = model.zero_configuration()
    for joint in START_POSE:
        config[joint] = START_POSE[joint] + (END_POSE[joint] - START_POSE[joint]) * t
    scene_object.update(config)
    for mesh in visual_meshes:
        mesh.keyframe_insert(data_path="location")
        mesh.keyframe_insert(data_path="rotation_euler")

bpy.ops.screen.animation_play()
