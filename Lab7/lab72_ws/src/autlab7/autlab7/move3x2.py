#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
import matplotlib.pyplot as plt
import os

class MoveSquare(Node):
    def __init__(self):
        super().__init__('move3x2')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        
        # Variables de control
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.trayectoria = []  # lista de (x, y)
        self.estado = 'avanzar'  # 'avanzar' o 'girar'
        self.distancia_recorrida = 0.0
        self.angulo_recorrido = 0.0
        self.distancia_objetivo = 3.0  # primer lado (luego 2.0)
        self.angulo_objetivo = math.pi / 2.1  # ~90°
        self.lado_actual = 0  # 0: lado de 3m, 1: lado de 2m, 2: lado de 3m, 3: lado de 2m
        self.vel_linear = 0.6  # m/s
        self.vel_angular = 0.2  # rad/s
        self.x_inicial = None
        self.y_inicial = None
        self.yaw_inicial = None
        self.recorrido = 0.0
        self.giro_acumulado = 0.0
        self.estado_girando = False
        
        # Timer para publicar cmd_vel a 10 Hz
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info("Nodo move3x2 iniciado")

    def odom_callback(self, msg):
        # Guardar posición y orientación
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self.yaw = math.atan2(2.0*(q.w*q.z + q.x*q.y), 1.0 - 2.0*(q.y*q.y + q.z*q.z))
        # Registrar trayectoria cada cierto tiempo
        self.trayectoria.append((self.x, self.y))

    def control_loop(self):
        twist = Twist()
        
        if self.estado == 'avanzar':
            # Avanzar en línea recta
            twist.linear.x = self.vel_linear
            twist.angular.z = 0.0
            self.publisher.publish(twist)
            
            # Calcular distancia recorrida desde el inicio del lado
            if self.x_inicial is None:
                self.x_inicial = self.x
                self.y_inicial = self.y
            dx = self.x - self.x_inicial
            dy = self.y - self.y_inicial
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Si alcanzó la distancia objetivo, cambiar a girar
            if dist >= self.distancia_objetivo:
                self.estado = 'girar'
                self.x_inicial = None
                self.y_inicial = None
                self.giro_acumulado = 0.0
                # Guardar yaw inicial para el giro
                self.yaw_inicial = self.yaw
                self.get_logger().info(f"Lado completado, distancia: {dist:.2f}m")
        
        elif self.estado == 'girar':
            # Girar 90° a la izquierda
            twist.linear.x = 0.0
            twist.angular.z = self.vel_angular
            self.publisher.publish(twist)
            
            ang = math.atan2(math.sin(self.yaw - self.yaw_inicial), math.cos(self.yaw - self.yaw_inicial))
            self.giro_acumulado = abs(ang)

            if self.giro_acumulado >= self.angulo_objetivo:
                self.estado = 'avanzar'
                self.yaw_inicial = None
                # Cambiar distancia objetivo según el lado
                self.lado_actual += 1
                if self.lado_actual % 2 == 0:
                    self.distancia_objetivo = 3.0
                else:
                    self.distancia_objetivo = 2.0
                self.get_logger().info(f"Giro completado, ángulo: {self.giro_acumulado:.2f} rad")
                
                # Si ya completamos 4 lados, detener y guardar gráfica
                if self.lado_actual >= 4:
                    twist.linear.x = 0.0
                    twist.angular.z = 0.0
                    self.publisher.publish(twist)
                    self.timer.cancel()
                    self.guardar_grafica()
                    rclpy.shutdown()

    def guardar_grafica(self):
        # Graficar la trayectoria
        if self.trayectoria:
            x_vals = [p[0] for p in self.trayectoria]
            y_vals = [p[1] for p in self.trayectoria]
            plt.figure(figsize=(8,6))
            plt.plot(x_vals, y_vals, 'b-', label='Odometría')
            plt.xlabel('X (m)')
            plt.ylabel('Y (m)')
            plt.title('Trayectoria del robot (cuadrado 3x2)')
            plt.axis('equal')
            plt.grid(True)
            plt.legend()
            # Guardar imagen (opcional) y mostrar
            plt.savefig('move3x2.png')
            plt.show()
        else:
            self.get_logger().warn("No se registró trayectoria")

def main(args=None):
    rclpy.init(args=args)
    node = MoveSquare()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
