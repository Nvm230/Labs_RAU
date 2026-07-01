import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
import matplotlib.pyplot as plt
import numpy as np

import tf2_ros
class TrackTruthPoseNode(Node):
    def __init__(self):
        # Declarar que usaremos el tiempo de simulación pasando el parámetro override
        super().__init__('track_truth_pose_node', parameter_overrides=[
            rclpy.parameter.Parameter('use_sim_time', rclpy.Parameter.Type.BOOL, True)
        ])
        
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )
        
        # TF2 listener para Ground Truth
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        self.state = 0
        self.target_distances = [1.5, 0.5, 1.5, 0.5]
        self.target_angles = [math.pi/2, math.pi/2, math.pi/2, math.pi/2]
        
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        
        self.start_x = 0.0
        self.start_y = 0.0
        self.start_yaw = 0.0
        
        self.is_first_odom = True
        self.state_initialized = False
        
        self.path_x = []
        self.path_y = []
        
        self.gt_path_x = []
        self.gt_path_y = []
        
        self.get_logger().info('Iniciando movimiento 3x2 con Ground Truth...')

    def euler_from_quaternion(self, x, y, z, w):
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        return math.atan2(t3, t4)

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        
        q = msg.pose.pose.orientation
        self.current_yaw = self.euler_from_quaternion(q.x, q.y, q.z, q.w)
        
        if self.is_first_odom:
            self.is_first_odom = False
            
        self.path_x.append(self.current_x)
        self.path_y.append(self.current_y)
        
        # Leer Ground Truth desde TF
        try:
            # Primero intentamos 'map' si existe (por ejemplo si hay SLAM/Nav2 corriendo)
            t = self.tf_buffer.lookup_transform('map', 'base_footprint', rclpy.time.Time())
            self.gt_path_x.append(t.transform.translation.x)
            self.gt_path_y.append(t.transform.translation.y)
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
            self.get_logger().warn(f"No se pudo usar 'map': {e}", throttle_duration_sec=2.0)
            try:
                # Fallback al frame 'odom' si 'map' no está disponible.
                t = self.tf_buffer.lookup_transform('odom', 'base_footprint', rclpy.time.Time())
                self.gt_path_x.append(t.transform.translation.x)
                self.gt_path_y.append(t.transform.translation.y)
            except Exception as e2:
                self.get_logger().warn(f"Fallback 'odom' falló: {e2}", throttle_duration_sec=2.0)

    def timer_callback(self):
        if self.is_first_odom:
            return
            
        if self.state >= 8:
            msg = Twist()
            self.publisher_.publish(msg)
            self.plot_path()
            return
            
        if not self.state_initialized:
            self.start_x = self.current_x
            self.start_y = self.current_y
            self.start_yaw = self.current_yaw
            self.state_initialized = True
            
        msg = Twist()
        
        is_moving_forward = (self.state % 2 == 0)
        
        if is_moving_forward:
            side_index = self.state // 2
            target_dist = self.target_distances[side_index]
            dist_moved = math.hypot(self.current_x - self.start_x, self.current_y - self.start_y)
            
            if dist_moved < target_dist:
                msg.linear.x = 0.6
            else:
                self.state += 1
                self.state_initialized = False
        else:
            angle_index = (self.state - 1) // 2
            target_angle = self.target_angles[angle_index]
            angle_moved = abs(self.current_yaw - self.start_yaw)
            
            if angle_moved > math.pi:
                angle_moved = 2 * math.pi - angle_moved
                
            if angle_moved < target_angle:
                msg.angular.z = 0.6
            else:
                self.state += 1
                self.state_initialized = False
                
        self.publisher_.publish(msg)

    def plot_path(self):
        self.get_logger().info('Movimiento finalizado. Generando gráfica con Ground Truth...')
        plt.figure(figsize=(10, 8))
        plt.plot(self.path_x, self.path_y, 'b-', label='Odometría')
        
        if len(self.gt_path_x) > 0:
            plt.plot(self.gt_path_x, self.gt_path_y, 'g--', label='Posición Verdadera (TF)')
            
        plt.title('Trayectoria del robot (Odometría vs Verdadera)')
        plt.xlabel('X (m)')
        plt.ylabel('Y (m)')
        plt.legend()
        plt.grid(True)
        plt.axis('equal')
        plt.savefig('trayectoria_odometria_vs_gt.png')
        self.get_logger().info('Gráfico guardado como trayectoria_odometria_vs_gt.png')
        plt.show()
        
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = TrackTruthPoseNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except rclpy.executors.ExternalShutdownException:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()
