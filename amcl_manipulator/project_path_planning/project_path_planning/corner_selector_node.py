import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import PoseWithCovarianceStamped, Pose, Quaternion, Point

import os
from ament_index_python.packages import get_package_share_directory
import yaml


class CornerPublisher(Node):

    def __init__(self):
        super().__init__('corner_publisher')

        # Путь к YAML-файлу с координатами
        self.spot_file_path = os.path.join(get_package_share_directory('project_path_planning'), 'config', 'spots.yaml')
        
        # Словарь для хранения точек
        self.corners = self.load_spots()

        # Подписка на топик с именами углов
        self.subscription = self.create_subscription(
            String,
            'corner',
            self.corner_callback,
            10
        )

        # Публикация в топик goal_point
        self.publisher = self.create_publisher(
            PoseWithCovarianceStamped,
            'goal_point',
            10
        )

        self.get_logger().info("CornerPublisher initialized and listening to 'corner' topic")

    def load_spots(self):
        """Загружает координаты углов из YAML-файла"""
        if not os.path.exists(self.spot_file_path):
            self.get_logger().error(f"File '{self.spot_file_path}' not found")
            return {}

        with open(self.spot_file_path, 'r') as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                self.get_logger().error(f"YAML parsing error: {e}")
                return {}

    def corner_callback(self, msg: String):
        corner_name = msg.data.strip()
        self.get_logger().info(f"Received request for: {corner_name}")

        if corner_name not in self.corners:
            self.get_logger().warn(f"Corner '{corner_name}' not found in spots file.")
            return

        pose_msg = PoseWithCovarianceStamped()
        pose_msg.header.frame_id = 'map'
        pose_msg.header.stamp = self.get_clock().now().to_msg()

        pos = self.corners[corner_name]['position']
        orient = self.corners[corner_name]['orientation']

        pose_msg.pose.pose.position = Point(x=pos['x'], y=pos['y'], z=0.0)
        pose_msg.pose.pose.orientation = Quaternion(x=0.0, y=0.0, z=orient['z'], w=orient['w'])

        self.publisher.publish(pose_msg)
        self.get_logger().info(f"Published pose for {corner_name} to 'goal_point'")


def main(args=None):
    rclpy.init(args=args)
    node = CornerPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
