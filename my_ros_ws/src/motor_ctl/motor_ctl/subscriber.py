import rclpy
from rclpy.node import Node
import time
from std_msgs.msg import String
from dynamixel_python import DynamixelManager


USB_PORT = '/dev/ttyUSB0'
DYNAMIXEL_MODEL = 'xl430-w250'
trackID = 1
gripID = 2

def motor_init():

	motors = DynamixelManager(USB_PORT, baud_rate=57600)
	trackMotor = motors.add_dynamixel('TrackMotor', trackID, DYNAMIXEL_MODEL)
	gripMotor = motors.add_dynamixel("GripMotor", gripID, DYNAMIXEL_MODEL)
	motors.init()
	
	if not trackMotor.ping():
		raise BaseException('track motor not configured correctly')
	if not gripMotor.ping():
		raise BaseException('grip motor not configured correctly')
		
	print("no exception")
	
	trackMotor.set_operating_mode(1)   
	trackMotor.set_led(True)
	trackMotor.set_torque_enable(True)
	print(trackMotor.get_torque_enable())
	
	gripMotor.set_operating_mode(1)   
	gripMotor.set_led(True)
	gripMotor.set_torque_enable(True)
	print(gripMotor.get_torque_enable())
	return trackMotor, gripMotor
    	
def turn_off_motor(testMotor):
	testMotor.set_torque_enable(False)
	testMotor.set_led(False)

class MySubscriber(Node):
	def __init__(self):
		super().__init__("motor_ctl_subscriber")
		self.subscription = self.create_subscription(String, 'detected', self.listener_callback_detected, 1)
		self.subscription = self.create_subscription(String, 'loading', self.listener_callback_loading, 1)
		self.is_egg=False
		self.is_egg_ctr = 0
		self.in_position=False
		#self.move_motors()
		#self.grab_egg()
		#self.move_egg()
		#self.drop_egg()
		#self.ret_gripper()
		
		
	def move_motors(self):
		'''uses globals to move the motors based on recorded times. I hope this works :) 
		'''
		print("entered motor function, is_egg is", self.is_egg, "in_position is", self.in_position)
		if self.is_egg_ctr > 3 and self.in_position:
			# follow protocol
			print("moving")
			self.grab_egg()
			self.move_egg()
			self.drop_egg()
			self.ret_gripper()
		else:
			# do nothing
			print("not yet")
			
	def grab_egg(self):
		print("grapping egg")
		gripmotor.set_goal_velocity(-10)
		time.sleep(1.7)
		gripmotor.set_goal_velocity(0)
		time.sleep(2)
		
		
	def move_egg(self):
		print('moving egg')
		trackmotor.set_goal_velocity(250)
		time.sleep(21)
		trackmotor.set_goal_velocity(0)
		time.sleep(1)
	
	def drop_egg(self):
		print("dropping_egg")
		gripmotor.set_goal_velocity(10)
		time.sleep(1.7)
		gripmotor.set_goal_velocity(0)
		time.sleep(1)
		
		
	
	def ret_gripper(self):
		print("returning gripper")
		trackmotor.set_goal_velocity(-250)
		time.sleep(21)
		trackmotor.set_goal_velocity(0)
		time.sleep(3)
		self.is_egg=False
		
		
		
		
	def listener_callback_detected(self, msg):
		'''
		gets distance message
		'''
		temp= f"{msg}"
		temp=temp[28:30]
		dist= int(temp)
		self.get_logger().info(f'got distance {dist}')
		if dist < 10:
			self.is_egg = True
			self.is_egg_ctr+=1
		else:
			self.is_egg = False
			self.is_egg_ctr=0
		#print("is_egg is", is_egg)
		
	def listener_callback_loading(self, msg):
		'''
		gets loading message
		'''
		temp=f"{msg}"
		temp=temp[26]
		L = int(temp)
		if L == 0:
			self.in_position = True
		else:
			self.in_position = False
		#print("in_position is ", in_position)
		self.move_motors()
		
		
	

def main():
    try:
    	rclpy.init()
    	global trackmotor
    	global gripmotor
    	global sub
    	#global is_egg
    	#is_egg = False
    	#global in_position
    	#in_position = False
    	trackmotor, gripmotor=motor_init()
    	sub = MySubscriber()
    	rclpy.spin(sub)
    except KeyboardInterrupt:
    	turn_off_motor(trackmotor)
    	turn_off_motor(gripmotor)
    	sub.destroy_node()
    	rclpy.shutdown()


if __name__ == '__main__':
    main()
