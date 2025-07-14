#!/usr/bin/env python
import rclpy
import math
import time
from rclpy.node import Node
from sensor_msgs.msg import Range
from std_msgs.msg import String, Int32
from geometry_msgs.msg import Point
MAX_RANGE = 0.1
import math

import sys
sys.path.insert(0, '/home/vadim/ros2_ws/src/executive_smach/smach')
import smach

sys.path.insert(0, '/home/vadim/ros2_ws/src/executive_smach/smach_ros')
import smach_ros

class Smach(Node):
    def __init__(self):
        super().__init__('smach')

        self.publisher_xyz = self.create_publisher(Point, 'xyz', 1)
        self.publisher_ee = self.create_publisher(String, 'end_effector', 1)
        

        self.create_subscription(Int32, 'start_status', self.start_status_callback, 1)
        self.start_status = None

        self.number_goal = 1
        self.number_goal_previous = self.number_goal

        self.goal_publisher = self.create_publisher(String, 'corner', 10)
        self.goal = String()

        self.create_subscription(String, 'goal_success', self.goal_success_callback, 1)
        self.goal_success = ""

        self.camera_on_publisher = self.create_publisher(Int32, 'camera_on', 10)
        
        self.create_subscription(Int32, 'wait_camera', self.wait_camera_callback, 1)
        self.wait_camera_value = None
        self.need_colour = String()
        
        self.publisher_need_colour = self.create_publisher(String, 'need_colour', 1)

        self.create_subscription(Int32, 'xyz_send', self.xyz_send_callback, 1)
        self.xyz_send_value = None


        self.left_sensor_value_ = None
        self.right_sensor_value_ = None
        self.colour_red = None
        self.colour_green = None
        self.feedback_ = None
        

        self.xz_cube_ = Point()
        self.xyz_Point = Point()

    def start_status_callback(self, int32):
        self.start_status = int32.data

    def goal_success_callback(self, string):
        self.goal_success = string.data

    def wait_camera_callback(self, int32):
        self.wait_camera_value = int32.data

    def xyz_send_callback(self, int32):
        self.xyz_send_value = int32.data


    def home_position(self):
        self.xyz_Point.x = -0.08
        self.xyz_Point.y = 0.08
        self.xyz_Point.z = 0.25
        self.publisher_xyz.publish(self.xyz_Point)

    def end_effector(self, status):
        end_effector = String()
        if status == 0:
            end_effector.data = "open"
        elif status == 1:
            end_effector.data = "close"
        elif status == 0.5:
            end_effector.data = "cube"
        self.publisher_ee.publish(end_effector)

    def take(self):
        self.xyz_Point.x = self.xz_cube_.x

        while self.left_sensor_value_ is None:
            rclpy.spin_once(self, timeout_sec=0.1)

        if self.need_colour.data == "GREEN":
            a = float(self.left_sensor_value_) - 0.25 + 0.1 + 0.03
        elif self.need_colour.data == "RED":
            a = float(self.left_sensor_value_) + 0.1 + 0.03
        b = float(self.xz_cube_.x)
        self.xyz_Point.y = math.sqrt(abs(a)**2 - abs(b)**2)

        self.xyz_Point.z = self.xz_cube_.z

        self.publisher_xyz.publish(self.xyz_Point)
        

class START(smach.State):
    def __init__(self, node):
        super().__init__(outcomes=['START', 'WAIT'])
        self.node = node

    def execute(self, userdata):
        while self.node.start_status is None:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        if self.node.start_status == 1:
            self.node.home_position()
            self.node.end_effector(0)
            self.node.start_status = None
            return 'START'
        else:
            self.node.start_status = None           
            return 'WAIT'
        
class GO(smach.State):
    def __init__(self, node):
        super().__init__(outcomes=['corner1', 'corner2', 'WAIT', 'corner3', 'corner4'])
        self.node = node
        self.topic1_sent = False
        self.topic2_sent = False
        self.topic3_sent = False
        self.topic4_sent = False

    def execute(self, userdata):
        if self.node.number_goal == 1:
            if not self.topic1_sent:
                self.node.goal.data = "corner1"
                self.node.goal_publisher.publish(self.node.goal)
                self.topic1_sent = True
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if self.node.goal_success == "GOAL SUCCESS":
                self.node.goal_success = None
                self.node.number_goal = self.node.number_goal +1
                return 'corner1'
            else:
                return 'WAIT'
            
        if self.node.number_goal == 2:
            if not self.topic2_sent:
                self.node.goal.data = "corner2"
                self.node.goal_publisher.publish(self.node.goal)
                self.topic2_sent = True
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if self.node.goal_success == "GOAL SUCCESS":
                self.node.goal_success = None
                self.node.number_goal = self.node.number_goal +1
                return 'corner2'
            else:
                return 'WAIT'
            
        if self.node.number_goal == 3:
            if not self.topic3_sent:
                self.node.goal.data = "corner3"
                self.node.goal_publisher.publish(self.node.goal)
                self.topic3_sent = True
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if self.node.goal_success == "GOAL SUCCESS":
                self.node.goal_success = None
                self.node.number_goal = self.node.number_goal +1
                return 'corner3'
            else:
                return 'WAIT'
            
        if self.node.number_goal == 4:
            if not self.topic4_sent:
                self.node.goal.data = "corner4"
                self.node.goal_publisher.publish(self.node.goal)
                self.topic4_sent = True
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if self.node.goal_success == "GOAL SUCCESS":
                self.node.goal_success = None
                self.node.number_goal = self.node.number_goal +1
                return 'corner4'
            else:
                return 'WAIT'

            
class CAMERA_ON(smach.State):
    def __init__(self, node):
        super().__init__(outcomes=['WAIT', 'NEXT_FIXED', 'NEXT_UNFIXED'])
        self.node = node
        self.topic_sent = False
        self.entry_count = 0

    def execute(self, userdata):
        flag_on = Int32()
        flag_on.data = 1
        self.node.camera_on_publisher.publish(flag_on)
        rclpy.spin_once(self.node, timeout_sec=0.1)
        if self.node.wait_camera_value == 1:
            if not self.topic_sent:
                if self.entry_count == 0:
                    self.node.need_colour.data = "GREEN"
                    #self.node.get_logger().info("CAMERA_ON: Ищу ЗЕЛЁНЫЙ объект.")
                else:
                    self.node.need_colour.data = "WHITE"
                    #self.node.get_logger().info("CAMERA_ON: Ищу БЕЛЫЙ объект.")

                self.node.publisher_need_colour.publish(self.node.need_colour)
                self.topic_sent = True
            time.sleep(1)
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if self.node.xyz_send_value == 1:
                self.node.xyz_send_value = None
                self.topic_sent = False
                self.entry_count +=1
                if self.node.need_colour.data == "GREEN":
                    return 'NEXT_FIXED' 
                else:
                    return 'NEXT_UNFIXED'
            else:
                return 'WAIT'
        else:
            self.node.get_logger().info("WWWWWWWWWWAAAAAAAAAIIIIIIITTTTTTTTTT")
            return 'WAIT'
        
class FIXED(smach.State):
    def __init__(self, node):
        super().__init__(outcomes=['NEXT'])
        self.node = node

    def execute(self, userdata):
        self.node.end_effector(0.5)
        time.sleep(1)
        return 'NEXT'
    
class UNFIXED(smach.State):
    def __init__(self, node):
        super().__init__(outcomes=['NEXT'])
        self.node = node
        self.xyz_Point = Point()

    def execute(self, userdata):
        time.sleep(1)
        self.node.end_effector(0)
        time.sleep(1)
        
        self.xyz_Point.x = -0.045
        self.xyz_Point.y = 0.17
        self.xyz_Point.z = 0.25
        self.node.publisher_xyz.publish(self.xyz_Point)
        time.sleep(1)
        return 'NEXT'
    
class HOME_POSITION(smach.State):
    def __init__(self, node):
        super().__init__(outcomes=['NEXT_CAMERA_ON', 'NEXT_CAMERA_OFF'])
        self.node = node
        self.entry_count = 0

    def execute(self, userdata):
        self.node.home_position()
        time.sleep(1)
        if self.entry_count == 0:
            self.entry_count += 1
            return 'NEXT_CAMERA_ON'
        else:
            return 'NEXT_CAMERA_OFF'
        
class CAMERA_OFF(smach.State):
    def __init__(self, node):
        super().__init__(outcomes=['NEXT'])
        self.node = node
        self.topic_sent = False
        self.entry_count = 0

    def execute(self, userdata):
        
        return 'NEXT'


def main(args=None):
    rclpy.init(args=args)
    node = Smach()
    sm = smach.StateMachine(outcomes=['END', 'outcome5'])
    with sm:
        smach.StateMachine.add('START', START(node), 
                            transitions={'START':'GO',
                                         'WAIT':'START'})
        smach.StateMachine.add('GO', GO(node), 
                            transitions={'corner1':'GO',
                                         'corner2':'CAMERA_ON',
                                         'WAIT':'GO',
                                         'corner3':'GO',
                                         'corner4':'END'})
        smach.StateMachine.add('CAMERA_ON', CAMERA_ON(node), 
                            transitions={'WAIT':'CAMERA_ON',
                                         'NEXT_FIXED':'FIXED',
                                         'NEXT_UNFIXED':'UNFIXED'})
        smach.StateMachine.add('FIXED', FIXED(node), 
                            transitions={'NEXT':'HOME_POSITION'})
        smach.StateMachine.add('HOME_POSITION', HOME_POSITION(node), 
                            transitions={'NEXT_CAMERA_ON':'CAMERA_ON',
                                         'NEXT_CAMERA_OFF':'CAMERA_OFF'})
        smach.StateMachine.add('UNFIXED', UNFIXED(node), 
                            transitions={'NEXT':'HOME_POSITION'})
        smach.StateMachine.add('CAMERA_OFF', CAMERA_OFF(node), 
                            transitions={'NEXT':'GO'})

    outcome = sm.execute()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
