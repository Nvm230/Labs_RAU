# simulation_with_amcl.launch.py
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    # Configuración
    pkg_gazebo_ros = FindPackageShare('gazebo_ros')
    pkg_nav2_bringup = FindPackageShare('nav2_bringup')
    
    # Ruta al mundo de Gazebo
    world_path = PathJoinSubstitution([
        FindPackageShare('turtlebot3_gazebo'),  # Reemplaza con tu paquete
        'worlds',
        'empty_world.world'  # Reemplaza con tu mundo
    ])
    
    return LaunchDescription([
        # 1. Iniciar Gazebo
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
            ),
            launch_arguments={'world': world_path}.items()
        ),
        
        # 2. Publicar el mapa (necesario para AMCL)
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'yaml_filename': 'mapa.yaml'  # Necesitas un mapa
            }]
        ),
        
        # 3. AMCL (localización)
        Node(
            package='amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'odom_frame_id': 'odom',
                'map_frame_id': 'map',
                'base_frame_id': 'base_footprint',
                'global_frame_id': 'map',
                # Parámetros de AMCL
                'min_particles': 100,
                'max_particles': 2000,
                'kld_err': 0.01,
                'kld_z': 0.99,
                'update_min_d': 0.2,
                'update_min_a': 0.2,
                'resample_interval': 1,
                'transform_tolerance': 1.0,
                'recovery_alpha_slow': 0.0,
                'recovery_alpha_fast': 0.0,
                'initial_pose_x': 0.0,  # Posición inicial en el mapa
                'initial_pose_y': 0.0,
                'initial_pose_a': 0.0,
            }]
        ),
        
        # 4. Lifecycle Manager para AMCL
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'autostart': True,
                'node_names': ['map_server', 'amcl']
            }]
        ),
    ])