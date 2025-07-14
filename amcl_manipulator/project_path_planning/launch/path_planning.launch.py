import os
from launch_ros.actions import Node
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    
    nav2_yaml = os.path.join(get_package_share_directory('project_path_planning'), 'config', 'planner_server.yaml')
    controller_yaml = os.path.join(get_package_share_directory('project_path_planning'), 'config', 'controller.yaml')
    bt_navigator_yaml = os.path.join(get_package_share_directory('project_path_planning'), 'config', 'bt_navigator.yaml')
    bt_tree_xml = os.path.join(get_package_share_directory('project_path_planning'), 'config', 'behavior.xml')
    recovery_yaml = os.path.join(get_package_share_directory('project_path_planning'), 'config', 'recovery.yaml')

    planner_server = Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[nav2_yaml]
    )

    controller_server = Node(
            name='controller_server',
            package='nav2_controller',
            executable='controller_server',
            output='screen',
            parameters=[controller_yaml]
    )

    bt_navigator = Node (
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[bt_navigator_yaml, {'default_nav_to_pose_bt_xml': bt_tree_xml}] 
    )

    recoveries_server = Node (
            package='nav2_behaviors',
            executable='behavior_server',
            name='recoveries_server',
            parameters=[recovery_yaml],
            output='screen'
    )

    lifecycle_manager = Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{'use_sim_time': True},
                        {'autostart': True},
                        {'node_names': ['planner_server',
                                        'controller_server',
                                        'bt_navigator',
                                        'recoveries_server']}]
    )

    nav_to_pose = Node (
        package='project_path_planning',
        executable='nav_to_pose_client',
        name='nav_to_pose_client',
        output='screen',
    )

    corner_selector_node = Node (
        package='project_path_planning',
        executable='corner_selector_node',
        name='corner_selector_node',
        output='screen',
    )

    return LaunchDescription([
        planner_server,
        controller_server,
        bt_navigator,
        recoveries_server,
        nav_to_pose,
        corner_selector_node,

        lifecycle_manager,
    ])
