#!/usr/bin/env python
import socket
import json
import rospy
from time import sleep
from std_msgs.msg import String
from dvl.msg import DVL
from dvl.msg import DVLBeam
from dvl.msg import DVLDeadReckoning
import select
#from dvl_ros import _handle,_process_messages,arguments_parser

def connect():
	global s, TCP_IP, TCP_PORT
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((TCP_IP, TCP_PORT))
		s.settimeout(2)
	except socket.error as err:
		rospy.logerr("No route to host, DVL might be booting? {}".format(err))
		sleep(1)
		connect()




def callback(data):
	#rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
	if data.data =="reset":
		rst={"command": "reset_dead_reckoning"}
		reset=json.dumps(rst)
		s.sendall(reset)
		

def publisher():
	reset_pub = rospy.Publisher('dvl/reset', String, queue_size=10)
	rate = rospy.Rate(10) # 10hz
	while not rospy.is_shutdown():
		
		#rospy.Subscriber("dvl/reset", String, callback)
		reset_pub.publish("reset")
		#sleep(10)
		rate.sleep()
		#exit()

if __name__ == '__main__':
	global s, TCP_IP, TCP_PORT
	rospy.init_node('a50_pub', anonymous=False)
	TCP_IP = rospy.get_param("~ip", "192.168.194.95")
	TCP_PORT = rospy.get_param("~port", 16171)

	connect()
	
	
	
	try:
		publisher()
		
	except rospy.ROSInterruptException:
		s.close()
