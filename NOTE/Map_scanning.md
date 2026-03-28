 # Setup Cartographer ROS2 + LIDAR C1

 ## 1. Install Cartographer Jazzy
 ```
 sudo apt update
sudo apt install ros-jazzy-cartographer ros-jazzy-cartographer-ros -y
 ```

## 2. Create **.lua** for hand held function (no encoder)

```
mkdir -p /home/radxa/ros2_ws/scripts/ConfigSLAM

cd ~/ros2_ws/scripts/ConfigSLAM
nano handheld_jazzy.lua
```
Copy and paste the below script to **handheld_jazzy.lua** the save the file

```
include "map_builder.lua"
include "trajectory_builder.lua"

options = {
  map_builder = MAP_BUILDER,
  trajectory_builder = TRAJECTORY_BUILDER,
  map_frame = "map",
  tracking_frame = "base_link",               -- Đổi thành "base_link" nếu KHÔNG có IMU ổn định
  published_frame = "base_link",             -- Frame chính publish pose (thay nếu cần)
  odom_frame = "odom",                       -- Chỉ dùng nếu provide_odom_frame = true
  provide_odom_frame = false,                -- Tắt vì không có odom thật
  publish_frame_projected_to_2d = true,      -- Rất quan trọng cho 2D handheld
  use_odometry = false,                      -- Tắt odometry hoàn toàn
  use_nav_sat = false,
  use_landmarks = false,
  num_laser_scans = 1,
  num_multi_echo_laser_scans = 0,
  num_subdivisions_per_laser_scan = 1,
  num_point_clouds = 0,
  lookup_transform_timeout_sec = 0.2,
  submap_publish_period_sec = 0.3,
  pose_publish_period_sec = 5e-3,
  trajectory_publish_period_sec = 30e-3,
  rangefinder_sampling_ratio = 1.,
  odometry_sampling_ratio = 1.,
  fixed_frame_pose_sampling_ratio = 1.,
  imu_sampling_ratio = 1.,
  landmarks_sampling_ratio = 1.,
}

MAP_BUILDER.use_trajectory_builder_2d = true

TRAJECTORY_BUILDER_2D.min_range = 0.12
TRAJECTORY_BUILDER_2D.max_range = 3.5
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 3.
TRAJECTORY_BUILDER_2D.use_imu_data = false          -- Nếu có IMU tốt, bật true và publish /imu
TRAJECTORY_BUILDER_2D.use_online_correlative_scan_matching = true  -- Bật để matching realtime tốt hơn khi không có odom
TRAJECTORY_BUILDER_2D.motion_filter.max_angle_radians = math.rad(0.1)

-- Tinh chỉnh cho handheld (giảm drift khi di chuyển tay)
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.translation_weight = 10.0   -- Tăng nếu drift tịnh tiến
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.rotation_weight = 40.0      -- Tăng để xoay chính xác hơn

-- Pose graph (loop closure)
POSE_GRAPH.constraint_builder.min_score = 0.65
POSE_GRAPH.constraint_builder.global_localization_min_score = 0.7
POSE_GRAPH.optimize_every_n_nodes = 30          -- Optimize thường xuyên hơn cho handheld
POSE_GRAPH.global_sampling_ratio = 0.003

return options

```

# Run the map_builder

# 0. Run essp connection
```bash
cd /home/radxa/turtlebot3_ws/src/turtlebot3/turtlebot3_bringup/launch
python3 sub_velocity.py
```

# 1. Start lidar
```
cd ros2_ws
source install/setup.bash
ros2 launch sllidar_ros2 sllidar_c1_launch.py serial_port:=/dev/lidar serial_baudrate:=460800
```


## 2. Link the base_link to laser origin
```
ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --yaw 0 --pitch 0 --roll 0 --frame-id base_link --child-frame-id laser
```
Then check the link between the node
```
ros2 run tf2_tools view_frames
```
The link should be map -> base_link -> laser

## 3. Run cartographer_ros resolution
```
ros2 run cartographer_ros cartographer_occupancy_grid_node -resolution 0.05
```

## 4. Run
```
ros2 run cartographer_ros cartographer_node -configuration_directory ~/ros2_ws/scripts/ConfigSLAM -configuration_basename handheld_jazzy.lua --ros-args -p use_sim_time:=false
```
If you see this [INFO] => DONE
```
[INFO] [1770993615.726220563] [cartographer logger]: I20260213 21:40:15.-2147483648  6373 configuration_file_resolver.cc:41] Found '/opt/ros/jazzy/share/cartographer/configuration_files/trajectory_builder.lua' for 'trajectory_builder.lua'.

```

## 5. Run rviz2
```
ros2 run rviz2 rviz2
```
Remember increase the value of DEPTH = 10 in topic MAP


## 6. Run telerobot
```bash
ros2 run turtlebot3_teleop teleop_keyboard
```

## 6. Save the map
Image check
```
ros2 run nav2_map_server map_saver_cli -f /home/radxa/turtlebot3_ws/map/map_2
```

pbstream
```
ros2 service call /finish_trajectory cartographer_ros_msgs/srv/FinishTrajectory "{trajectory_id: 0}"
```
```
ros2 service call /write_state cartographer_ros_msgs/srv/WriteState "{filename: '/home/radxa/ros2_ws/scripts/Map_Scan/my_map.pbstream', include_unfinished_submaps: false}"
```
Convert to pgm yaml
```
ros2 run cartographer_ros cartographer_pbstream_to_ros_map \
  -map_filestem=/home/radxa/ros2_ws/scripts/Map_Scan \
  -pbstream_filename=/home/radxa/ros2_ws/scripts/Map_Scan/my_map.pbstream \
  -resolution=0.05
```
