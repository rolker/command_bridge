#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool
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
    parts = data.data.split(None,2)
    ts,cmd = parts[:2]
    if len(parts) > 2:
        args = parts[2]
    else:
        args = None
    if not cmd in last_messages_received or last_messages_received[cmd] != ts:
        # we got a new command
        last_messages_received[cmd] = ts
        processMessage(cmd,args)
    sendAck(cmd,ts)

def processMessage(cmd, args):
    #following should be seperated out into different node
    global emControl
    #print 'processing',cmd,args
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
    if cmd == 'mission_plan':
        s = String(args)
        mission_plan_pub.publish(s)
    if cmd == 'piloting_mode':
        s = String(args)
        piloting_mode_pub.publish(s)
    if cmd in ('goto_line','start_line','goto','hover','clear_mission'):
        if args is None:
            s = String(cmd)
        else:
            s = String(cmd+' '+args)
        mm_comand_pub.publish(s)
    if cmd == 'mission_manager':
        s = String(args)
        mm_comand_pub.publish(s)

rospy.init_node('command_bridge_receiver', anonymous=False)

mission_plan_pub = rospy.Publisher('/mission_plan',String,queue_size=10)
piloting_mode_pub = rospy.Publisher('/project11/piloting_mode',String,queue_size=10)
mm_comand_pub = rospy.Publisher('/project11/mission_manager/command',String,queue_size=10)

response_pub =  rospy.Publisher('/project11/response',String,queue_size=10)               
rospy.Subscriber('/project11/command', String, commandCallback)
rospy.spin()
