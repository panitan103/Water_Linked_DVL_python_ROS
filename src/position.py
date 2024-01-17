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
		s.settimeout(1)
	except socket.error as err:
		rospy.logerr("No route to host, DVL might be booting? {}".format(err))
		sleep(1)
		connect()

oldJson = ""

theDVL = DVL()
theDVL_dead_reckoging=DVLDeadReckoning()
beam0 = DVLBeam()
beam1 = DVLBeam()
beam2 = DVLBeam()
beam3 = DVLBeam()

def getData():
	global oldJson,s
	raw_data = ""

	while not '\n' in raw_data:
		try:
			rec = s.recv(1) # Add timeout for that
			if len(rec) == 0:
				rospy.logerr("Socket closed by the DVL, reopening")
				connect()
				continue
		except socket.timeout as err:
			rospy.logerr("Lost connection with the DVL, reinitiating the connection: {}".format(err))
			connect()
			continue
		raw_data = raw_data + rec
	raw_data = oldJson + raw_data
	oldJson = ""
	raw_data = raw_data.split('\n')
	oldJson = raw_data[1]
	raw_data = raw_data[0]
	return raw_data

def callback(data):
	#rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
	if data.data =="reset":
		rst={"command": "reset_dead_reckoning"}
		reset=json.dumps(rst)
		s.sendall(reset)

def publisher():
	pub_raw = rospy.Publisher('dvl/json_data', String, queue_size=10)
	pub = rospy.Publisher('dvl/data', DVL, queue_size=10)
	pub_dead_reckoning=rospy.Publisher('dvl/dead_reckoging', DVLDeadReckoning, queue_size=10)
	rate = rospy.Rate(10) # 10hz
	while not rospy.is_shutdown():
		raw_data = getData()
		data = json.loads(raw_data)
		
		
		# edit: the logic in the original version can't actually publish the raw data
		# we slightly change the if else statement so now
		# do_log_raw_data is true: publish the raw data to /dvl/json_data topic, fill in theDVL using velocity data and publish to dvl/data topic
		# do_log_raw_data is true: only fill in theDVL using velocity data and publish to dvl/data topic
		
		
		if data["type"] == "position_local":
			theDVL_dead_reckoging.position.x=data["x"]
			theDVL_dead_reckoging.position.y=data["y"]
			theDVL_dead_reckoging.position.z=data["z"]

			theDVL_dead_reckoging.orientation.x=data["roll"]
			theDVL_dead_reckoging.orientation.y=data["pitch"]
			theDVL_dead_reckoging.orientation.z=data["yaw"]
		
			pub_dead_reckoning.publish(theDVL_dead_reckoging)
		rospy.Subscriber("dvl/reset", String, callback)
		rate.sleep()
		

if __name__ == '__main__':
	global s, TCP_IP, TCP_PORT, do_log_raw_data
	rospy.init_node('a50_pub', anonymous=False)
	TCP_IP = rospy.get_param("~ip", "192.168.194.95")
	TCP_PORT = rospy.get_param("~port", 16171)
	do_log_raw_data = rospy.get_param("~do_log_raw_data", False)
	connect()
	
	
	
	try:
		publisher()
		
	except rospy.ROSInterruptException:
		s.close()
