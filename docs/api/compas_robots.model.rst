********************************************************************************
compas_robots.model
********************************************************************************

.. currentmodule:: compas_robots.model

.. rst-class:: lead

This package provides classes for describing robots, their components, and their kinematic behaviour.


Model
=====

A robot model consists of a set of link elements, and a set of joint
elements connecting the links together.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Joint
    Link


Geometric description
=====================

The robot itself as well as its links can be geometrically described
using the following classes.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Geometry
    MeshDescriptor
    Material
    Texture


Link
====

The link is described as a rigid body with inertial, visual and collision values.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Visual
    Collision
    Inertial
    Mass
    Inertia


Joint
=====

The joint describes the kinematics and dynamics of the robot's joint.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    ParentLink
    ChildLink
    Calibration
    Dynamics
    Limit
    Axis
    Mimic
    SafetyController
