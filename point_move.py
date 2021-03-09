#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist, Point
#from std_msgs.msg import String
#import std_msgs.msg
from gazebo_msgs.srv import GetModelState
from tf.transformations import euler_from_quaternion
from math import atan2

global target
target = Point()

def callback(data):
	target.x,target.y = data.x, data.y

	print(data)

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

def _get_coords(name):
	model_coordinates = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
	resp_coordinates = model_coordinates(str(name), 'link')
	#print(resp_coordinates)
	return (resp_coordinates.pose.position.x, resp_coordinates.pose.position.y)

pub = rospy.Publisher("/part2_cmr/cmd_vel", Twist, queue_size = 1)

rospy.init_node('lab2_master_node')
speed = Twist()
rate = rospy.Rate(10)# 10hz

while not rospy.is_shutdown():
	pos_x, pos_y = _get_coords('rosbots')
	cangle = _get_yaw_angle('rosbots')
	sub = rospy.Subscriber("/lab2_master", Point, callback)
	inc_x = target.x - pos_x
	inc_y = target.y - pos_y
	goal = atan2(inc_y, inc_x)

	if abs(goal - cangle) > 0.1 :
		speed.linear.x = 0.0
		speed.angular.z = 0.3
	elif 	abs(inc_x) < 0.15 and abs(inc_y) < 0.15:
		speed.linear.x = 0.0
		speed.angular.z = 0.0
	else:
		speed.linear.x = 0.5
		speed.angular.z = 0.0
	#print(inc_x, inc_y)
	pub.publish(speed)
	rate.sleep()
speed.linear.x = 0.0
speed.angular.z = 0.0
pub.publish(speed)
rate.sleep()
