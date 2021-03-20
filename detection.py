#!/usr/bin/env python3
import cv2 as cv
import os
import rospy
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class image_converter:
        def __init__(self):
            self.image_pub = rospy.Publisher("/image_processed",Image, queue_size=10)
            self.bridge = CvBridge()
            self.image_sub = rospy.Subscriber("/camera1/image_raw",Image,self.callback)
        def callback(self,data):
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            template = cv.imread("/home/sit/catkin_ws/src/MAC-design-and-operation/scripts/Logo1.png", cv.IMREAD_GRAYSCALE)
            image = recognise_picture(cv_image, template)

            self.image_pub.publish(self.bridge.cv2_to_imgmsg(image, "bgr8"))

def recognise_picture(img, template):

    sift = cv.SIFT_create()

    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(img, None)

    #ex_im = cv.drawKeypoints (resized_image, kp1, None)
    #ex_im_cv = cv.drawKeypoints (cv_image, kp2, None)
    #cv.imwrite('res.jpg', ex_im)
    #cv.imwrite('res_cv.jpg', ex_im_cv)

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
        cv.rectangle(img, (min_x, min_y), (max_x,max_y), 255, 2)

        return img

rospy.init_node('command_node', anonymous=True)
image = image_converter()
os.system('rosrun image_view image_view image:=/image_processed')
rospy.spin()
