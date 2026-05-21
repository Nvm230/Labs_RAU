#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('aubot_description')

    # Path to SDF model
    sdf_path = os.path.join(pkg_dir, 'models', 'aubot', 'model.sdf')

    # Launch configuration
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')

    return LaunchDescription([
        DeclareLaunchArgument('x_pose', default_value='0.0',
                              description='X position to spawn the robot'),
        DeclareLaunchArgument('y_pose', default_value='0.0',
                              description='Y position to spawn the robot'),

        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-entity', 'aubot',
                '-file', sdf_path,
                '-x', x_pose,
                '-y', y_pose,
                '-z', '0.01'
            ],
            output='screen',
        ),
    ])
