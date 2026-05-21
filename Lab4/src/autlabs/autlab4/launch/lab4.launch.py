import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_autlab4 = get_package_share_directory('autlab4')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    world_file = os.path.join(pkg_autlab4, 'worlds', 'mesa.world')
    urdf_file = os.path.join(pkg_autlab4, 'urdf', 'robot.urdf')

    # Parse URDF
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    # Start Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_file}.items()
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    # Spawn Robot
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'robot_depth', '-file', urdf_file, '-x', '0', '-y', '0', '-z', '0'],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity
    ])
