import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from project_localization_interfaces.srv import MyServiceMessage
import os
from ament_index_python.packages import get_package_share_directory
from pathlib import Path

class SpotRecorder(Node):

    def __init__(self):
        super().__init__('spot_recorder')
        self.spots = {}
        self.current_pose = None

        # Подписка на /amcl_pose
        self.subscriber = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.pose_callback,
            10
        )

        # Сервис /save_spot
        self.srv = self.create_service(
            MyServiceMessage,
            '/save_spot',
            self.save_spot_callback
        )

        self.get_logger().info('SpotRecorder node is ready.')

        # Путь к config/ внутри пакета
        #package_share_directory = get_package_share_directory('project_localization')
        #self.config_path = os.path.join(package_share_directory, 'config', 'spots.txt')
        self.config_path = str(Path.home() / 'ros2_ws' / 'src' / 'project_localization' / 'config' / 'spots.txt')
        
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

    def pose_callback(self, msg):
        self.current_pose = msg.pose.pose

    def save_spot_callback(self, request, response):
        label = request.label

        if label == "end":
            try:
                with open(self.config_path, "w") as f:
                    for name, pose in self.spots.items():
                        f.write(f"{name}:\n")
                        f.write(f"  position:\n")
                        f.write(f"    x: {pose.position.x}\n")
                        f.write(f"    y: {pose.position.y}\n")
                        f.write(f"  orientation:\n")
                        f.write(f"    z: {pose.orientation.z}\n")
                        f.write(f"    w: {pose.orientation.w}\n")
                response.navigation_successfull = True
                response.message = f"File saved to {self.config_path}"
                self.get_logger().info(response.message)
            except Exception as e:
                response.navigation_successfull = False
                response.message = f"Failed to write file: {str(e)}"
        else:
            if self.current_pose:
                self.spots[label] = self.current_pose
                response.navigation_successfull = True
                response.message = f"Spot '{label}' saved."
                self.get_logger().info(response.message)
            else:
                response.navigation_successfull = False
                response.message = "Current pose not available yet."

        return response

def main(args=None):
    rclpy.init(args=args)
    node = SpotRecorder()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
