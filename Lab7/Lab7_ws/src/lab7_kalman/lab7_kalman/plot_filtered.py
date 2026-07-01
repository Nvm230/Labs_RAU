import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
import matplotlib.pyplot as plt
import tf2_ros

class PlotFilteredNode(Node):
    def __init__(self):
        super().__init__('plot_filtered_node')
        
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Subscripciones
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.filtered_sub = self.create_subscription(Odometry, '/odometry/filtered', self.filtered_callback, 10)
        
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
        
        # Listas para almacenar trayectorias
        self.path_x = []
        self.path_y = []
        
        self.gt_path_x = []
        self.gt_path_y = []
        
        self.filtered_path_x = []
        self.filtered_path_y = []
        
        self.get_logger().info('Iniciando nodo para graficar Odometría, Ground Truth y Filtro (EKF/UKF)...')

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
        
        # Ground Truth vía TF
        try:
            t = self.tf_buffer.lookup_transform('odom', 'base_footprint', rclpy.time.Time())
            self.gt_path_x.append(t.transform.translation.x)
            self.gt_path_y.append(t.transform.translation.y)
        except:
            pass

    def filtered_callback(self, msg):
        # Callback para la odometría filtrada por robot_localization
        self.filtered_path_x.append(msg.pose.pose.position.x)
        self.filtered_path_y.append(msg.pose.pose.position.y)

    def timer_callback(self):
        if self.is_first_odom:
            return
            
        if self.state >= 8:
            msg = Twist()
            self.publisher_.publish(msg)
            self.plot_paths()
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
                msg.linear.x = 0.2
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
                msg.angular.z = 0.2
            else:
                self.state += 1
                self.state_initialized = False
                
        self.publisher_.publish(msg)

    def plot_paths(self):
        self.get_logger().info('Generando gráfica de comparación de todas las trayectorias...')
        plt.figure(figsize=(10, 8))
        
        plt.plot(self.path_x, self.path_y, 'b-', label='Odometría (Raw)')
        
        if len(self.gt_path_x) > 0:
            plt.plot(self.gt_path_x, self.gt_path_y, 'g--', label='Ground Truth (TF)')
            
        if len(self.filtered_path_x) > 0:
            plt.plot(self.filtered_path_x, self.filtered_path_y, 'r-', linewidth=2, label='Odometría Filtrada (EKF/UKF)')
            
        plt.title('Comparación de Trayectorias: Odom vs Ground Truth vs Filtro')
        plt.xlabel('X (m)')
        plt.ylabel('Y (m)')
        plt.legend()
        plt.grid(True)
        plt.axis('equal')
        plt.savefig('trayectoria_completa_filtros.png')
        self.get_logger().info('Gráfico guardado como trayectoria_completa_filtros.png')
        plt.show()
        
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = PlotFilteredNode()
    
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
