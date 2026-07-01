import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = get_package_share_directory('lab7_kalman')
    config_file = os.path.join(pkg_dir, 'config', 'ukf_odom.yaml')

    return LaunchDescription([
        Node(
            package='robot_localization',
            executable='ukf_node',
            name='ukf_filter_node',
            output='screen',
            parameters=[config_file],
        )
    ])
