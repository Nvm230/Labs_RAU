#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class Cam(Node):

  def __init__(self):
    super().__init__('camera_node')

    self.bridge = CvBridge()
    self.image = np.zeros((10, 10, 3), dtype=np.uint8)

    self.subscription = self.create_subscription(Image,'/camera/image_raw',self.image_callback,10)

    self.publisher = self.create_publisher(Image,'image_out',10)

    self.timer = self.create_timer(0.1, self.timer_callback)  # 10 Hz

  def image_callback(self, msg):
    self.image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

  def timer_callback(self):
    I = self.image

    # Aquí puede poner el codigo de procesamiento de imagenes, por ejemplo:
    I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)

    # Show image
    cv2.imshow("Imagen Camara Turtlebot3", I)
    cv2.waitKey(1)

    # Publicador opcional, descomentar en caso lo necesite
    #msg = self.bridge.cv2_to_imgmsg(I, encoding='bgr8')
    #self.publisher.publish(msg)


def main(args=None):
  
  rclpy.init(args=args)
  node = Cam()

  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    pass

  node.destroy_node()
  rclpy.shutdown()
  cv2.destroyAllWindows()

if __name__ == '__main__':
  main()
