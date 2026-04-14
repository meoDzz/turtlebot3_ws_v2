#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class ImuTfNode(Node):
    def __init__(self):
        super().__init__('imu_tf_node')

        self.br = TransformBroadcaster(self)

        self.sub = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )

        self.parent_frame = 'world'
        self.child_frame = 'imu_viz'

        self.get_logger().info('Dang publish TF dong: world -> imu_viz')

    def imu_callback(self, msg: Imu):
        t = TransformStamped()
        t.header.stamp = msg.header.stamp
        t.header.frame_id = self.parent_frame
        t.child_frame_id = self.child_frame

        # Giữ nguyên vị trí gốc, chỉ cho quay
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.0

        t.transform.rotation = msg.orientation

        self.br.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = ImuTfNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
