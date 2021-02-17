#!/usr/bin/env python

import rospy
from std_msgs.msg import String
import datetime
from threading import Lock

send_queue = {}
lock = Lock()
        
def sendCommandCallback(data):
    parts = data.data.split(None,1)
    cmd = parts[0]
    if len(parts) > 1:
        args = parts[1]
    else:
        args = None
    ts = datetime.datetime.utcnow().isoformat()
    with lock:
        send_queue[cmd] = (ts,args)
    
def update(event):
    with lock:
        for cmd in send_queue:
            s = String()
            s.data = send_queue[cmd][0]+' '+cmd
            if send_queue[cmd][1] is not None:
                s.data += ' '+send_queue[cmd][1]
            #print s
            command_pub.publish(s)

def responseCallback(data):
    ts,cmd = data.data.split(None,1)
    with lock:
        if cmd in send_queue and send_queue[cmd][0] == ts:
            send_queue.pop(cmd,None)

rospy.init_node('command_bridge_sender', anonymous=False)
command_pub = rospy.Publisher('project11/command',String,queue_size=10)
rospy.Subscriber('project11/send_command',String,sendCommandCallback)
rospy.Subscriber('project11/response',String,responseCallback)
rospy.Timer(rospy.Duration.from_sec(1.0),update)
rospy.spin()
