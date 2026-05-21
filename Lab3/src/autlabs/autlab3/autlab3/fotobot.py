#!/usr/bin/env python3
"""
Actividad 2 - Lab 3: Robot CamBot que toma fotos del Turtlebot3
- Se posicionan 3 CamBots en círculo alrededor del Turtlebot3
- Cada robot tiene una cámara en un poste de 1 metro
- Toma 30 fotos y las guarda en disco
"""
import rclpy
from rclpy.node import Node
import cv2
import os
import time
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class FotoBot(Node):

    def __init__(self):
        super().__init__('fotobot_node')

        # Parámetro: ¿qué cambot soy? (1, 2 o 3)
        self.declare_parameter('robot_id', 1)
        self.robot_id = self.get_parameter('robot_id').value

        self.bridge = CvBridge()
        self.imagen_actual = None

        # Carpeta donde guardaremos las fotos
        self.carpeta = f'/tmp/fotos_cambot/robot_{self.robot_id}'
        os.makedirs(self.carpeta, exist_ok=True)

        self.contador_fotos = 0
        self.MAX_FOTOS      = 10    # cada robot toma 10 fotos → 3 robots = 30 fotos

        # El topic de la cámara varía según el robot
        # (en la simulación cada robot tiene su namespace)
        topic_cam = f'/cambot{self.robot_id}/cambot_camera/image_raw'
        self.sub = self.create_subscription(Image, topic_cam, self.cb_imagen, 10)

        # Toma una foto cada 2 segundos
        self.timer = self.create_timer(2.0, self.cb_timer)

        self.get_logger().info(f'FotoBot {self.robot_id} listo. Guardando fotos en {self.carpeta}')

    # ------------------------------------------------------------------
    def cb_imagen(self, msg):
        """Guarda la última imagen recibida."""
        self.imagen_actual = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

    # ------------------------------------------------------------------
    def cb_timer(self):
        """Toma una foto si ya tenemos imagen y no llegamos al límite."""
        if self.imagen_actual is None:
            self.get_logger().warn('Esperando imagen de cámara...')
            return

        if self.contador_fotos >= self.MAX_FOTOS:
            self.get_logger().info(f'Robot {self.robot_id}: {self.MAX_FOTOS} fotos completadas.')
            return

        # Nombre del archivo con timestamp
        nombre = os.path.join(self.carpeta, f'foto_{self.contador_fotos:03d}.jpg')
        cv2.imwrite(nombre, self.imagen_actual)
        self.contador_fotos += 1
        self.get_logger().info(f'Robot {self.robot_id}: foto {self.contador_fotos}/{self.MAX_FOTOS} guardada → {nombre}')

        # Mostramos la foto en pantalla (Comentado para evitar problemas con BSPWM)
        # cv2.imshow(f'CamBot {self.robot_id}', self.imagen_actual)
        # cv2.waitKey(1)


# ----------------------------------------------------------------------
def main(args=None):
    rclpy.init(args=args)
    node = FotoBot()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
