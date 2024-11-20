from compas_fab.robots import RobotCellLibrary

rc, rcs = RobotCellLibrary.ur10e()
model = rc.robot_model
for link in model.iter_links():
    print(link.name)
    print(model.get_link_visual_meshes(link))
    print(model.get_link_collision_meshes(link))
    print(model.get_link_visual_meshes_joined(link))
    print(model.get_link_collision_meshes_joined(link))
    print("---------------------")
