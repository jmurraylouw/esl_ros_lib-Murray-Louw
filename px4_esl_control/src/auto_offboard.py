#!/usr/bin/env python2

# Switch to Offboard mode automatically

# ROS python API
import rospy

# import needed geometry messages
from geometry_msgs.msg import Point, Vector3, PoseStamped, TwistStamped
from std_msgs.msg import Bool
# import all mavros messages and services
from mavros_msgs.msg import *
from mavros_msgs.srv import *

# import quat and eul transformation
from tf.transformations import euler_from_quaternion

# import other system/utils
import time, sys, math
import numpy

# Global variables

# Flight modes class
# Flight modes are activated using ROS services
class FlightModes:
    def __init__(self):
        pass

    # Switch to OFFBOARD mode
    def setOffboardMode(self):
        rospy.wait_for_service('mavros/set_mode')
        try:
            flightModeService = rospy.ServiceProxy('mavros/set_mode', mavros_msgs.srv.SetMode)
            flightModeService(custom_mode='OFFBOARD')
        except rospy.ServiceException as e:
            print("setOffboardMode - service set_mode call failed: %s. Offboard Mode could not be set."%e)

# Offboard controller for state subscriber
class Controller:
    def __init__(self):
        # Drone state
        self.state = State()

    # Drone State callback
    def stateCb(self, msg):
        self.state = msg

def run(argv):
    # initiate node
    rospy.init_node('waypoint_scheduler_node')

    modes = FlightModes()
    cnt = Controller()
    rate = rospy.Rate(20.0) # ROS loop rate

    # Subscribers
    rospy.Subscriber('mavros/state', State, cnt.stateCb)
    
    # Activate OFFBOARD mode
    print("Activating OFFBOARD mode...")
    print("Other node needs to send mavros setpoints for OFFBOARD mode to be accepted...")
    while not (cnt.state.mode == "OFFBOARD" or rospy.is_shutdown()):
        # PX4 will not activate OFFBOARD until setpoints are received from MAVROS
        # Other node will send setpoints, this node only activates offboard
        modes.setOffboardMode()
        rate.sleep()
    print("OFFBOARD mode activated.")

def main(argv):
    try:
        run(argv)
    except rospy.ROSInterruptException:
        pass
    print("Terminated\n")

if __name__ == "__main__":
    main(sys.argv[1:])