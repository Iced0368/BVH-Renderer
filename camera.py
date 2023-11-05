import glm
import numpy as np


def adjust_angle(angle):
    while angle <= -180:
        angle += 360
    while angle > 180:
        angle -= 360
    return angle

def auto_property(name):
    @property
    def prop(self):
        attr_name = f'_{self.__class__.__name__}__{name}'
        return getattr(self, attr_name)

    @prop.setter
    def prop(self, value):
        attr_name = f'_{self.__class__.__name__}__{name}'
        if value == getattr(self, attr_name):
            return
        if self.controller is not None:
            self.controller.factors[name].setValue(value)
        setattr(self, attr_name, value)
        self.update()

    return prop

class Camera:
    def __init__(self):
        self.__target_x = 0
        self.__target_y = 0
        self.__target_z = 0
        self.__azimuth = 0.1
        self.__elevation = 1.2
        self.__distance = 4

        self.isPerspective = True
        self.target = glm.vec3(0, 0, 0)
        self.controller = None
        self.update()

    target_x = auto_property("target_x")
    target_y = auto_property("target_y")
    target_z = auto_property("target_z")
    azimuth = auto_property("azimuth")
    elevation = auto_property("elevation")
    distance = auto_property("distance")

    def update(self):
        self.target = glm.vec3(self.target_x, self.target_y, self.target_z)
        self.up = glm.vec3(0, 1 if self.elevation > 0 else -1, 0)

        # Eye position
        R = glm.rotate(np.deg2rad(self.azimuth), glm.vec3(0, 1, 0)) * glm.rotate(np.deg2rad(self.elevation), glm.vec3(0, 0, 1))
        T = glm.translate(self.target)
        S = glm.scale(self.distance*glm.vec3(1, 1, 1))
        self.eye = T * R * S * glm.vec3(0, 1, 0)

        # Camera frame
        self.w = glm.normalize(self.eye-self.target) 
        self.u = glm.normalize(glm.cross(self.up, self.w))
        self.v = glm.normalize(glm.cross(self.w, self.u))

    def orbit(self, da, de):
        self.azimuth = adjust_angle(self.azimuth + da)
        self.elevation = adjust_angle(self.elevation - de)

    def pan(self, horizontal, vertical):
        dpos = horizontal * self.u + vertical * self.v
        self.target += self.distance * dpos
        self.eye += self.distance * dpos

        self.target_x, self.target_y, self.target_z = self.target

    def zoom(self, offset):
        self.distance *= 1.1**-offset

    def projectionMatrix(self):
        return glm.perspective(45, 1, 1, -1) if self.isPerspective else glm.ortho(*list(self.distance*np.array([-0.5, 0.5, -0.5, 0.5, -5, 5])))
