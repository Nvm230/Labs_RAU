#!/usr/bin/env python3
"""
Actividad 1 - Lab 3: Detección de pelota azul y navegación con LiDAR
El robot se mueve hacia la pelota azul usando visión y se detiene 
cuando el LiDAR detecta que está muy cerca.
"""
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge


class DetectBall(Node):

    def __init__(self):
        super().__init__('detect_ball_node')

        self.bridge = CvBridge()
        self.image  = np.zeros((480, 640, 3), dtype=np.uint8)

        # Distancia mínima del LiDAR para detenerse (metros)
        self.dist_frontal = 999.0
        self.DISTANCIA_PARADA = 0.5   # 50 cm

        # ---- Máquina de Estados ----
        self.estado = 'BUSCANDO'
        self.tiempo_inicio_estado = 0.0

        # ---- Suscriptores ----
        self.sub_cam   = self.create_subscription(Image,     '/camera/image_raw', self.cb_imagen,  10)
        self.sub_lidar = self.create_subscription(LaserScan, '/scan',             self.cb_lidar,   10)

        # ---- Publicador de velocidad ----
        self.pub_vel = self.create_publisher(Twist, '/cmd_vel', 10)

        # ---- Timer: procesa la imagen a 10 Hz ----
        self.timer = self.create_timer(0.1, self.cb_timer)

        self.get_logger().info('Nodo detect_ball iniciado. Buscando pelota azul...')

    # ------------------------------------------------------------------
    def cb_imagen(self, msg):
        """Guarda la imagen más reciente de la cámara."""
        self.image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

    # ------------------------------------------------------------------
    def cb_lidar(self, msg):
        """
        Calcula la distancia al obstáculo frontal.
        El sector frontal es ±15° (índices cerca de 0 y el final del array).
        """
        ranges = np.array(msg.ranges)

        # Quitamos infinitos y NaN para no romper el cálculo
        ranges[ranges == np.inf] = 999.0
        ranges = np.nan_to_num(ranges, nan=999.0)

        n = len(ranges)
        # Sector frontal: últimos 15° y primeros 15°
        sector = int(n * 15 / 360)
        frente = np.concatenate([ranges[:sector], ranges[n - sector:]])
        self.dist_frontal = float(np.min(frente))

    # ------------------------------------------------------------------
    def cb_timer(self):
        """
        Lógica principal: detecta la pelota azul y decide la velocidad.
        """
        img = self.image.copy()
        cmd = Twist()   # por defecto todo en 0 → robot parado

        # -------- DETECCIÓN DE COLOR AZUL --------
        # Convertimos BGR → HSV para segmentar por color
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Rango de color azul en HSV
        azul_bajo = np.array([100, 100, 50])
        azul_alto = np.array([130, 255, 255])
        mascara   = cv2.inRange(hsv, azul_bajo, azul_alto)

        # Limpiamos ruido pequeño con morfología
        kernel  = np.ones((5, 5), np.uint8)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN,  kernel)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)

        # Encontramos contornos de la pelota
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        pelota_detectada = False
        error_x = 0      # posición horizontal de la pelota respecto al centro
        area_pelota = 0  # Área para detenerse por visión

        if contornos:
            # Tomamos el contorno más grande
            mayor = max(contornos, key=cv2.contourArea)
            area  = cv2.contourArea(mayor)

            if area > 300:   # ignoramos manchas muy pequeñas
                pelota_detectada = True
                area_pelota = area

                # Centro del contorno
                M   = cv2.moments(mayor)
                cx  = int(M['m10'] / M['m00']) if M['m00'] != 0 else img.shape[1] // 2

                # Error: qué tan a la izquierda/derecha está la pelota
                centro_img = img.shape[1] // 2
                error_x    = cx - centro_img

                # Dibujamos sobre la imagen para visualizar
                cv2.drawContours(img, [mayor], -1, (0, 255, 0), 2)
                cv2.circle(img, (cx, img.shape[0] // 2), 5, (0, 0, 255), -1)
                cv2.putText(img, f'Pelota: area={int(area)} err={error_x}',
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # -------- MÁQUINA DE ESTADOS (DECISIÓN DE MOVIMIENTO) --------
        tiempo_actual = self.get_clock().now().nanoseconds / 1e9

        if self.estado == 'BUSCANDO':
            if pelota_detectada:
                self.estado = 'ACERCANDOSE'
                self.get_logger().info('Pelota detectada! Acercandose...')
            else:
                # Exploración aleatoria y evasión de obstáculos
                if self.dist_frontal < 0.6:
                    # Obstáculo cerca, girar para evadir pared
                    cmd.linear.x  = 0.0
                    cmd.angular.z = 0.5  # girar a la izquierda
                    cv2.putText(img, 'Evadiendo obstaculo...', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                else:
                    # Avanzar y girar levemente para explorar el mapa (movimiento ondulante)
                    cmd.linear.x  = 0.15
                    cmd.angular.z = 0.2 * np.sin(tiempo_actual) 
                    cv2.putText(img, 'Buscando (Modo Aleatorio)...', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        elif self.estado == 'ACERCANDOSE':
            # Nos detenemos si el LiDAR ve algo a < 50cm, O si la cámara ve la pelota suficientemente grande
            if self.dist_frontal < self.DISTANCIA_PARADA or area_pelota > 20000:
                self.get_logger().info(f'Objetivo alcanzado! Esperando 3 segundos...')
                self.estado = 'ESPERANDO'
                self.tiempo_inicio_estado = tiempo_actual
                cmd.linear.x  = 0.0
                cmd.angular.z = 0.0
            elif not pelota_detectada:
                # Perdimos la pelota, volvemos a buscar
                self.estado = 'BUSCANDO'
            else:
                # Vemos la pelota → avanzamos y corregimos la dirección
                cmd.linear.x  = 0.15                        
                cmd.angular.z = -error_x / 500.0            
                cv2.putText(img, 'Acercandose al objetivo...', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        elif self.estado == 'ESPERANDO':
            cmd.linear.x  = 0.0
            cmd.angular.z = 0.0
            tiempo_transcurrido = tiempo_actual - self.tiempo_inicio_estado
            cv2.putText(img, f'ESPERANDO... {3.0 - tiempo_transcurrido:.1f}s', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            if tiempo_transcurrido > 3.0:
                self.get_logger().info('Tiempo terminado! Girando para buscar otra pelota...')
                self.estado = 'ESCAPANDO'
                self.tiempo_inicio_estado = tiempo_actual

        elif self.estado == 'ESCAPANDO':
            # Girar rápido para darle la espalda a la pelota actual
            cmd.linear.x  = 0.0
            cmd.angular.z = 1.0  # Giro rápido sobre su eje
            tiempo_transcurrido = tiempo_actual - self.tiempo_inicio_estado
            cv2.putText(img, 'Evadiendo pelota actual...', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            
            if tiempo_transcurrido > 2.0: # 2 segundos a 1.0 rad/s = aprox 114 grados de giro
                self.get_logger().info('Escape terminado, retomando busqueda...')
                self.estado = 'BUSCANDO'

        # Escribir el estado actual fijo en la pantalla
        cv2.putText(img, f'ESTADO: {self.estado}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        self.pub_vel.publish(cmd)

        # -------- VISUALIZACIÓN --------
        mascara_color = cv2.cvtColor(mascara, cv2.COLOR_GRAY2BGR)
        combinada     = np.hstack([img, mascara_color])
        cv2.imshow('Deteccion Pelota Azul | Original  /  Mascara', combinada)
        cv2.waitKey(1)


# ----------------------------------------------------------------------
def main(args=None):
    rclpy.init(args=args)
    node = DetectBall()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    # Paramos el robot al cerrar
    node.pub_vel.publish(Twist())
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
