from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseWithCovarianceStamped

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from std_msgs.msg import String


class NavToPoseActionClient(Node):

    def __init__(self):
        super().__init__('move_to_spot')
        self._action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')

        # Подписка на топик "goal_point"
        self.subscription = self.create_subscription(
            PoseWithCovarianceStamped,
            'goal_point',
            self.pose_callback,
            10
        )
        
        self.goal_publisher = self.create_publisher(String, 'goal_success', 1)

        self.get_logger().info("NavToPoseActionClient initialized and subscribed to 'clicked_point'")

    def pose_callback(self, msg: PoseWithCovarianceStamped):
        self.get_logger().info("Received goal from 'clicked_point'")

        goal_pose = NavigateToPose.Goal()
        goal_pose.pose.header.frame_id = 'map'
        goal_pose.pose.header.stamp = self.get_clock().now().to_msg()

        # Копирование позиции
        goal_pose.pose.pose.position.x = msg.pose.pose.position.x
        goal_pose.pose.pose.position.y = msg.pose.pose.position.y
        goal_pose.pose.pose.position.z = 0.0

        # Копирование ориентации
        goal_pose.pose.pose.orientation.x = 0.0
        goal_pose.pose.pose.orientation.y = 0.0
        goal_pose.pose.pose.orientation.z = msg.pose.pose.orientation.z
        goal_pose.pose.pose.orientation.w = msg.pose.pose.orientation.w

        self.send_goal(goal_pose)

    def send_goal(self, goal_pose):
        self.get_logger().info("Sending goal to NavigateToPose...")

        self._action_client.wait_for_server()

        self._send_goal_future = self._action_client.send_goal_async(
            goal_pose,
            feedback_callback=self.feedback_callback)

        self.get_logger().info(f"Goal being sent: x={goal_pose.pose.pose.position.x}, y={goal_pose.pose.pose.position.y}")

        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return
            
        self.get_logger().info('Goal accepted :)')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        status = future.result().status
        
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Navigation succeeded!')
            goal_pub = String()
            goal_pub.data = "GOAL SUCCESS"
            self.goal_publisher.publish(goal_pub)
        else:
            self.get_logger().info(f'Navigation failed with status: {status}')

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        # Вывод можно настроить при необходимости


def main(args=None):
    rclpy.init(args=args)

    action_client = NavToPoseActionClient()

    rclpy.spin(action_client)

    action_client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()