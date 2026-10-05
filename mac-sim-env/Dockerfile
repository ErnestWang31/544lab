# MTE544 dev environment: Ubuntu 22.04 + ROS 2 Humble desktop + TurtleBot3 sim,
# with a browser-accessible desktop (noVNC) so Gazebo/RViz work on macOS.
# Built as linux/amd64 (see setup.sh): Gazebo Classic has no arm64 packages for Humble.
FROM --platform=linux/amd64 tiryoh/ros2-desktop-vnc:humble

USER root
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-humble-gazebo-ros-pkgs \
        ros-humble-turtlebot3 \
        ros-humble-turtlebot3-msgs \
        ros-humble-turtlebot3-simulations \
        ros-humble-teleop-twist-keyboard \
        ros-humble-slam-toolbox \
        ros-humble-nav2-map-server \
        python3-matplotlib \
        python3-numpy \
        git nano \
    && rm -rf /var/lib/apt/lists/*

# Environment for every new terminal (system-wide: the desktop user is only created at container start)
RUN { \
      echo 'source /opt/ros/humble/setup.bash'; \
      echo '[ -f /usr/share/gazebo/setup.sh ] && source /usr/share/gazebo/setup.sh'; \
      echo 'export TURTLEBOT3_MODEL=burger'; \
      echo 'export ROS_DOMAIN_ID=0'; \
      echo 'export LIBGL_ALWAYS_SOFTWARE=1   # no GPU in the container'; \
      echo 'cd /mte544 2>/dev/null || true'; \
    } >> /etc/bash.bashrc
