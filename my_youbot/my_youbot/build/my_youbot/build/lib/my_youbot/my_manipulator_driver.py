import rclpy
from geometry_msgs.msg import Twist, Point
import math
from std_msgs.msg import String, Float32
from sensor_msgs.msg import Range
import numpy as np

Q = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

# Enum-like mapping in Python (using a dictionary)
arm_lengths = {
    'ARM1': 0.253,
    'ARM2': 0.155,
    'ARM3': 0.135,
    'ARM4': 0.081,
    'ARM5': 0.105,
}

def arm_get_sub_arm_length(arm):
    """Returns the length of a sub-arm.  Handles invalid arm names."""
    return arm_lengths.get(arm, 0.0) # Returns 0.0 if arm is not found


def arm_ik(x, y, z, Q):
    """Calculates and sets the joint angles for inverse kinematics."""
    y1 = math.sqrt(x**2 + y**2)
    z1 = z + arm_get_sub_arm_length('ARM4') + arm_get_sub_arm_length('ARM5') - arm_get_sub_arm_length('ARM1')

    a = arm_get_sub_arm_length('ARM2')
    b = arm_get_sub_arm_length('ARM3')
    c = math.sqrt(y1**2 + z1**2)

    if abs(x / y1) > 1:
        raise ValueError("Значение x/y1 выходит за пределы допустимого диапазона для asin")

    # Проверка на допустимые значения для acos
    acos_arg = (a**2 + c**2 - b**2) / (2.0 * a * c)
    if not -1 <= acos_arg <= 1:
        raise ValueError(f"{acos_arg} Значение аргумента acos выходит за пределы допустимого диапазона")

    acos_arg_gamma = (a**2 + b**2 - c**2) / (2.0 * a * b)
    if not -1 <= acos_arg_gamma <= 1:
        raise ValueError(f"{acos_arg_gamma}Значение аргумента acos для gamma выходит за пределы допустимого диапазона")

    Q[1] = -math.asin(x / y1)
    Q[2] = -(math.pi / 2 - math.acos((a**2 + c**2 - b**2) / (2.0 * a * c)) - math.atan(z1 / y1))
    Q[3] = -(math.pi - math.acos((a**2 + b**2 - c**2) / (2.0 * a * b)))
    Q[4] = -(math.pi + (Q[2] + Q[3]))
    Q[5] = math.pi / 2 + Q[1]

class MyManipulatorDriver:
    def init(self, webots_node, properties):
        self.__robot = webots_node.robot

        self.__arm1 = self.__robot.getDevice('arm1')
        self.__arm2 = self.__robot.getDevice('arm2')
        self.__arm3 = self.__robot.getDevice('arm3')
        self.__arm4 = self.__robot.getDevice('arm4')
        self.__arm5 = self.__robot.getDevice('arm5')

        self.__point = Point()

        rclpy.init(args=None)
        self.__node = rclpy.create_node('my_manipulator_driver')
        self.__node.create_subscription(Point, 'xyz', self.__xyz_callback, 1)
        
        self.__node.create_subscription(Float32, 'rot_err', self.__rot_err__callback, 1)

    def __xyz_callback(self, point):
        self.__point = point
        if self.__point.x != 0.0 and self.__point.y != 0.0 and self.__point.z != 0.0:
            arm_ik(self.__point.x, self.__point.y, self.__point.z, Q)

    def step(self):
        rclpy.spin_once(self.__node, timeout_sec=0)

        self.__arm1.setPosition(Q[1])
        self.__arm2.setPosition(Q[2])
        self.__arm3.setPosition(Q[3])
        self.__arm4.setPosition(Q[4])
        self.__arm5.setPosition(0)