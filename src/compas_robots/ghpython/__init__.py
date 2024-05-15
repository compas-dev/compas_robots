import compas

if compas.RHINO:
    from .scene import (
        RobotModelObject,
    )
    
    __all__ = [
        "RobotModelObject",
    ]