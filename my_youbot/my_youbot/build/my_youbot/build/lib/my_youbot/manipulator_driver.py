import rclpy
import math

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


def arm_ik(x, y, z, manipulator):
  """Calculates and sets the joint angles for inverse kinematics."""
  y1 = math.sqrt(x**2 + y**2)
  z1 = z + arm_get_sub_arm_length('ARM4') + arm_get_sub_arm_length('ARM5') - arm_get_sub_arm_length('ARM1')

  a = arm_get_sub_arm_length('ARM2')
  b = arm_get_sub_arm_length('ARM3')
  c = math.sqrt(y1**2 + z1**2)

  alpha = -math.asin(x / y1)
  beta = -(math.pi / 2 - math.acos((a**2 + c**2 - b**2) / (2.0 * a * c)) - math.atan(z1 / y1))
  gamma = -(math.pi - math.acos((a**2 + b**2 - c**2) / (2.0 * a * b)))
  delta = -(math.pi + (beta + gamma))
  epsilon = math.pi / 2 + alpha

  manipulator.__arm1.setPosition(alpha)
  manipulator.__arm2.setPosition(beta)
  manipulator.__arm3.setPosition(gamma)
  manipulator.__arm4.setPosition(delta)
  manipulator.__arm5.setPosition(epsilon)


class ManipulatorDriver:
    def init(self, webots_node, properties):
        self.__robot = webots_node.robot

        self.__arm1 = self.__robot.getDevice('arm1')
        self.__arm2 = self.__robot.getDevice('arm2')
        self.__arm3 = self.__robot.getDevice('arm3')
        self.__arm4 = self.__robot.getDevice('arm4')
        self.__arm5 = self.__robot.getDevice('arm5')


        rclpy.init(args=None)
        self.__node = rclpy.create_node('manipulator_driver')

    def step(self):
        rclpy.spin_once(self.__node, timeout_sec=0)

        
        # Example usage
        x, y, z = 0.3, 0.2, 0.4
        arm_ik(x, y, z, self)
