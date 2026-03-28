#!/bin/bash

# Đường dẫn tới workspace của bạn
WS_PATH="/home/radxa/turtlebot3_ws"
MAP_PATH="/home/radxa/turtlebot3_ws/map/map_2.yaml"

echo "Đang khởi động hệ thống Robot Roofi..."

# 1. Terminal 1: Giao tiếp ESP (Velocity Subscriber)
gnome-terminal --tab --title="ESP_Comm" -- bash -c "
source /opt/ros/jazzy/setup.bash;
source $WS_PATH/install/setup.bash;
cd $WS_PATH/src/turtlebot3/turtlebot3_bringup/launch;
python3 sub_velocity.py;
exec bash"

sleep 2

# 2. Terminal 2: Robot Bringup
gnome-terminal --tab --title="Bringup" -- bash -c "
export TURTLEBOT3_MODEL=burger;
source /opt/ros/jazzy/setup.bash;
source $WS_PATH/install/setup.bash;
ros2 launch turtlebot3_bringup robot.launch.py;
exec bash"

sleep 3

# 3. Terminal 3: Navigation 2 (Chạy với Map có sẵn)
gnome-terminal --tab --title="Navigation" -- bash -c "
export TURTLEBOT3_MODEL=burger;
source /opt/ros/jazzy/setup.bash;
source $WS_PATH/install/setup.bash;
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=False map:=$MAP_PATH;
exec bash"

sleep 5

# 4. Terminal 4: Set Initial Pose
gnome-terminal --tab --title="InitialPose" -- bash -c "
source /opt/ros/jazzy/setup.bash;
source $WS_PATH/install/setup.bash;
ros2 run robot_base_interface set_init_pose;
exec bash"

echo "Tất cả các terminal đã được mở!"