#!/usr/bin/env python

import rospy
from std_msgs.msg import String
import datetime
send_queue = {}

        
def sendCommandCallback(data):
    cmd,args = data.data.split(None,1)
    ts = datetime.datetime.utcnow().isoformat()
    send_queue[cmd] = (ts,args)
    
def update(event):
    for cmd in send_queue:
        s = String()
        s.data = send_queue[cmd][0]+' '+cmd+' '+send_queue[cmd][1]
        print s
        command_pub.publish(s)

def responseCallback(data):
    ts,cmd = data.data.split(None,1)
    if cmd in send_queue and send_queue[cmd][0] == ts:
        send_queue.pop(cmd,None)

rospy.init_node('command_bridge_sender', anonymous=False)
command_pub = rospy.Publisher('/udp/command',String,queue_size=10)
rospy.Subscriber('/send_command',String,sendCommandCallback)
rospy.Subscriber('/udp/response',String,responseCallback)
rospy.Timer(rospy.Duration.from_sec(1.0),update)
rospy.spin()
