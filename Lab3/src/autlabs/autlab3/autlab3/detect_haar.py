#!/usr/bin/env python3
"""
Actividad 3.2 - Detección Haar Cascade en SIMULACIÓN y VIDA REAL
=================================================================
El nodo detecta el objeto entrenado en dos modos:

  MODO SIMULACION (--ros-args -p modo:=sim)
    Suscribe al topic /camera/image_raw del Turtlebot3 en Gazebo

  MODO REAL (--ros-args -p modo:=real)
    Abre la webcam directamente (sin ROS)

  MODO TOPIC (--ros-args -p modo:=topic -p topic:=/mi_camara/image_raw)
    Suscribe a cualquier topic de cámara (ej: cámara USB con ROS)

Parámetros:
    modo          → 'sim' | 'real' | 'topic'  (default: 'sim')
    cascade_path  → ruta al archivo cascade.xml entrenado
    topic         → topic de cámara (solo para modo 'topic')
    escala        → scaleFactor del detector (default: 1.1)
    vecinos       → minNeighbors del detector (default: 4)

Uso:
    # Simulación
    ros2 run autlab3 detect_haar

    # Vida real (webcam)
    ros2 run autlab3 detect_haar --ros-args -p modo:=real

    # Cualquier topic
    ros2 run autlab3 detect_haar --ros-args -p modo:=topic -p topic:=/usb_cam/image_raw
"""
import os
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

# Ruta por defecto al cascade.xml entrenado (apunta al src del workspace actual)
RUTA_DEFAULT = '/home/nvm/Documents/nvm/UTEC/Autonoma/Labs/Lab3/Lab3_ws/src/autlabs/autlab3/haar_training/cascade_output/cascade.xml'


class DetectHaar(Node):

    def __init__(self):
        super().__init__('detect_haar_node')

        # ---- Parámetros del nodo ----
        self.declare_parameter('modo',          'sim')
        self.declare_parameter('cascade_path',  os.path.abspath(RUTA_DEFAULT))
        self.declare_parameter('topic',         '/camera/image_raw')
        self.declare_parameter('escala',        1.2)
        self.declare_parameter('vecinos',       8)

        self.modo         = self.get_parameter('modo').value
        self.cascade_path = self.get_parameter('cascade_path').value
        self.topic        = self.get_parameter('topic').value
        self.escala       = self.get_parameter('escala').value
        self.vecinos      = int(self.get_parameter('vecinos').value)

        self.bridge = CvBridge()
        self.image = np.zeros((480, 640, 3), dtype=np.uint8)

        # ---- Timer general para refresco de ventana (10 Hz) ----
        self.timer_display = self.create_timer(0.1, self.cb_timer_display)

        # ---- Cargar el clasificador ----
        self.clasificador = self._cargar_clasificador(self.cascade_path)

        self.get_logger().info(f'Modo: {self.modo}')
        self.get_logger().info(f'Cascade: {self.cascade_path}')

        if self.modo == 'sim':
            # ---- Modo Simulación: suscribe al topic de Gazebo ----
            self.sub = self.create_subscription(
                Image, '/camera/image_raw', self.cb_imagen_ros, 10)
            self.get_logger().info('Suscrito a /camera/image_raw (Gazebo)')

        elif self.modo == 'topic':
            # ---- Modo Topic: suscribe al topic indicado ----
            self.sub = self.create_subscription(
                Image, self.topic, self.cb_imagen_ros, 10)
            self.get_logger().info(f'Suscrito a {self.topic}')

        elif self.modo == 'real':
            # ---- Modo Real: abre la webcam directamente ----
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.get_logger().error('No se encontró webcam (índice 0)')
                raise RuntimeError('Webcam no disponible')
            self.get_logger().info('Usando webcam en tiempo real')

        else:
            self.get_logger().error(f'Modo desconocido: {self.modo}')

    # ------------------------------------------------------------------
    def _cargar_clasificador(self, ruta):
        """Carga el cascade.xml. Si no existe, intenta con los de OpenCV."""
        if os.path.isfile(ruta):
            clf = cv2.CascadeClassifier(ruta)
            if not clf.empty():
                self.get_logger().info('✅ Clasificador entrenado cargado correctamente')
                return clf
            else:
                self.get_logger().warn('⚠️  El archivo cascade.xml está vacío o es inválido')

        # Si no hay cascade entrenado, intentamos usar el de rostros de OpenCV como fallback
        self.get_logger().warn('⚠️  cascade.xml no encontrado en la ruta de entrenamiento.')
        self.get_logger().warn('    Usando cascade de rostros de OpenCV como demo (si está disponible).')
        
        # Ruta estándar en Ubuntu para OpenCV 4
        ruta_demo = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
        if os.path.exists(ruta_demo):
            clf = cv2.CascadeClassifier(ruta_demo)
            return clf
            
        self.get_logger().error('❌ Tampoco se encontró el cascade de rostros. Abortando.')
        raise RuntimeError('No se encontró ningún archivo cascade.xml válido.')

    # ------------------------------------------------------------------
    def _detectar_y_mostrar(self, imagen_bgr, titulo='Deteccion Haar'):
        """
        Aplica el clasificador Haar a la imagen y dibuja los resultados.
        Retorna la imagen con las detecciones dibujadas.
        """
        # Convertir a escala de grises (el Haar trabaja en gris)
        gris = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2GRAY)

        # Equalización del histograma → mejora el contraste y robustez
        gris = cv2.equalizeHist(gris)

        # ---- Detección ----
        detecciones = self.clasificador.detectMultiScale(
            gris,
            scaleFactor=self.escala,   # qué tanto se escala la imagen en cada paso
            minNeighbors=self.vecinos,  # cuántos vecinos mínimo para confirmar detección
            minSize=(100, 100),         # tamaño mínimo del objeto en píxeles (ignora cuadros chiquitos)
            maxSize=(350, 350)          # tamaño máximo (para no detectar el fondo entero)
        )

        salida = imagen_bgr.copy()
        num    = len(detecciones)

        # Dibujar cada detección
        for (x, y, w, h) in detecciones:
            # Rectángulo verde alrededor del objeto
            cv2.rectangle(salida, (x, y), (x + w, y + h), (0, 255, 0), 3)
            # Etiqueta encima del rectángulo
            cv2.putText(salida, 'Objeto detectado',
                        (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

        # Información en la imagen
        info = f'Detecciones: {num}  |  escala={self.escala}  vecinos={self.vecinos}'
        cv2.putText(salida, info, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 200, 255), 2)

        modo_str = f'Modo: {self.modo.upper()}'
        cv2.putText(salida, modo_str, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 0), 2)

        if num > 0:
            # Comentado para evitar spam excesivo en terminal
            # self.get_logger().info(f'Detectado el objeto: {num} instancia(s) en la imagen')
            pass

        return salida

    # ------------------------------------------------------------------
    def cb_imagen_ros(self, msg):
        """Callback para mensajes ROS (simulación y modo topic)."""
        try:
            self.image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Error procesando imagen: {e}')

    # ------------------------------------------------------------------
    def cb_timer_display(self):
        """Timer para visualizar la ventana independientemente de ROS."""
        # Si estamos en modo real, leemos la webcam aquí
        if self.modo == 'real' and hasattr(self, 'cap'):
            ret, frame = self.cap.read()
            if ret:
                self.image = frame
        
        titulo = f'Haar Cascade — {self.modo.upper()}'
        salida = self._detectar_y_mostrar(self.image, titulo=titulo)
        
        cv2.namedWindow(titulo, cv2.WINDOW_NORMAL)
        cv2.imshow(titulo, salida)
        cv2.waitKey(1)

    # ------------------------------------------------------------------
    def destroy_node(self):
        if self.modo == 'real' and hasattr(self, 'cap'):
            self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()


# ----------------------------------------------------------------------
def main(args=None):
    rclpy.init(args=args)
    node = DetectHaar()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
