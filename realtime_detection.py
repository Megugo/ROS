#!/usr/bin/env python3
import cv2 as cv
import os
import rospy
import numpy as np
import argparse
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

global args
global CLASSES
global COLORS
global net

class image_converter:
        def __init__(self):
            self.image_pub = rospy.Publisher("/image_processed",Image, queue_size=10)
            self.bridge = CvBridge()
            self.image_sub = rospy.Subscriber("/camera1/image_raw",Image,self.callback)
        def callback(self,data):
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            #template = cv.imread("/home/sit/catkin_ws/src/MAC-design-and-operation/scripts/Logo1.png", cv.IMREAD_GRAYSCALE)
            image = recognise_picture(cv_image)

            self.image_pub.publish(self.bridge.cv2_to_imgmsg(image, "bgr8"))

def recognise_picture(image):
    (h, w) = image.shape[:2]
    blob = cv.dnn.blobFromImage(cv.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

    net.setInput(blob)
    detections = net.forward()

    for i in np.arange(0, detections.shape[2]):
    	confidence = detections[0, 0, i, 2]

    	if confidence > args["confidence"]:
    		idx = int(detections[0, 0, i, 1])
    		box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
    		(startX, startY, endX, endY) = box.astype("int")

    		label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
    		cv.rectangle(image, (startX, startY), (endX, endY),
    			COLORS[idx], 2)
    		y = startY - 15 if startY - 15 > 15 else startY + 15
    		cv.putText(image, label, (startX, y),
    			cv.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

    # show the output image
    return image
    #cv.imshow("broadcasting", image)
    #key = cv.waitKey(1) & 0xFF
    #if key == ord("q"):
    	#rospy.signal_shutdown('c')


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
#ap.add_argument("-i", "--image", required=True,
    #help="path to input image")
ap.add_argument("-p", "--prototxt", required=True,
    help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
    help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
    help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print("[INFO] loading model...")
net = cv.dnn.readNetFromCaffe(args["prototxt"], args["model"])

rospy.init_node('command_node', anonymous=True)
image = image_converter()
os.system('rosrun image_view image_view image:=/image_processed')
rospy.spin()
