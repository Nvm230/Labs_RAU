#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import sensor_msgs_py.point_cloud2 as pc2
import pcl
import numpy as np

class NodoDepthPcl(Node):
    def __init__(self):
        super().__init__('nodo_depth_pcl')
        self.subscription = self.create_subscription(
            PointCloud2,
            '/depth_camera/points',
            self.listener_callback,
            10)
        self.msg_received = False
        self.get_logger().info("Nodo Depth PCL iniciado. Esperando mensaje...")

    def listener_callback(self, msg):
        if not self.msg_received:
            self.get_logger().info("Mensaje recibido, convirtiendo y guardando...")
            
            # Convertir PointCloud2 a lista de puntos (x, y, z) ignorando nulos (nan)
            points_list = []
            for point in pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True):
                points_list.append([point[0], point[1], point[2]])
            
            # Crear nube de puntos de PCL a partir de numpy
            p = pcl.PointCloud()
            p.from_array(np.array(points_list, dtype=np.float32))
            
            # Guardar a archivo .pcd
            pcl.save(p, 'camara_depth.pcd')
            self.get_logger().info("Nube de puntos guardada exitosamente como camara_depth.pcd")
            
            self.msg_received = True

def main(args=None):
    rclpy.init(args=args)
    nodo_depth_pcl = NodoDepthPcl()
    # Ejecutar hasta recibir el primer mensaje y guardarlo
    while rclpy.ok() and not nodo_depth_pcl.msg_received:
        rclpy.spin_once(nodo_depth_pcl)
    nodo_depth_pcl.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
