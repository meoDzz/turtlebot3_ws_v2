
# TurtleBot3 Robot Operation Guide

## Prerequisites
Before running any commands, set the robot model:
```bash
export TURTLEBOT3_MODEL=burger
```

---

## 1. Robot Bringup & Hardware Setup

### 1.1 Start Hardware Communication (ESP)
Initialize velocity subscription and ESP communication:
```bash
cd /home/radxa/turtlebot3_ws/src/turtlebot3/turtlebot3_bringup/launch
python3 sub_velocity.py
```

### 1.2 Launch Robot Bringup
Brings up all robot hardware drivers and base control:
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_bringup robot.launch.py
```

---

## 2. Mapping & Localization

### 2.1 SLAM with Cartographer
Launch simultaneous localization and mapping (SLAM) for creating a new map:
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=False
```
**Use this to generate a map of your environment by driving the robot around.**

---

## 3. Navigation

### 3.0 Run Esp connection for motor
```bash
cd /home/radxa/turtlebot3_ws/src/turtlebot3/turtlebot3_bringup/launch
python3 sub_velocity.py
```
### 3.1 Run Cartographer
```bash
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=False
```
### 3.1 Launch Navigation Stack
Initialize the navigation stack with an existing map:
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_navigation2 navigation2.launch.py acml:=false use_sim_time:=False map:=/home/radxa/turtlebot3_ws/map/map_2.yaml
```
**Provides autonomous navigation capabilities with the specified map.**

### 3.2 Set Initial Pose
Define the robot's starting position on the map:
```bash
export TURTLEBOT3_MODEL=burger
ros2 run robot_base_interface set_init_pose
```

### 3.3 Send Goal Pose
Command the robot to navigate to a specific goal location:
```bash
export TURTLEBOT3_MODEL=burger
ros2 run robot_base_interface send_goal
```

---

## 4. On the **Laptop**, set the TurtleBot 3 model and launch RViz for navigation:

```bash
export TURTLEBOT3_MODEL=burger
source /opt/ros/jazzy/setup.bash
ros2 launch nav2_bringup rviz_launch.py
```


## 5. Teleoperation & Manual Control

### 5.1 Keyboard Teleop Control
Operate the robot manually using keyboard commands:
```bash
export TURTLEBOT3_MODEL=burger
ros2 run turtlebot3_teleop teleop_keyboard
```

---

## 6. Monitoring & Debugging

### 6.1 Monitor Velocity Commands
View the velocity commands being sent to the robot:
```bash
ros2 topic echo /cmd_vel
```

### 6.2 Monitor Clicked Points
Track navigation goals selected on the map:
```bash
ros2 topic echo /clicked_point
```

---

## Typical Workflow

1. **Hardware Setup**: Run bringup and ESP communication
2. **Mapping**: Use Cartographer to create or update your map
3. **Navigation**: Launch navigation stack with your map
4. **Operation**: Set initial pose → Send goals OR use teleop for manual control
5. **Monitoring**: Use echo commands to debug topics as needed