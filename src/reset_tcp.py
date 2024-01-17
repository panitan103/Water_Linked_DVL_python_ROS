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

def connect_dvl(TCP_IP, TCP_PORT):
	
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((TCP_IP, TCP_PORT))
		s.settimeout(3)
	except socket.error as err:
		print("No route to host, DVL might be booting? {}".format(err))
		sleep(1)
		connect_dvl(TCP_IP, TCP_PORT)
	return s
def connect_ground(TCP_IP, TCP_PORT):
	
	try:
		s = socket.socket()

		s.bind((TCP_IP, TCP_PORT))
		s.listen(1)

		#s.settimeout(1)
	except socket.error as err:
		print("{}".format(err))
		sleep(1)
		connect_ground(TCP_IP, TCP_PORT)
	return s
def reset_tcp():
	s=connect_dvl("192.168.194.95",16171)	
	rst={"command": "reset_dead_reckoning"}
	reset=json.dumps(rst)
	s.sendall(reset)
	s.close()

def callback(data):
	print(data.data)
	if data.data=="reset":
		reset_tcp()

def reset():
	tcp_input=connect_ground("192.168.194.60",16172)
	rospy.Subscriber("dvl/reset", String, callback)
	rate = rospy.Rate(5)
	while not rospy.is_shutdown():

		clientSocket,clientAddress = tcp_input.accept() 

		
		data_recv = clientSocket.recv(1024) 
		print("At Server: %s"%data_recv) 
		if data_recv=="reset":
			reset_tcp()
			
	rate.sleep()
if __name__ == '__main__':
	rospy.init_node('dvl_reset', anonymous=False)
	
	try:
		
		reset()
	except rospy.ROSInterruptException:
		s.close()
