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
    ts,cmd,args = data.data.split(None,2)
    if not cmd in last_messages_received or last_messages_received[cmd] != ts:
        # we got a new command
        last_messages_received[cmd] = ts
        processMessage(cmd,args)
    sendAck(cmd,ts)

def processMessage(cmd, args):
    #following should be seperated out into different node
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
    if cmd == 'moos_wpt_updates':
        s = String(args)
        moos_wpt_update_pub.publish(s)
    if cmd == 'moos_loiter_updates':
        s = String(args)
        moos_loiter_update_pub.publish(s)
    if cmd == 'active':
        if args == 'True':
            active = Bool(True)
        else:
            active = Bool(False) 
        active_pub.publish(active)
    if cmd == 'mission_plan':
        s = String(args)
        mission_plan_pub.publish(s)
    if cmd == 'helm_mode':
        s = String(args)
        helm_mode_pub.publish(s)

rospy.init_node('command_bridge_receiver', anonymous=False)

moos_wpt_update_pub = rospy.Publisher('/moos/wpt_updates',String,queue_size=10)
moos_loiter_update_pub = rospy.Publisher('/moos/loiter_updates',String,queue_size=10)
active_pub = rospy.Publisher('/active',Bool,queue_size=10)
mission_plan_pub = rospy.Publisher('/mission_plan',String,queue_size=10)
helm_mode_pub = rospy.Publisher('/helm_mode',String,queue_size=10)

response_pub =  rospy.Publisher('/project11/response',String,queue_size=10)               
rospy.Subscriber('/project11/command', String, commandCallback)
rospy.spin()
