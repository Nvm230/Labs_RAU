import threading
import rclpy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float64

def main():
    rclpy.init()

    node = rclpy.create_node('infrared')

    msg_received = LaserScan()
    msg_published = Float64() 

    def callback(msg):
        nonlocal msg_received
        msg_received = msg
        node.get_logger().info(f'Received scan with {len(msg.ranges)} measurements')

    subscription = node.create_subscription(LaserScan, 'scan', callback, 10)
    publisher = node.create_publisher(Float64, 'infrared', 10)

    thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    thread.start()

    rate = node.create_rate(10.0)  # 10 Hz = 10 medidas por segundo

    try:
        while rclpy.ok():
            if msg_received.ranges:
                # Tomar medición centradas en el frente
                front_measurement = msg_received.ranges[0]
                msg_published.data = front_measurement
                publisher.publish(msg_published)
                node.get_logger().info(f'Publishing: {msg_published.data} measurements')
            else:
                node.get_logger().warn('No scan data received yet')

            rate.sleep()
    except KeyboardInterrupt:
        node.get_logger().info('Subscriber stopped by user')

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()