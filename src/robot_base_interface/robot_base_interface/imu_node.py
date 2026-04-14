# import rclpy
# from rclpy.node import Node
# from sensor_msgs.msg import Imu
# from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
# import smbus2
# import time

# # class MPU6050Node(Node):
# #     def __init__(self):
# #         super().__init__('imu_node')
# #         self.publisher_ = self.create_publisher(Imu, 'imu/data_raw', 10)
        
# #         # Kết nối I2C (Bus 0 như bạn đã check)
# #         self.bus = smbus2.SMBus(0)
# #         self.address = 0x68
        
# #         # Đánh thức MPU6050 (Ghi 0 vào thanh ghi Power Management 1)
# #         self.bus.write_byte_data(self.address, 0x6b, 0)
        
# #         self.get_logger().info('Cảm biến IMU đã sẵn sàng trên Bus 0!')
# #         self.timer = self.create_timer(0.05, self.publish_imu) # 20Hz
# #         qos_profile = QoSProfile(
# #         reliability=ReliabilityPolicy.BEST_EFFORT, # Không gửi lại nếu mất gói
# #         history=HistoryPolicy.KEEP_LAST,
# #         depth=10 # Chỉ giữ lại 10 tin nhắn mới nhất trong hàng đợi
# #         )

# #     def read_raw_data(self, addr):
# #         # Đọc 2 byte (High và Low) rồi ghép lại
# #         high = self.bus.read_byte_data(self.address, addr)
# #         low = self.bus.read_byte_data(self.address, addr + 1)
# #         val = (high << 8) | low
# #         if val > 32768:
# #             val = val - 65536
# #         return val

# #     def publish_imu(self):
# #         msg = Imu()
# #         msg.header.stamp = self.get_clock().now().to_msg()
# #         msg.header.frame_id = 'imu_link'

# #         # Đơn vị đo: Gia tốc (g) chuyển sang m/s^2 (chia cho 16384.0 rồi nhân 9.80665)
# #         # Vận tốc góc chuyển sang rad/s (chia cho 131.0 rồi chuyển sang radian)
# #         acc_scale = 16384.0
# #         msg.linear_acceleration.x = (self.read_raw_data(0x3b) / acc_scale) * 9.80665
# #         msg.linear_acceleration.y = (self.read_raw_data(0x3d) / acc_scale) * 9.80665
# #         msg.linear_acceleration.z = (self.read_raw_data(0x3f) / acc_scale) * 9.80665

# #         gyro_scale = 131.0
# #         msg.angular_velocity.x = (self.read_raw_data(0x43) / gyro_scale) * (3.14159 / 180.0)
# #         msg.angular_velocity.y = (self.read_raw_data(0x45) / gyro_scale) * (3.14159 / 180.0)
# #         msg.angular_velocity.z = (self.read_raw_data(0x47) / gyro_scale) * (3.14159 / 180.0)

# #         self.publisher_.publish(msg)


# class MPU6050Node(Node):
#     def __init__(self):
#         super().__init__('imu_node')
        
#         # Thiết lập QoS chuẩn cho IMU
#         qos_profile = QoSProfile(
#             reliability=ReliabilityPolicy.BEST_EFFORT,
#             history=HistoryPolicy.KEEP_LAST,
#             depth=10
#         )
        
#         # Đổi topic thành /imu/data_raw để Madgwick nhận diện đúng bản chất
#         self.publisher_ = self.create_publisher(Imu, '/imu/data_raw', qos_profile)
        
#         self.bus = smbus2.SMBus(0)
#         self.address = 0x68
#         self.bus.write_byte_data(self.address, 0x6b, 0)
        
#         self.get_logger().info('MPU6050 Raw Data Node đã chạy!')
        
#         # Tăng lên 50Hz (0.02s) để Cartographer mượt hơn
#         self.timer = self.create_timer(0.02, self.publish_imu) 

#     def read_raw_data(self, addr):
#         try:
#             high = self.bus.read_byte_data(self.address, addr)
#             low = self.bus.read_byte_data(self.address, addr + 1)
#             val = (high << 8) | low
#             return val - 65536 if val > 32768 else val
#         except:
#             return 0

#     def publish_imu(self):
#         msg = Imu()
#         msg.header.stamp = self.get_clock().now().to_msg()
#         msg.header.frame_id = 'imu_link'

#         # Đọc gia tốc (m/s^2)
#         acc_scale = 16384.0
#         msg.linear_acceleration.x = (self.read_raw_data(0x3b) / acc_scale) * 9.80665
#         msg.linear_acceleration.y = (self.read_raw_data(0x3d) / acc_scale) * 9.80665
#         msg.linear_acceleration.z = (self.read_raw_data(0x3f) / acc_scale) * 9.80665

#         # Đọc vận tốc góc (rad/s)
#         gyro_scale = 131.0
#         msg.angular_velocity.x = (self.read_raw_data(0x43) / gyro_scale) * (3.14159 / 180.0)
#         msg.angular_velocity.y = (self.read_raw_data(0x45) / gyro_scale) * (3.14159 / 180.0)
#         msg.angular_velocity.z = (self.read_raw_data(0x47) / gyro_scale) * (3.14159 / 180.0)

#         # Gán covariance nhỏ để bộ lọc không bỏ qua dữ liệu (Quan trọng cho Cartographer)
#         msg.linear_acceleration_covariance = [0.01] * 9
#         msg.angular_velocity_covariance = [0.01] * 9

#         self.publisher_.publish(msg)


# def main(args=None):
#     rclpy.init(args=args)
#     node = MPU6050Node()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass
#     node.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()

#------------------------------------------------------------------------
#!/usr/bin/env python3

import math
import time
import smbus2

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy


class MPU6050Node(Node):
    def __init__(self):
        super().__init__('imu_node')

        # [FIX 1] QoS kiểu cảm biến
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # [FIX 2] Publish đúng topic raw IMU
        self.publisher_ = self.create_publisher(Imu, '/imu/data_raw', qos_profile)

        # [FIX 3] Khởi tạo I2C + MPU6050
        self.bus = smbus2.SMBus(0)   # Bus 0 theo phần cứng của bạn
        self.address = 0x68
        self.last_i2c_error_time = 0.0

        # Wake up MPU6050
        self.write_register(0x6B, 0x00)

        # Chọn full-scale mặc định:
        # Gyro ±250 deg/s  -> reg 0x1B = 0x00
        # Accel ±2g        -> reg 0x1C = 0x00
        self.write_register(0x1B, 0x00)
        self.write_register(0x1C, 0x00)

        time.sleep(0.1)

        # Scale theo full-scale ở trên
        self.acc_scale = 16384.0
        self.gyro_scale = 131.0

        # [FIX 4] Offset gyro để giảm drift
        self.gx_offset = 0.0
        self.gy_offset = 0.0
        self.gz_offset = 0.0

        self.get_logger().info('Dang hieu chuan gyro, giu IMU dung yen...')
        self.calibrate_gyro(samples=300)
        self.get_logger().info(
            f'Gyro offset: gx={self.gx_offset:.2f}, gy={self.gy_offset:.2f}, gz={self.gz_offset:.2f}'
        )

        self.get_logger().info('MPU6050 Raw Data Node da chay! Publishing /imu/data_raw')

        # 50 Hz
        self.timer = self.create_timer(0.02, self.publish_imu)

    def write_register(self, reg, value):
        self.bus.write_byte_data(self.address, reg, value)

    def read_raw_data(self, reg):
        try:
            high = self.bus.read_byte_data(self.address, reg)
            low = self.bus.read_byte_data(self.address, reg + 1)
            value = (high << 8) | low
            if value > 32767:
                value -= 65536
            return value
        except Exception as e:
            # [FIX 5] Không nuốt lỗi hoàn toàn, nhưng cũng tránh spam log liên tục
            now = time.time()
            if now - self.last_i2c_error_time > 2.0:
                self.get_logger().error(f'Loi doc I2C tai reg {hex(reg)}: {e}')
                self.last_i2c_error_time = now
            return 0

    def calibrate_gyro(self, samples=300):
        sum_gx = 0.0
        sum_gy = 0.0
        sum_gz = 0.0

        for _ in range(samples):
            sum_gx += self.read_raw_data(0x43)
            sum_gy += self.read_raw_data(0x45)
            sum_gz += self.read_raw_data(0x47)
            time.sleep(0.005)

        self.gx_offset = sum_gx / samples
        self.gy_offset = sum_gy / samples
        self.gz_offset = sum_gz / samples

    def publish_imu(self):
        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'

        # [FIX 6] Node này KHÔNG tính orientation
        # Phải khai báo orientation không có dữ liệu theo chuẩn ROS
        msg.orientation.x = 0.0
        msg.orientation.y = 0.0
        msg.orientation.z = 0.0
        msg.orientation.w = 1.0
        msg.orientation_covariance = [
            -1.0, 0.0, 0.0,
             0.0, 0.0, 0.0,
             0.0, 0.0, 0.0
        ]

        # Accelerometer -> m/s^2
        ax_raw = self.read_raw_data(0x3B)
        ay_raw = self.read_raw_data(0x3D)
        az_raw = self.read_raw_data(0x3F)

        msg.linear_acceleration.x = (ax_raw / self.acc_scale) * 9.80665
        msg.linear_acceleration.y = (ay_raw / self.acc_scale) * 9.80665
        msg.linear_acceleration.z = (az_raw / self.acc_scale) * 9.80665

        # Gyroscope -> rad/s, có trừ offset
        gx_raw = self.read_raw_data(0x43) - self.gx_offset
        gy_raw = self.read_raw_data(0x45) - self.gy_offset
        gz_raw = self.read_raw_data(0x47) - self.gz_offset

        msg.angular_velocity.x = (gx_raw / self.gyro_scale) * (math.pi / 180.0)
        msg.angular_velocity.y = (gy_raw / self.gyro_scale) * (math.pi / 180.0)
        msg.angular_velocity.z = (gz_raw / self.gyro_scale) * (math.pi / 180.0)

        # [FIX 7] Covariance sửa thành ma trận chéo đúng nghĩa
        msg.angular_velocity_covariance = [
            0.01, 0.0,  0.0,
            0.0,  0.01, 0.0,
            0.0,  0.0,  0.01
        ]

        msg.linear_acceleration_covariance = [
            0.10, 0.0,  0.0,
            0.0,  0.10, 0.0,
            0.0,  0.0,  0.10
        ]

        self.publisher_.publish(msg)

    def destroy_node(self):
        # [FIX 8] Đóng I2C bus khi tắt node
        try:
            self.bus.close()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MPU6050Node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()