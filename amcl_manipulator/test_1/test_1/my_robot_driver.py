import rclpy
from geometry_msgs.msg import Twist, TransformStamped, Point
from nav_msgs.msg import Odometry
from rclpy.time import Time
from tf2_ros import TransformBroadcaster
from transforms3d.euler import euler2quat
import numpy as np
import math

from std_msgs.msg import String

WHEEL_RADIUS = 0.05
LX = 0.228
LY = 0.158
L = 2 * LY  # Геометрический параметр для разворота

Q = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

LEFT = 0
RIGHT = 1

MIN_POS = 0.0
MAX_POS = 0.025
OFFSET_WHEN_LOCKED = 0.021

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
        raise ValueError(f"{acos_arg} Значение аргумента acos выходит за пределы допустимого диапазона, x: {x}, y: {y}, z:{z}")

    acos_arg_gamma = (a**2 + b**2 - c**2) / (2.0 * a * b)
    if not -1 <= acos_arg_gamma <= 1:
        raise ValueError(f"{acos_arg_gamma}Значение аргумента acos для gamma выходит за пределы допустимого диапазона")

    Q[1] = -math.asin(x / y1)
    Q[2] = -(math.pi / 2 - math.acos((a**2 + c**2 - b**2) / (2.0 * a * c)) - math.atan(z1 / y1))
    Q[3] = -(math.pi - math.acos((a**2 + b**2 - c**2) / (2.0 * a * b)))
    Q[4] = -(math.pi + (Q[2] + Q[3]))
    Q[5] = math.pi / 2 + Q[1]


class MyRobotDriver:
    def init(self, webots_node, properties):
        # ROS 2
        rclpy.init(args=None)
        self.node = rclpy.create_node('my_robot_driver')
        self.node.create_subscription(Twist, 'cmd_vel', self.__cmd_vel_callback, 1)
        self.odom_pub = self.node.create_publisher(Odometry, 'odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self.node)

        self.__robot = webots_node.robot
        self.timestep = int(self.__robot.getBasicTimeStep())

        self.__arm1 = self.__robot.getDevice('arm1')
        self.__arm2 = self.__robot.getDevice('arm2')
        self.__arm3 = self.__robot.getDevice('arm3')
        self.__arm4 = self.__robot.getDevice('arm4')
        self.__arm5 = self.__robot.getDevice('arm5')

        self.__gripper = self.__robot.getDevice('finger::left')
        self.__gripper.setVelocity(0.03)
        self.__end_effector = ""

        self.node.create_subscription(String, 'end_effector', self.__end_effector_callback, 1)
        self.node.create_subscription(Point, 'xyz', self.__xyz_callback, 1)

        # Моторы
        self.motor_fl = self.__robot.getDevice('wheel2')  # Front Left
        self.motor_fr = self.__robot.getDevice('wheel1')  # Front Right
        self.motor_rl = self.__robot.getDevice('wheel4')  # Rear Left
        self.motor_rr = self.__robot.getDevice('wheel3')  # Rear Right

        for motor in [self.motor_fl, self.motor_fr, self.motor_rl, self.motor_rr]:
            motor.setPosition(float('inf'))
            motor.setVelocity(0.0)

        # Энкодеры
        self.encoder_fl = self.__robot.getDevice('wheel2sensor')
        self.encoder_fr = self.__robot.getDevice('wheel1sensor')
        self.encoder_rl = self.__robot.getDevice('wheel4sensor')
        self.encoder_rr = self.__robot.getDevice('wheel3sensor')

        for encoder in [self.encoder_fl, self.encoder_fr, self.encoder_rl, self.encoder_rr]:
            encoder.enable(self.timestep)

        self.prev_enc = [0.0, 0.0, 0.0, 0.0]

        

        self.cmd_vel = Twist()
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0
        self.last_time = self.__robot.getTime()

        self.theta = 0.0

        self.S = 0

        # Последняя временная метка для проверки перескоков времени
        self.last_stamp = None

    def __cmd_vel_callback(self, msg):
        self.cmd_vel = msg

    def __end_effector_callback(self, string):
        self.__end_effector = string.data

    def __xyz_callback(self, point):
        self.__point = point
        if self.__point.x != 0.0 and self.__point.y != 0.0 and self.__point.z != 0.0:
            arm_ik(self.__point.x, self.__point.y, self.__point.z, Q)

    def publish_rotating_wheel_tf(self, parent, child, x, y, z, angle_rad, now):
        t = TransformStamped()
        t.header.stamp = now
        t.header.frame_id = parent
        t.child_frame_id = child
        t.transform.translation.x = x
        t.transform.translation.y = y
        t.transform.translation.z = z

        qw, qx, qy, qz = euler2quat(0, angle_rad, 0)
        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw

        self.tf_broadcaster.sendTransform(t)

    def step(self):
        rclpy.spin_once(self.node, timeout_sec=0)

        # Управление
        vx = self.cmd_vel.linear.x
        wz = self.cmd_vel.angular.z

        # Дифференциальное управление
        left_speed = (vx - wz * L / 2) / WHEEL_RADIUS
        right_speed = (vx + wz * L / 2) / WHEEL_RADIUS

        self.motor_fl.setVelocity(left_speed)
        self.motor_rl.setVelocity(left_speed)
        self.motor_fr.setVelocity(right_speed)
        self.motor_rr.setVelocity(right_speed)

        # Одометрия
        enc = [
            self.encoder_fr.getValue(),
            self.encoder_fl.getValue(),
            self.encoder_rr.getValue(),
            self.encoder_rl.getValue()
        ]

        delta = [enc[i] - self.prev_enc[i] for i in range(4)]
        self.prev_enc = enc.copy()

        # Перевод в метры
        d_fr = delta[0] * WHEEL_RADIUS
        d_fl = delta[1] * WHEEL_RADIUS
        d_rr = delta[2] * WHEEL_RADIUS
        d_rl = delta[3] * WHEEL_RADIUS

        d_left = (d_fl + d_rl) / 2.0
        d_right = (d_fr + d_rr) / 2.0
        K_th = 2.6489
        K_f = 1.0102
        d_forward = (d_left + d_right) / (2.0 * K_f)
        d_theta = (d_right - d_left) / (K_th * L)
        dt = self.timestep / 1000

        self.th += d_theta
        self.x += d_forward * np.cos(self.th)
        self.y += d_forward * np.sin(self.th)

        # Получаем текущее время
        now = self.node.get_clock().now().to_msg()

        # Проверка и коррекция времени (обеспечиваем монотонный рост)
        if self.last_stamp is not None:
            # Если новое время меньше или равно предыдущему — увеличиваем
            if (now.sec < self.last_stamp.sec) or (now.sec == self.last_stamp.sec and now.nanosec <= self.last_stamp.nanosec):
                # Коррекция на +1 миллисекунду (1_000_000 наносекунд)
                new_sec = self.last_stamp.sec
                new_nanosec = self.last_stamp.nanosec + 1_000_000
                if new_nanosec >= 1_000_000_000:
                    new_sec += 1
                    new_nanosec -= 1_000_000_000
                now.sec = new_sec
                now.nanosec = new_nanosec

        self.last_stamp = now

        # Публикация одометрии
        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'

        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0

        qw, qx, qy, qz = euler2quat(0, 0, self.th)
        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw

        odom.twist.twist.linear.x = d_forward / dt if dt > 0 else 0.0
        odom.twist.twist.angular.z = d_theta / dt if dt > 0 else 0.0

        self.odom_pub.publish(odom)

        # TF трансформация
        t = TransformStamped()
        t.header.stamp = now
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw

        self.tf_broadcaster.sendTransform(t)

        self.publish_rotating_wheel_tf("base_link", "wheel_front_left",  0.228,  0.158, -0.055, self.encoder_fl.getValue(), now)
        self.publish_rotating_wheel_tf("base_link", "wheel_front_right", 0.228, -0.158, -0.055, self.encoder_fr.getValue(), now)
        self.publish_rotating_wheel_tf("base_link", "wheel_rear_left",  -0.228,  0.158, -0.055, self.encoder_rl.getValue(), now)
        self.publish_rotating_wheel_tf("base_link", "wheel_rear_right", -0.228, -0.158, -0.055, self.encoder_rr.getValue(), now)

        self.__arm1.setPosition(Q[1])
        self.__arm2.setPosition(Q[2])
        self.__arm3.setPosition(Q[3])
        self.__arm4.setPosition(Q[4])
        self.__arm5.setPosition(0)

        if self.__end_effector == "open":
            self.__gripper.setPosition(MAX_POS)

        if self.__end_effector == "close":
            self.__gripper.setPosition(MIN_POS)

        if self.__end_effector == "cube":
            self.__gripper.setPosition((0.05-OFFSET_WHEN_LOCKED-0.001)/2)
