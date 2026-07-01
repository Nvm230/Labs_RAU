import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import numpy as np
import matplotlib.pyplot as plt

class Kalman1DNode(Node):
    def __init__(self):
        super().__init__('kalman_1d_node')
        
        self.subscription = self.create_subscription(
            Float64,
            '/infrared',
            self.infrared_callback,
            10
        )
        
        self.measurements = []
        self.max_measurements = 20
        self.is_done = False
        
        # Parámetros del Filtro de Kalman 1D
        self.x_est = 0.0 # Estado estimado inicial
        self.P_est = 1.0 # Varianza estimada inicial (incertidumbre)
        self.R = 0.1     # Varianza de la medición (ruido del sensor) - Se ajustará luego
        self.Q = 0.001   # Varianza del proceso (ruido del modelo)
        
        self.estimates = []
        
        self.get_logger().info('Recopilando mediciones...')

    def infrared_callback(self, msg):
        if self.is_done:
            return
            
        z = msg.data
        self.measurements.append(z)
        
        if len(self.measurements) == 1:
            self.x_est = z # Inicializamos con la primera lectura
            
        # --- Predicción ---
        x_pred = self.x_est
        P_pred = self.P_est + self.Q
        
        # --- Actualización ---
        K = P_pred / (P_pred + self.R) # Ganancia de Kalman
        self.x_est = x_pred + K * (z - x_pred)
        self.P_est = (1 - K) * P_pred
        
        self.estimates.append(self.x_est)
        
        self.get_logger().info(f'Medición: {z:.4f} | Estimación: {self.x_est:.4f}')
        
        if len(self.measurements) >= self.max_measurements:
            self.is_done = True
            self.process_and_plot()

    def process_and_plot(self):
        measurements_array = np.array(self.measurements)
        variance = np.var(measurements_array)
        self.get_logger().info(f'--- Recopilación completa ---')
        self.get_logger().info(f'Varianza de las {self.max_measurements} mediciones: {variance:.6f}')
        
        # Actualizamos la R (ruido del sensor) basado en la varianza real obtenida para futuros usos si se desea
        self.R = variance
        
        # Graficar
        plt.figure(figsize=(10, 5))
        plt.plot(self.measurements, 'ro-', label='Medición (Sensor)')
        plt.plot(self.estimates, 'b*-', label='Estimación (Filtro Kalman)')
        plt.title('Filtro de Kalman 1D - Sensor Infrarrojo simulado')
        plt.xlabel('Tiempo (iteración)')
        plt.ylabel('Distancia (m)')
        plt.legend()
        plt.grid(True)
        
        # Guardar gráfico y mostrar
        plt.savefig('kalman_1d_result.png')
        self.get_logger().info('Gráfico guardado como kalman_1d_result.png')
        plt.show()
        
        # Detener ROS 2
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = Kalman1DNode()
    
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
