#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2

class NodoDepth(Node):
    def __init__(self):
        super().__init__('nodo_depth')
        self.subscription = self.create_subscription(
            PointCloud2,
            '/depth_camera/points',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.get_logger().info("Nodo Depth iniciado. Esperando PointCloud2...")

    def listener_callback(self, msg):
        self.get_logger().info(f"Recibido mensaje PointCloud2 con dimensiones: {msg.width} x {msg.height}")

def main(args=None):
    rclpy.init(args=args)
    nodo_depth = NodoDepth()
    try:
        rclpy.spin(nodo_depth)
    except KeyboardInterrupt:
        pass
    finally:
        nodo_depth.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
