import os
import launch
from launch_ros.actions import Node
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from webots_ros2_driver.webots_launcher import WebotsLauncher
from webots_ros2_driver.webots_controller import WebotsController


def generate_launch_description():
    package_dir = get_package_share_directory('test_1')
    robot_description_path = os.path.join(package_dir, 'resource', 'my_robot.urdf')

    

    webots = WebotsLauncher(
        world=os.path.join(package_dir, 'worlds', 'my_world_new.wbt')
    )

    my_robot_driver = WebotsController(
        robot_name='my_robot',
        parameters=[
            {'robot_description': robot_description_path},
        ]
    )

    smach = Node(
        package='test_1',
        executable='smach',
    )

    #slam_toolbox_node = Node(
    #   package='slam_toolbox',
    #    executable='sync_slam_toolbox_node',
    #    name='slam_toolbox',
    #    parameters=[{'use_sim_time': True}],
    #    remappings=[
    #        ('scan', '/scan')  # ничего не переназначаем, используем стандарт
    #    ]
    #)

    pointcloud_to_laserscan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan_node',
        parameters=[os.path.join(package_dir, 'config', 'pointcloud_to_laserscan_params.yaml')],
        remappings=[
            ('cloud_in', '/my_robot/lidar/point_cloud'),  # вход из Webots
            ('scan', '/scan')  # выход для SLAM
        ]
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': open(robot_description_path).read()}]
    )

    #clock= Node(
    #    package='test_1',
    #    executable='clock_publisher',
    #)

    camera_node= Node(
        package='test_1',
        executable='camera_node',
    )


    return LaunchDescription([
        webots,
        my_robot_driver,
    #    slam_toolbox_node,
        pointcloud_to_laserscan_node,
        robot_state_publisher,
    #    clock,
        smach,
        camera_node,
 
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=webots,
                on_exit=[launch.actions.EmitEvent(event=launch.events.Shutdown())],
            )
        )
    ])
