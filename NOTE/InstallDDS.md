# Installing and Configuring CycloneDDS for ROS 2 on TurtleBot 3

## Introduction

This guide explains how to install and configure CycloneDDS, a DDS (Data Distribution Service) implementation, for ROS 2 on a TurtleBot 3 setup. DDS enables efficient communication between ROS 2 nodes across different machines, such as a Radxa board (robot) and a laptop (control station). This is particularly useful for multi-machine ROS 2 deployments.

## Prerequisites

- ROS 2 Jazzy installed on both machines (Radxa and Laptop).
- Network connectivity between the Radxa and Laptop.
- Basic knowledge of ROS 2 commands and environment variables.

## Installation

### 1. Install CycloneDDS RMW Implementation

On the Radxa (robot) and Laptop, install the CycloneDDS C++ RMW (ROS Middleware) package:

```bash
sudo apt update
sudo apt install ros-jazzy-rmw-cyclonedds-cpp
```

This package provides the ROS 2 interface to CycloneDDS.

## Configuration

### 1. Edit the Bashrc File

Open the `.bashrc` file for editing:

```bash
nano ~/.bashrc
```

### 2. Add ROS 2 Environment Variables

Append the following lines to the end of `.bashrc` to configure ROS 2 to use CycloneDDS:

```bash
# ROS 2 Environment Setup for CycloneDDS
export ROS_DOMAIN_ID=30  # Unique domain ID for your ROS 2 network
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp  # Specify CycloneDDS as the RMW
```

### 3. Configure CycloneDDS for Multi-Machine Communication

To enable discovery between the Radxa and Laptop, add the peer address. Replace `IP_LAPTOP_CUA_BAN` with the actual IP address of your Laptop:

```bash
# CycloneDDS Configuration (Point to Laptop's IP for peer discovery)
export CYCLONEDDS_URI='<CycloneDDS><Domain><Discovery><Peers><Peer address="IP_LAPTOP_CUA_BAN"/></Peers></Discovery></Domain></CycloneDDS>'
```

**Note:** Ensure the IP address is static or use a reliable network setup. You may need to add the Radxa's IP as a peer on the Laptop's configuration as well, depending on your network topology.

### 4. Source the Updated Bashrc

After saving the changes, source the file to apply them:

```bash
source ~/.bashrc
```

## Testing the Setup

### 1. Basic Communication Test

- On the **Radxa** (robot), run the talker node:

```bash
ros2 run demo_nodes_cpp talker
```

- On the **Laptop**, run the listener node:

```bash
ros2 run demo_nodes_cpp listener
```

You should see messages being published from the talker and received by the listener across machines.

### 2. Verify Environment Variables

Check that the variables are set correctly:

```bash
echo $ROS_DOMAIN_ID  # Should output: 30
echo $RMW_IMPLEMENTATION  # Should output: rmw_cyclonedds_cpp
echo $CYCLONEDDS_URI  # Should display the XML with the peer IP
```

## Usage with TurtleBot 3

### Running Navigation on Laptop

On the **Laptop**, set the TurtleBot 3 model and launch RViz for navigation:

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch nav2_bringup rviz_launch.py
```

### Running on Radxa

On the **Radxa**, run standard ROS 2 commands for the robot, such as launching bringup or other nodes. Ensure the environment is sourced.

## Troubleshooting

- **No communication:** Verify IP addresses, firewall settings, and that both machines are on the same network.
- **RMW not recognized:** Ensure the package is installed and the environment is sourced.
- **Discovery issues:** Check the CYCLONEDDS_URI for correct IP and XML syntax.
- **Domain ID conflicts:** Use a unique ROS_DOMAIN_ID if multiple ROS 2 networks exist.

## Additional Notes

- Restart terminals or source `.bashrc` after changes.
- For production, consider using more advanced DDS configurations for security and performance.
- Refer to the [ROS 2 DDS documentation](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Different-Middleware-Vendors.html) for more details.