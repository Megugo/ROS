#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
import sys, select, tty
from sensor_msgs.msg import LaserScan

global cmd
global pub

def laser_callback(data):
    rate = rospy.Rate(100)
    simplefier = data.ranges[180:540]
    for range in simplefier:
        if range < 3:
            print("stena")
            cmd.angular.z = 0.2
            cmd.linear.x = 0.0

        else:
            cmd.linear.x = 0.5
            cmd.angular.z = 0.0
        pub.publish(cmd)


pub = rospy.Publisher('/part2_cmr/cmd_vel', Twist, queue_size=1)
rospy.init_node('command_node', anonymous=True)
rate = rospy.Rate(10)  # 10hz
cmd = Twist()
rospy.Subscriber("/bot_0/laser/scan", LaserScan, laser_callback)

rospy.spin()
