#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
import sys, select, tty
from sensor_msgs.msg import LaserScan
import random
from gazebo_msgs.srv import GetModelState
from tf.transformations import euler_from_quaternion
from math import atan2

global cmd
global pub

def _get_yaw_angle(name):
	model_coordinates = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
	resp_coordinates = model_coordinates(str(name), 'link')
	orientation_list = [
	resp_coordinates.pose.orientation.x,
	resp_coordinates.pose.orientation.y,
	resp_coordinates.pose.orientation.z,
	resp_coordinates.pose.orientation.w]
	_, _, yaw = euler_from_quaternion(orientation_list)
	return yaw

def laser_callback(data):
    rate = rospy.Rate(100)
    simplefier = data.ranges
    #for range in simplefier:
    if min(simplefier) < 2:
        print("stena", min(simplefier), _get_yaw_angle('rosbots'))
        rangle = random.randrange(-3,3,1)
        while abs(rangle - _get_yaw_angle('rosbots')) > 0.25:
            cmd.angular.z = 0.5
            cmd.linear.x = 0.0
            pub.publish(cmd)
            #rate.sleep()

    else:
        print('ne stena', min(simplefier))
        cmd.linear.x = 0.5
        cmd.angular.z = 0.0
        pub.publish(cmd)

pub = rospy.Publisher('/part2_cmr/cmd_vel', Twist, queue_size=1)
rospy.init_node('command_node', anonymous=True)
cmd = Twist()
#while not rospy.is_shutdown():
rospy.Subscriber("/bot_0/laser/scan", LaserScan, laser_callback)
rospy.spin()
