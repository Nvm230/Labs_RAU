#!/usr/bin/env python3
"""
moteus_bridge - Subscriber that reads /cmd_vel, applies inverse kinematics,
and sends wheel velocities to Moteus motor controllers.

Subscribes:
    /cmd_vel (geometry_msgs/Twist) - desired robot velocity

Drives:
    Moteus Controller id=1 → left wheel  (ωL)
    Moteus Controller id=2 → right wheel (ωR)

Inverse Kinematics:
    ωR = (v + ω * L/2) / R
    ωL = (v - ω * L/2) / R

    Moteus velocity is in [rev/s], so we convert: vel_revs = ω / (2π)
"""

import math
import sys

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

import asyncio
import moteus


class MoteusBridge(Node):
    def __init__(self):
        super().__init__('moteus_bridge')

        # ============ Robot Parameters ============
        self.declare_parameter('wheel_separation', 0.20)   # L [m]
        self.declare_parameter('wheel_radius', 0.06)        # R [m]

        self.L = self.get_parameter('wheel_separation').value
        self.R = self.get_parameter('wheel_radius').value

        # ============ Motor state ============
        self.omega_left = 0.0    # [rad/s]
        self.omega_right = 0.0   # [rad/s]

        # ============ Subscriber ============
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)

        self.get_logger().info(
            f'moteus_bridge initialized: L={self.L}m, R={self.R}m')

    def cmd_vel_callback(self, msg: Twist):
        """
        Inverse kinematics: (v, ω) → (ωL, ωR)
        """
        v = msg.linear.x
        omega = msg.angular.z

        # Inverse kinematics
        self.omega_right = (v + omega * self.L / 2.0) / self.R
        self.omega_left = (v - omega * self.L / 2.0) / self.R

        self.get_logger().info(
            f'v={v:.3f}, ω={omega:.3f} → '
            f'ωL={self.omega_left:.3f} rad/s, ωR={self.omega_right:.3f} rad/s',
            throttle_duration_sec=1.0)


async def run_moteus(node):
    """
    Async loop: reads wheel velocities from the node
    and sends them to moteus controllers.
    """
    rate = 50  # Hz

    # Connect to moteus controllers
    transport = moteus.Fdcanusb()
    c1 = moteus.Controller(id=1)  # Left wheel
    c2 = moteus.Controller(id=2)  # Right wheel

    # Stop motors initially
    await transport.cycle([c1.make_stop(), c2.make_stop()])
    node.get_logger().info('Moteus motors connected and stopped.')

    try:
        while rclpy.ok():
            # Spin ROS once to process callbacks
            rclpy.spin_once(node, timeout_sec=0.0)

            # Convert rad/s → rev/s for moteus
            vel_left = node.omega_left / (2.0 * math.pi)
            vel_right = node.omega_right / (2.0 * math.pi)

            # Send to motors
            result = await transport.cycle([
                c1.make_position(
                    position=math.nan,
                    velocity=vel_left,
                    query=True),
                c2.make_position(
                    position=math.nan,
                    velocity=vel_right,
                    query=True),
            ])

            await asyncio.sleep(1.0 / rate)

    except KeyboardInterrupt:
        pass
    finally:
        await transport.cycle([c1.make_stop(), c2.make_stop()])
        node.get_logger().info('Motors stopped.')


def main(args=None):
    rclpy.init(args=args)
    node = MoteusBridge()
    try:
        asyncio.run(run_moteus(node))
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
