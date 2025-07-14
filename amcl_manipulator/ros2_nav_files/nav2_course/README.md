# nav2_course

The `nav2_course` package is an example bringup system for Navigation2 applications.

### Pre-requisites:
* [Install ROS 2](https://index.ros.org/doc/ros2/Installation/Eloquent/)
* Install Navigation2

    ```sudo apt install ros-<ros2_distro>-navigation2```

* Install Navigation2 Bringup

    ```sudo apt install ros-<ros2_distro>-nav2-bringup```

* Install your robot specific package (ex:[Turtlebot 3](http://emanual.robotis.com/docs/en/platform/turtlebot3/ros2/))

## Launch Navigation2 in *Simulation* with Gazebo
### Pre-requisites:

* [Install Gazebo](http://gazebosim.org/tutorials?tut=install_ubuntu&cat=install)
* gazebo_ros_pkgs for ROS2 installed on the system

    ```sudo apt-get install ros-<ros2-distro>-gazebo*```
* A Gazebo world for simulating the robot ([Gazebo tutorials](http://gazebosim.org/tutorials?tut=quick_start))
* A map of that world saved to a map.pgm and map.yaml ([ROS Navigation Tutorials](https://github.com/ros-planning/navigation2/tree/master/doc/use_cases))
