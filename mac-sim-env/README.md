# MTE544 environment on macOS (ROS 2 Humble + TurtleBot3 sim)

ROS 2 Humble doesn't run natively on macOS, so this runs Ubuntu 22.04 in Docker with a
desktop you open in your browser. Gazebo and RViz run inside that desktop.

## One-time setup

Quick way: `cd` into this folder and run `bash setup.sh`. It installs Docker Desktop if it's missing, then builds, starts and opens everything. The manual steps follow.

1. Install **Docker Desktop for Mac** (docker.com). In Settings → Resources, give it
   at least **4 CPUs and 8 GB RAM**. Gazebo is CPU-heavy because it renders in software.
2. Unzip this folder somewhere, e.g. `~/mte544-env`. Your lab repo is already inside
   it at `workspace/MTE544_student`.
3. In Terminal:
   ```bash
   cd ~/mte544-env
   docker compose up -d --build     # first build takes ~10–15 min
   ```
4. Open **http://localhost:6080** and click Connect. You'll see an Ubuntu desktop.

## Daily use

- Start: `docker compose up -d`. Stop: `docker compose stop`.
- Edit code on your Mac in `workspace/` with VS Code etc. It's the same folder as
  `/mte544` inside the container, so changes show up instantly and logged CSVs land on your Mac.
- Open terminals inside the browser desktop (Terminal Emulator in the menu). ROS is
  already sourced and `TURTLEBOT3_MODEL=burger` is set.

## Running Lab 1 in sim

Terminal 1, simulator:
```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```
Terminal 2, sanity check, then run your code:
```bash
ros2 topic list                       # expect /cmd_vel /odom /imu /scan
ros2 topic info /odom --verbose       # check QoS (Part 3)
cd /mte544/MTE544_student
python3 motions.py --motion circle    # Ctrl+C stops the robot
python3 filePlotter.py --files odom_content_circle.csv
```
Reset the robot between runs: Gazebo menu Edit → Reset World.

Part 8 map in sim:
```bash
ros2 launch slam_toolbox online_sync_launch.py                 # terminal 2
ros2 launch turtlebot3_bringup rviz2.launch.py                 # terminal 3, add Map display on /map
ros2 run turtlebot3_teleop teleop_keyboard                     # terminal 4
ros2 run nav2_map_server map_saver_cli -f /mte544/map         # when done
```

## Notes

- `turtlebot3_house` is heavy under software rendering. `turtlebot3_world` loads much faster.
- If Gazebo dies on start, run `killall gzserver gzclient` and relaunch.
- This setup is for sim only. The real TB4s are used from the lab PCs, per the course rules.
