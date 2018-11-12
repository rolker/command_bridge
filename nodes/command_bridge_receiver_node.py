#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from kongsberg_em_control.srv import EMControl
from kongsberg_em_control.srv import EMControlRequest

last_messages_received = {}

emControl = None

def sendAck(cmd,ts):
    s = String()
    s.data = ts+' '+cmd
    response_pub.publish(s)

def commandCallback(data):
    #for now: timestamp, command, args
    ts,cmd,args = data.data.split(None,2)
    if not cmd in last_messages_received or last_messages_received[cmd] != ts:
        # we got a new command
        last_messages_received[cmd] = ts
        processMessage(cmd,args)
    sendAck(cmd,ts)

def processMessage(cmd, args):
    global emControl
    print 'processing',cmd,args
    if cmd == 'sonar_control':
        print 'Sonar:',args
        if emControl is None:
            emControl = rospy.ServiceProxy('/sonar/control', EMControl)
        mode,linenum = args.split()
        em_req = EMControlRequest()
        em_req.requested_mode = int(mode)
        em_req.line_number = int(linenum)
        try:
            response = emControl(em_req)
        except rospy.ServiceException as exc:
            print 'error:',str(exc)


rospy.init_node('command_bridge_receiver', anonymous=False)

response_pub =  rospy.Publisher('/project11/response',String,queue_size=10)               
rospy.Subscriber('/project11/command', String, commandCallback)
rospy.spin()
