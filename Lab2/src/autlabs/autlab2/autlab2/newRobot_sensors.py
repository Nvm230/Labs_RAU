#!/usr/bin/env python3
"""
newRobot_sensors - Encoder Odometry Node for Differential Drive Robot

Actividad 3.2: Computes odometry from encoder readings (joint_states)
using forward kinematics for a differential drive robot.

Robot parameters:
    - L (wheel separation / distance between axes) = 0.20 m
    - R (wheel radius) = 0.06 m

Forward Kinematics (odometry from encoders):
    Δs_R = R * Δθ_R        (right wheel arc length)
    Δs_L = R * Δθ_L        (left wheel arc length)
    Δs   = (Δs_R + Δs_L) / 2   (robot center displacement)
    Δφ   = (Δs_R - Δs_L) / L   (heading change)

    x += Δs * cos(θ + Δφ/2)
    y += Δs * sin(θ + Δφ/2)
    θ += Δφ

Subscribes:
    /joint_states (sensor_msgs/JointState) - wheel encoder readings

Publishes:
    /odom_encoder (nav_msgs/Odometry) - computed odometry
    TF: odom_encoder → base_footprint
"""

import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped, Quaternion
from tf2_ros import TransformBroadcaster


def euler_to_quaternion(yaw):
    """Convert yaw angle to quaternion (roll=0, pitch=0)."""
    return Quaternion(
        x=0.0,
        y=0.0,
        z=math.sin(yaw / 2.0),
        w=math.cos(yaw / 2.0)
    )


class NewRobotSensors(Node):
    def __init__(self):
        super().__init__('newRobot_sensors')

        # ============ Robot Parameters ============
        self.declare_parameter('wheel_separation', 0.20)
        self.declare_parameter('wheel_radius', 0.06)

        self.L = self.get_parameter('wheel_separation').value
        self.R = self.get_parameter('wheel_radius').value

        self.get_logger().info(
            f'newRobot_sensors initialized: L={self.L}m, R={self.R}m')

        # ============ Odometry State ============
        self.x = 0.0        # Position x [m]
        self.y = 0.0        # Position y [m]
        self.theta = 0.0    # Heading [rad]

        # Previous encoder readings
        self.prev_left_pos = None
        self.prev_right_pos = None
        self.prev_time = None

        # Joint name mapping
        self.left_joint = 'wheel_left_joint'
        self.right_joint = 'wheel_right_joint'

        # ============ Subscriber ============
        self.joint_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_states_callback, 10)

        # ============ Publisher ============
        self.odom_pub = self.create_publisher(
            Odometry, '/odom_encoder', 10)

        # ============ TF Broadcaster ============
        self.tf_broadcaster = TransformBroadcaster(self)

    def joint_states_callback(self, msg: JointState):
        """
        Process encoder readings and compute odometry.

        Forward kinematics:
            Δs = R * (Δθ_R + Δθ_L) / 2
            Δφ = R * (Δθ_R - Δθ_L) / L
        """
        # Find wheel positions in joint_states message
        try:
            left_idx = msg.name.index(self.left_joint)
            right_idx = msg.name.index(self.right_joint)
        except ValueError:
            return  # Joints not found yet

        left_pos = msg.position[left_idx]
        right_pos = msg.position[right_idx]
        current_time = self.get_clock().now()

        # Initialize on first reading
        if self.prev_left_pos is None:
            self.prev_left_pos = left_pos
            self.prev_right_pos = right_pos
            self.prev_time = current_time
            return

        # ============ Compute deltas ============
        dt = (current_time - self.prev_time).nanoseconds * 1e-9
        if dt <= 0.0:
            return

        # Change in wheel angles [rad]
        delta_left = left_pos - self.prev_left_pos
        delta_right = right_pos - self.prev_right_pos

        # Arc lengths [m]
        ds_left = self.R * delta_left
        ds_right = self.R * delta_right

        # ============ Forward Kinematics ============
        # Robot center displacement
        ds = (ds_right + ds_left) / 2.0
        # Heading change
        dphi = (ds_right - ds_left) / self.L

        # ============ Update Pose ============
        # Use midpoint integration for better accuracy
        self.x += ds * math.cos(self.theta + dphi / 2.0)
        self.y += ds * math.sin(self.theta + dphi / 2.0)
        self.theta += dphi
        # Normalize theta to [-π, π]
        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))

        # ============ Compute velocities ============
        vx = ds / dt        # Linear velocity [m/s]
        vth = dphi / dt     # Angular velocity [rad/s]

        # ============ Publish Odometry ============
        odom = Odometry()
        odom.header.stamp = current_time.to_msg()
        odom.header.frame_id = 'odom_encoder'
        odom.child_frame_id = 'base_footprint'

        # Position
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation = euler_to_quaternion(self.theta)

        # Velocity
        odom.twist.twist.linear.x = vx
        odom.twist.twist.linear.y = 0.0
        odom.twist.twist.angular.z = vth

        self.odom_pub.publish(odom)

        # ============ Publish TF ============
        t = TransformStamped()
        t.header.stamp = current_time.to_msg()
        t.header.frame_id = 'odom_encoder'
        t.child_frame_id = 'base_footprint'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation = euler_to_quaternion(self.theta)

        self.tf_broadcaster.sendTransform(t)

        # ============ Log ============
        self.get_logger().info(
            f'Odom: x={self.x:.3f}, y={self.y:.3f}, '
            f'θ={math.degrees(self.theta):.1f}°, '
            f'v={vx:.3f} m/s, ω={vth:.3f} rad/s',
            throttle_duration_sec=1.0)

        # Save for next iteration
        self.prev_left_pos = left_pos
        self.prev_right_pos = right_pos
        self.prev_time = current_time


def main(args=None):
    rclpy.init(args=args)
    node = NewRobotSensors()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
