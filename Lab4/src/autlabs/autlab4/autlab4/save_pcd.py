#!/usr/bin/env python3
import rospy
from pcl_helper import *
from sensor_msgs.msg import PointCloud2

global cloud_msg
cloud_msg = PointCloud2()

def callback(msg): # Tipo callback
  global cloud_msg
  cloud_msg = msg

if __name__ == "__main__":

  rospy.init_node('save_pcd')
  rospy.Subscriber('/camera/depth_registered/points', PointCloud2, callback)
  rate = rospy.Rate(2) # 2 Hz
  
  while not rospy.is_shutdown():
    
    if len(cloud_msg.data) > 0:
      cloud = ros2pcl(cloud_msg)
      pcl.save(cloud, 'mesa.pcd')
      break
    
    rate.sleep()
