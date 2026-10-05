# Imports
import rclpy

from rclpy.node import Node

from utilities import Logger, euler_from_quaternion
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy

# TODO Part 3: Import message types needed:
    # For sending velocity commands to the robot: Twist
    # For the sensors: Imu, LaserScan, and Odometry
# Check the online documentation to fill in the lines below
from geometry_msgs.msg import Twist     # /cmd_vel
from sensor_msgs.msg import Imu         # /imu
from sensor_msgs.msg import LaserScan   # /scan
from nav_msgs.msg import Odometry       # /odom

from rclpy.time import Time

# You may add any other imports you may need/want to use below
import sys


CIRCLE=0; SPIRAL=1; ACC_LINE=2
motion_types=['circle', 'spiral', 'line']

class motion_executioner(Node):

    # Tunable motion parameters. Kept below the TB3 Burger limits (0.22 m/s, 2.84 rad/s);
    # the TB4 allows a bit more (~0.31 m/s) but the classroom is small. Tune in-lab.
    CIRCLE_V=0.15        # [m/s]
    CIRCLE_W=0.5         # [rad/s]  -> radius = v/w = 0.3 m

    SPIRAL_W=0.6         # [rad/s]  constant yaw rate
    SPIRAL_V0=0.02       # [m/s]    starting forward speed
    SPIRAL_ACC=0.01      # [m/s^2]  forward-speed ramp -> radius grows over time
    SPIRAL_V_MAX=0.22    # [m/s]    cap (radius stops growing at v_max/w ~ 0.37 m)

    LINE_ACC=0.02        # [m/s^2]  constant acceleration from rest
    LINE_V_MAX=0.22      # [m/s]    cap, then cruise at constant speed

    def __init__(self, motion_type=0):

        super().__init__("motion_types")

        self.type=motion_type

        self.radius_=0.0

        self.successful_init=False
        self.imu_initialized=False
        self.odom_initialized=False
        self.laser_initialized=False

        # TODO Part 3: Create a publisher to send velocity commands by setting the proper parameters in (...)
        # Twist messages on /cmd_vel with a queue depth of 10
        self.vel_publisher=self.create_publisher(Twist, '/cmd_vel', 10)

        # Motion bookkeeping: timer ticks since the motion started (timer runs at 10 Hz)
        self.tick_count=0
        self.dt=0.1

        # loggers
        self.imu_logger=Logger('imu_content_'+str(motion_types[motion_type])+'.csv', headers=["acc_x", "acc_y", "angular_z", "stamp"])
        self.odom_logger=Logger('odom_content_'+str(motion_types[motion_type])+'.csv', headers=["x","y","th", "stamp"])
        self.laser_logger=Logger('laser_content_'+str(motion_types[motion_type])+'.csv', headers=["ranges", "angle_increment", "stamp"])

        # TODO Part 3: Create the QoS profile by setting the proper parameters in (...)
        # The TB4 sensor topics (/imu, /odom, /scan) are published BEST_EFFORT. A BEST_EFFORT
        # subscriber is compatible with both BEST_EFFORT and RELIABLE publishers, so this one
        # profile works on the real TurtleBot 4 and on the TurtleBot 3 simulation.
        # (Verify with: ros2 topic info /odom --verbose)
        qos=QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                       durability=DurabilityPolicy.VOLATILE,
                       history=HistoryPolicy.KEEP_LAST,
                       depth=10)

        # TODO Part 5: Create below the subscription to the topics corresponding to the respective sensors
        # IMU subscription
        self.create_subscription(Imu, '/imu', self.imu_callback, qos)

        # ENCODER subscription
        self.create_subscription(Odometry, '/odom', self.odom_callback, qos)

        # LaserScan subscription
        self.create_subscription(LaserScan, '/scan', self.laser_callback, qos)

        self.create_timer(self.dt, self.timer_callback)


    # TODO Part 5: Callback functions: complete the callback functions of the three sensors to log the proper data.
    # To also log the time you need to use the rclpy Time class, each ros msg will come with a header, and then
    # inside the header you have a stamp that has the time in seconds and nanoseconds, you should log it in nanoseconds as
    # such: Time.from_msg(imu_msg.header.stamp).nanoseconds
    # You can save the needed fields into a list, and pass the list to the log_values function in utilities.py

    def imu_callback(self, imu_msg: Imu):
        """Log planar IMU data: linear acceleration x/y [m/s^2], yaw rate [rad/s], stamp [ns]."""
        acc_x=imu_msg.linear_acceleration.x
        acc_y=imu_msg.linear_acceleration.y
        angular_z=imu_msg.angular_velocity.z
        stamp=Time.from_msg(imu_msg.header.stamp).nanoseconds

        self.imu_logger.log_values([acc_x, acc_y, angular_z, stamp])
        self.imu_initialized=True   # first message received -> sensor is alive

    def odom_callback(self, odom_msg: Odometry):
        """Log wheel-odometry pose: x, y [m], yaw th [rad] (from the quaternion), stamp [ns]."""
        pos=odom_msg.pose.pose.position
        q=odom_msg.pose.pose.orientation
        th=euler_from_quaternion([q.x, q.y, q.z, q.w])
        stamp=Time.from_msg(odom_msg.header.stamp).nanoseconds

        self.odom_logger.log_values([pos.x, pos.y, th, stamp])
        self.odom_initialized=True

    def laser_callback(self, laser_msg: LaserScan):
        """Log the full range array [m], the angular step between beams [rad], and stamp [ns].
        The ranges list is written as one space-separated field (see Logger.log_values).
        inf/nan readings are kept here and cleaned during post-processing."""
        ranges=list(laser_msg.ranges)
        stamp=Time.from_msg(laser_msg.header.stamp).nanoseconds

        self.laser_logger.log_values([ranges, laser_msg.angle_increment, stamp])
        self.laser_initialized=True

    def timer_callback(self):

        if self.odom_initialized and self.laser_initialized and self.imu_initialized:
            self.successful_init=True

        if not self.successful_init:
            return

        cmd_vel_msg=Twist()

        if self.type==CIRCLE:
            cmd_vel_msg=self.make_circular_twist()

        elif self.type==SPIRAL:
            cmd_vel_msg=self.make_spiral_twist()

        elif self.type==ACC_LINE:
            cmd_vel_msg=self.make_acc_line_twist()

        else:
            print("type not set successfully, 0: CIRCLE 1: SPIRAL and 2: ACCELERATED LINE")
            raise SystemExit

        self.vel_publisher.publish(cmd_vel_msg)
        self.tick_count+=1

    def stop(self):
        """Publish a zero twist so the robot doesn't keep driving on its last command."""
        self.vel_publisher.publish(Twist())


    # TODO Part 4: Motion functions: complete the functions to generate the proper messages corresponding to the desired motions of the robot

    def make_circular_twist(self):
        """Constant v and w -> circle of radius r = v/w."""
        msg=Twist()
        msg.linear.x=self.CIRCLE_V
        msg.angular.z=self.CIRCLE_W
        self.radius_=self.CIRCLE_V/self.CIRCLE_W
        return msg

    def make_spiral_twist(self):
        """Constant w with linearly increasing v -> radius r = v/w grows with time (outward spiral)."""
        msg=Twist()
        t=self.tick_count*self.dt
        v=min(self.SPIRAL_V0 + self.SPIRAL_ACC*t, self.SPIRAL_V_MAX)
        msg.linear.x=v
        msg.angular.z=self.SPIRAL_W
        self.radius_=v/self.SPIRAL_W
        return msg

    def make_acc_line_twist(self):
        """Pure translation (w = 0) with v ramping up at constant acceleration until v_max."""
        msg=Twist()
        t=self.tick_count*self.dt
        msg.linear.x=min(self.LINE_ACC*t, self.LINE_V_MAX)
        msg.angular.z=0.0
        return msg

import argparse

if __name__=="__main__":


    argParser=argparse.ArgumentParser(description="input the motion type")


    argParser.add_argument("--motion", type=str, default="circle")



    rclpy.init()

    args = argParser.parse_args()

    if args.motion.lower() == "circle":

        ME=motion_executioner(motion_type=CIRCLE)
    elif args.motion.lower() == "line":
        ME=motion_executioner(motion_type=ACC_LINE)

    elif args.motion.lower() =="spiral":
        ME=motion_executioner(motion_type=SPIRAL)

    else:
        print(f"we don't have {args.motion.lower()} motion type")
        rclpy.shutdown()
        sys.exit(1)



    try:
        rclpy.spin(ME)
    except KeyboardInterrupt:
        print("Exiting")
        ME.stop()   # make sure the robot stops when the script is killed
