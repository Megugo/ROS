#!/usr/bin/env python3

#Скрипт мониторинга

#Использование:
#python3 <path>/normal_bot.py <ID робота>

import rospy
import sys,os
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from math import exp

global MAS_id
global cur_id
global msg
global data_c
global time

rospy.init_node(f"laser_checker_{str(sys.argv[1])}")
pub = rospy.Publisher(f"/lidar_check_{str(sys.argv[1])}", String, queue_size=10)
b_number = sys.argv[1]
MAS_id = [1,2,3]#.remove(int(b_number))
MAS_id.remove(int(b_number))
print (MAS_id)
print (MAS_id[1] == b_number)
cur_id = 0
creputation = [0.75, 0.75, 0.75]
preputation = [0.0,0.0,0.0]
truth_p = [0.0,0.0]
data_c = [3,3,3]
time = 0
def laser_callback(data):
    min_range = 30
    for _range in data.ranges[300:420]:
        if _range < min_range:
            min_range = _range

    if min_range < 5:
        msg = "1"
    else:
        msg= "0"
    pub.publish(msg)
    data_c[int(b_number)-1] = int(msg)
def callback1(data):
    data_c[MAS_id[0]-1] = int(data.data)
    #print(1)
def callback2(data):
    data_c[MAS_id[1]-1] = int(data.data)
    #print(2)
    #callback()

def callback():
    global data_c
    global cur_id
    global time



def rep_change(I0,I1):
    rt = [I0,I1]
    #for i in rt:
    if I0 >= 0.5:
        buff = 0.75 + truth_p[0]
        if buff > 1: buff = 1
        preputation[MAS_id[0]-1] = creputation[MAS_id[0]-1]
        creputation[MAS_id[0]-1] = buff
    else:
        print("I0", I0)
        buff = 0.75 + truth_p[0] - (creputation[MAS_id[0]-1] - exp(-(1-I0)*time))
        preputation[MAS_id[0]-1] = creputation[MAS_id[0]-1]
        creputation[MAS_id[0]-1] = buff
    if I1 >= 0.5:
        buff = 0.75 + truth_p[1]
        if buff > 1: buff = 1
        preputation[MAS_id[1]-1] = creputation[MAS_id[1]-1]
        creputation[MAS_id[1]-1] = buff
    else:
        print("I1", I1)
        buff = creputation[MAS_id[1]-1] + (truth_p[1]) - (creputation[MAS_id[1]-1] - exp(-(1-I1)*time))
        preputation[MAS_id[1]-1] = creputation[MAS_id[1]-1]
        creputation[MAS_id[1]-1] = buff
    k = 1
    #os.system("clear")
    for i in creputation:
        if i < 0.5:
            print ("Robot", k, "bandit -", i)
            exit(1)
        elif i == 0.75:
            print ("Robot", k, "Eto ia))", i)
        else:
            print ("Robot", k, "norm - ", i)
        k+=1

rospy.Subscriber(f"/bot_{str(int(sys.argv[1])-1)}/laser/scan", LaserScan, laser_callback)
rospy.Subscriber(f"/lidar_check_{str(MAS_id[0])}", String, callback1)
rospy.Subscriber(f"/lidar_check_{str(MAS_id[1])}", String, callback2)
rate = rospy.Rate(100)
while not rospy.is_shutdown():
    time += 1
    #print ((data_c))
    I0 = (int(data_c[1] == data_c[0]) + int(data_c[1] == data_c[1]) + int(data_c[1] == data_c[2]))/3
    I1 = (int(data_c[2] == data_c[0]) + int(data_c[2] == data_c[1]) + int(data_c[2] == data_c[2]))/3
    #rep_change(I0,I1)
    truth_p[0] += I0
    truth_p[1] += I1
    #print ("I0,I1",I0,I1)
        #data_c = []
    print ("iteration:", time)
    rt = [I0,I1]
    #for i in rt:
    if I0 >= 0.5:
        buff = 0.75 + truth_p[0]
        #if buff > 1: buff = 1
        preputation[MAS_id[0]-1] = creputation[MAS_id[0]-1]
        creputation[MAS_id[0]-1] = buff/time
    else:
        #print("I0", I0)
        buff = 0.75 + truth_p[0] - (creputation[MAS_id[0]-1] - exp(-(1-I0)*time))
        preputation[MAS_id[0]-1] = creputation[MAS_id[0]-1]
        creputation[MAS_id[0]-1] = buff/time
    if I1 >= 0.5:
        buff = 0.75 + truth_p[1]
        #if buff > 1: buff = 1
        preputation[MAS_id[1]-1] = creputation[MAS_id[1]-1]
        creputation[MAS_id[1]-1] = buff/time
    else:
        #print("I1", I1)
        #print("truth_p[1]", truth_p[1])
        #print("-", creputation[MAS_id[1]-1] - exp(-(1-I1)*time))
        buff = 0.75 + (truth_p[1]) - (preputation[MAS_id[1]-1] - exp(-(1-I1)*time))
        preputation[MAS_id[1]-1] = creputation[MAS_id[1]-1]
        creputation[MAS_id[1]-1] = buff/time
    k = 1
    #os.system("clear")
    for i in creputation:
        if i < 0.4:
            print ("Robot", k, "bandit -", i)
            exit(1)
        elif i == 0.75:
            print ("Robot", k, "Eto ia))", i)
        else:
            print ("Robot", k, "norm - ", i)
        k+=1
    rate.sleep()
    pass
