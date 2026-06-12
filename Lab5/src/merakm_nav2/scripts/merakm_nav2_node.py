#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import time

class Nav2Client(Node):
    def __init__(self):
        super().__init__('merakm_nav2_node')
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def send_goal(self, x, y, theta_z, theta_w):
        goal_msg = NavigateToPose.Goal()

        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.orientation.z = float(theta_z)
        pose.pose.orientation.w = float(theta_w)

        goal_msg.pose = pose

        self.get_logger().info(f'Waiting for action server...')
        self._action_client.wait_for_server()

        self.get_logger().info(f'Sending goal request: x={x}, y={y}')
        self._send_goal_future = self._action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Distance remaining: {feedback.distance_remaining:.2f} meters', throttle_duration_sec=2.0)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result reached!')
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)

    nav_client = Nav2Client()
    
    # Position indicated in code as requested by the activity
    # Target: x=2.0, y=0.5
    nav_client.send_goal(2.0, 0.5, 0.0, 1.0)

    rclpy.spin(nav_client)

if __name__ == '__main__':
    main()
