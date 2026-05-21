#!/usr/bin/env python3
"""
newRobot_cmd - Inverse Kinematics + Motor Control Node

Actividad 3.1: Subscribes to /cmd_vel, applies inverse kinematics,
and sends wheel velocities to Moteus motor controllers.

Robot parameters:
    - L (wheel separation / distance between axes) = 0.20 m
    - R (wheel radius) = 0.06 m

Inverse Kinematics:
    ωR = (v + ω * L/2) / R   [rad/s]
    ωL = (v - ω * L/2) / R   [rad/s]

Subscribes:
    /cmd_vel (geometry_msgs/Twist) - desired robot velocity

Usage:
    # With real motors:
    ros2 run autlab2 newRobot_cmd
    # Without motors (testing):
    ros2 run autlab2 newRobot_cmd --ros-args -p simulate:=true
"""

import math
import sys
import asyncio

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64


class NewRobotCmd(Node):
    def __init__(self):
        super().__init__('newRobot_cmd')

        # ============ Robot Parameters ============
        self.declare_parameter('wheel_separation', 0.20)
        self.declare_parameter('wheel_radius', 0.06)
        self.declare_parameter('simulate', False)

        self.L = self.get_parameter('wheel_separation').value
        self.R = self.get_parameter('wheel_radius').value
        self.simulate = self.get_parameter('simulate').value

        # Wheel velocities [rad/s]
        self.omega_left = 0.0
        self.omega_right = 0.0

        # ============ Subscriber (CREATES /cmd_vel topic) ============
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)

        # ============ Publishers (for debugging) ============
        self.pub_left = self.create_publisher(Float64, '/wheel_cmd/left', 10)
        self.pub_right = self.create_publisher(Float64, '/wheel_cmd/right', 10)

        self.get_logger().info(
            f'newRobot_cmd ready: L={self.L}m, R={self.R}m | '
            f'Publish to /cmd_vel to move the robot!')

    def cmd_vel_callback(self, msg: Twist):
        """
        Inverse kinematics: (v, ω) → (ωL, ωR)

        ωR = (v + ω * L/2) / R
        ωL = (v - ω * L/2) / R
        """
        v = msg.linear.x
        omega = msg.angular.z

        # Inverse kinematics
        self.omega_right = (v + omega * self.L / 2.0) / self.R
        self.omega_left = (v - omega * self.L / 2.0) / self.R

        # Publish wheel velocities for debugging
        msg_left = Float64()
        msg_left.data = self.omega_left
        self.pub_left.publish(msg_left)

        msg_right = Float64()
        msg_right.data = self.omega_right
        self.pub_right.publish(msg_right)

        self.get_logger().info(
            f'v={v:.3f} m/s, ω={omega:.3f} rad/s → '
            f'ωL={self.omega_left:.3f} rad/s, ωR={self.omega_right:.3f} rad/s',
            throttle_duration_sec=0.5)


async def run_with_moteus(node):
    """Main loop: spins ROS + sends to moteus motors."""
    import moteus

    transport = moteus.Fdcanusb()
    c1 = moteus.Controller(id=1)  # Left
    c2 = moteus.Controller(id=2)  # Right

    await transport.cycle([c1.make_stop(), c2.make_stop()])
    node.get_logger().info('Moteus motors connected!')

    rate = 50
    try:
        while rclpy.ok():
            # Process ROS callbacks
            rclpy.spin_once(node, timeout_sec=0.0)

            # rad/s → rev/s
            vel_left = node.omega_left / (2.0 * math.pi)
            vel_right = node.omega_right / (2.0 * math.pi)

            await transport.cycle([
                c1.make_position(position=math.nan, velocity=vel_left, query=True),
                c2.make_position(position=math.nan, velocity=vel_right, query=True),
            ])
            await asyncio.sleep(1.0 / rate)
    except KeyboardInterrupt:
        pass
    finally:
        await transport.cycle([c1.make_stop(), c2.make_stop()])
        node.get_logger().info('Motors stopped.')


def run_simulate(node):
    """Main loop: only ROS, no motors."""
    node.get_logger().info('SIMULATE mode: no moteus hardware')
    rclpy.spin(node)


def main(args=None):
    rclpy.init(args=args)
    node = NewRobotCmd()

    try:
        if node.simulate:
            run_simulate(node)
        else:
            asyncio.run(run_with_moteus(node))
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
