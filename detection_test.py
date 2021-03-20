#!/usr/bin/env python3

import os
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
import sys, select, termios, tty # For user input
import cv2 as cv
import numpy as np
from cv_bridge import CvBridge

# Данная часть полностью такая же как и в предыдущих ЛР
rospy.init_node('command_node')
pub = rospy.Publisher('/part2_cmr/cmd_vel', Twist, queue_size=10)
image_pub = rospy.Publisher("/image_processed",Image, queue_size=10)
rate = rospy.Rate(100)
msg = Twist()
# Добавляем CvBridge
bridge = CvBridge()

# Задаем целевое изображение (собственно то, которое должна найти машинка)
global goal_image
goal_image = cv.imread('/home/sit/catkin_ws/src/MAC-design-and-operation/scripts/Logo1.png', cv.IMREAD_GRAYSCALE)
resized_image = goal_image
#resized_image = cv.resize(goal_image, (640, 480))

def callback(data):
    global resized_image
    global msg
    global pub
    global rate
    global bridge

	#IMAGE
    sift = cv.SIFT_create()

    cv_image = bridge.imgmsg_to_cv2(data, "bgr8")
    gray= cv.cvtColor(cv_image, cv.COLOR_BGR2GRAY)

    kp1, des1 = sift.detectAndCompute(resized_image, None)
    kp2, des2 = sift.detectAndCompute(cv_image, None)

    ex_im = cv.drawKeypoints (resized_image, kp1, None)
    ex_im_cv = cv.drawKeypoints (cv_image, kp2, None)

    cv.imwrite('res.jpg', ex_im)
    cv.imwrite('res_cv.jpg', ex_im_cv)

    bf = cv.BFMatcher()
    matches = bf.knnMatch(des2, des1, k=2)

    good = []
    for m,n in matches:
        if m.distance < 0.75*n.distance:
            good.append([m])

    print(str(len(good)) + "/10")
    if len(good) >= 5:

        src_pts = np.float32([ kp2[m[0].queryIdx].pt for m in good ]).reshape(-1,1,2)

        src_pts = src_pts.reshape((len(src_pts), -1))

        pts = src_pts
        min_x, min_y = np.int32(pts.min(axis=0))
        max_x, max_y = np.int32(pts.max(axis=0))

        cv.rectangle(cv_image, (min_x, min_y), (max_x,max_y), 255, 2)
    #for g in good:
        #center = tuple([int(x) for x in kp1[g.imgIdx].pt])
        #img = cv.circle(img, center, 10, 255, 2)

    image_pub.publish(bridge.cv2_to_imgmsg(cv_image, "bgr8"))
    #cv.imshow('image', cv_image)


subImage = rospy.Subscriber("/camera1/image_raw", Image, callback)
os.system('clear')
if not rospy.is_shutdown():
    rospy.spin()
