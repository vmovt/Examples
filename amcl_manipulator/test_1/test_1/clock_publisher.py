# clock_publisher_node.py

import rclpy
from rclpy.node import Node
from rosgraph_msgs.msg import Clock

class ClockPublisher(Node):
    def __init__(self):
        super().__init__('clock_publisher')
        self.clock_pub = self.create_publisher(Clock, '/clock', 10)
        self.timer = self.create_timer(0.01, self.timer_callback)
        self.current_time = self.get_clock().now()

    def timer_callback(self):
        msg = Clock()
        msg.clock = self.get_clock().now().to_msg()
        self.clock_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ClockPublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
