import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float64

class InfraredNode(Node):
    def __init__(self):
        super().__init__('infrared_node')
        
        # Publisher para la medición de infrarrojo a 10 Hz
        self.publisher_ = self.create_publisher(Float64, '/infrared', 10)
        
        # Subscriptor al láser (LiDAR)
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )
        
        # Timer para publicar a 10 Hz
        self.timer_period = 0.1  # 10 Hz
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        
        # Variable para almacenar la distancia actual frente al robot
        self.current_distance = 0.0

    def scan_callback(self, msg):
        # El rayo frente al robot en Turtlebot3 Waffle Pi típicamente es el índice 0 (0 grados).
        # msg.ranges contiene las distancias medidas.
        
        dist = msg.ranges[0]
        
        # Manejo de inf y nan
        if dist > msg.range_max:
            dist = msg.range_max
        elif dist < msg.range_min:
            dist = msg.range_min
            
        self.current_distance = float(dist)

    def timer_callback(self):
        msg = Float64()
        msg.data = self.current_distance
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = InfraredNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
