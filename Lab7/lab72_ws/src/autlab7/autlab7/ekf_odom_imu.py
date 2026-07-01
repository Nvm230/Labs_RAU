#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf2_ros import Buffer, TransformListener
import math
import matplotlib.pyplot as plt

class Ekf_odom_imu(Node):
    def __init__(self):
        super().__init__('ekf_odom_imu')

        # Publicador de cmd_vel
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        # Suscripciones para odometría, IMU y EKF
        self.sub_odom = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.sub_ekf = self.create_subscription(Odometry, '/odom/ekf_odom', self.ekf_callback, 10)
        self.sub_ekf_imu = self.create_subscription(Odometry, '/odom/ekf_odom_imu', self.ekf_imu_callback, 10)

        # TF listener para posición verdadera
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Almacenamiento de trayectorias
        self.tray_odom = []   # (x, y)
        self.tray_ekf = []    # (x, y)
        self.tray_true = []   # (x, y)
        self.tray_ekf_imu = []  # (x, y)

        # Variables de control (igual que move3x2)
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.estado = 'avanzar'
        self.distancia_objetivo = 1.5
        self.angulo_objetivo = math.pi / 2.05
        self.lado_actual = 0
        self.vel_linear = 0.26
        self.vel_angular = 0.82
        self.x_inicial = None
        self.y_inicial = None
        self.yaw_inicial = None
        self.giro_acumulado = 0.0

        # Timer de control a 10 Hz
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info("Nodo Ekf_odom_imu iniciado")

    # ---------- Callbacks de suscripción ----------
    def odom_callback(self, msg):
        # Guardar posición y orientación para control
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self.yaw = math.atan2(2.0*(q.w*q.z + q.x*q.y), 1.0 - 2.0*(q.y*q.y + q.z*q.z))
        # Guardar trayectoria de odometría cruda
        self.tray_odom.append((self.x, self.y))

    def ekf_callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        self.tray_ekf.append((x, y))

    def ekf_imu_callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        self.tray_ekf_imu.append((x, y))

    def get_true_pose(self):
        """Obtiene la posición verdadera desde TF (odom -> base_footprint)."""
        try:
            trans = self.tf_buffer.lookup_transform('odom', 'base_footprint', rclpy.time.Time())
            return (trans.transform.translation.x, trans.transform.translation.y)
        except Exception:
            return None

    # ---------- Control de movimiento ----------
    def control_loop(self):
        # Guardar posición verdadera en cada iteración (si está disponible)
        true_pose = self.get_true_pose()
        if true_pose is not None:
            self.tray_true.append(true_pose)

        twist = Twist()

        if self.estado == 'avanzar':
            twist.linear.x = self.vel_linear
            twist.angular.z = 0.0
            self.publisher.publish(twist)

            if self.x_inicial is None:
                self.x_inicial = self.x
                self.y_inicial = self.y

            dx = self.x - self.x_inicial
            dy = self.y - self.y_inicial
            dist = math.sqrt(dx*dx + dy*dy)

            if dist >= self.distancia_objetivo:
                self.estado = 'girar'
                self.x_inicial = None
                self.y_inicial = None
                self.giro_acumulado = 0.0
                self.yaw_inicial = self.yaw
                self.get_logger().info(f"Lado completado, distancia: {dist:.2f}m")

        elif self.estado == 'girar':
            ang = math.atan2(math.sin(self.yaw - self.yaw_inicial),
                             math.cos(self.yaw - self.yaw_inicial))
            self.giro_acumulado = abs(ang)

            error = self.angulo_objetivo - self.giro_acumulado

            if error <= 0.04: # Tolerancia de ~2 grados
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                self.publisher.publish(twist)
                
                self.estado = 'avanzar'
                self.yaw_inicial = None
                self.lado_actual += 1
                if self.lado_actual % 2 == 0:
                    self.distancia_objetivo = 1.5
                else:
                    self.distancia_objetivo = 0.5
                self.get_logger().info(f"Giro completado, ángulo: {self.giro_acumulado:.2f} rad")
                
                # Si ya completamos 4 lados, detener y finalizar
                if self.lado_actual >= 4:
                    twist.linear.x = 0.0
                    twist.angular.z = 0.0
                    self.publisher.publish(twist)
                    self.timer.cancel()
                    self.finalizar()
            else:
                # Control Proporcional para no pasarse. Minimo 0.25 para vencer friccion.
                velocidad_giro = max(0.25, min(self.vel_angular, error * 1.5))
                twist.linear.x = 0.0
                twist.angular.z = velocidad_giro
                self.publisher.publish(twist)

    # ---------- Finalización y gráfica ----------
    def finalizar(self):
        self.get_logger().info("Movimiento completado. Generando gráfica...")
        self.generar_grafica()
        rclpy.shutdown()

    def generar_grafica(self):
        plt.figure(figsize=(10, 8))

        if self.tray_odom:
            x_odom, y_odom = zip(*self.tray_odom)
            plt.plot(x_odom, y_odom, 'b-', linewidth=2, label='Odometría cruda')

        if self.tray_ekf:
            x_ekf, y_ekf = zip(*self.tray_ekf)
            plt.plot(x_ekf, y_ekf, 'g-', linewidth=2, label='EKF (odom)')

        if self.tray_true:
            x_true, y_true = zip(*self.tray_true)
            plt.plot(x_true, y_true, 'r--', linewidth=2, label='Verdadera (TF)')

        if self.tray_ekf_imu:
            x_ekf_imu, y_ekf_imu = zip(*self.tray_ekf_imu)
            plt.plot(x_ekf_imu, y_ekf_imu, 'c-', linewidth=2, label='EKF (odom+imu)')

        plt.xlabel('X (m)')
        plt.ylabel('Y (m)')
        plt.title('Comparación de trayectorias - Cuadrado 3x2')
        plt.axis('equal')
        plt.grid(True)
        plt.legend()
        plt.savefig('ekf_odom_imu.png')
        plt.show()

# ---------- Punto de entrada ----------
def main(args=None):
    rclpy.init(args=args)
    node = Ekf_odom_imu()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()