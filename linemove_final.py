import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from std_msgs.msg import Int32
import RPi.GPIO as GPIO
import time
import requests
from geometry_msgs.msg import Twist

new_data = {
    "action": "openDoor",
    "parameters": {"robotId": "30"}
}

url_post = "http://192.168.144.87/openDoor"

GPIO.setmode(GPIO.BCM)
GPIO.setup(23,GPIO.IN) #front left 16
GPIO.setup(24,GPIO.IN) #front right 18
GPIO.setup(25,GPIO.IN) #right 22
GPIO.setup(22,GPIO.IN) #left 15
GPIO.setup(13, GPIO.OUT)
pwm = GPIO.PWM(13, 50)
pwm.start(2.5)

class LineMove(Node):

	triggered = False
	shootval = Bool()
	nfcval = Bool()
	lrState = 0; #1 is left 2 is right
	left = GPIO.input(23)
	right = GPIO.input(24)
	sideL = GPIO.input(22)
	sideR = GPIO.input(25)

	def __init__(self):
		super().__init__('lineMove')
		self.subscription_ = self.create_subscription(Bool, 'nfc', 
self.listener_callback, 10)
		self.shootsub = self.create_subscription(Int32, 'nfc', 
self.shoot_callback, 10)
		self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
		self.timer = self.create_timer(0.1, self.timer_callback)
		self.get_logger().info('starting')

	def shoot_callback(self, msg):
		if msg.data == 1:
			self.shootval = True
		else:
			self.shootval = False

	def listener_callback(self, msg):
		if msg.data == True:
			self.nfcval = True
		else:
			self.nfcval = False

	def timer_callback(self):
		time.sleep(0.1)
		self.left = GPIO.input(23)
		self.right = GPIO.input(24)
		self.sideL = GPIO.input(22)
		self.sideR = GPIO.input(25)
		if self.sideL == True and self.sideR == False:
			self.lrState = 1
		elif self.sideL == False and self.sideR == True:
			self.lrState = 2

	def move(self):
		while True:
			print(self.sideL,self.left, self.right,self.sideR,self.lrState)
			
			twist = Twist()
			if self.left ==  True and self.right == True:
				twist.linear.x = 0.16
				twist.angular.z = 0.0
			elif self.left == True and self.right == False:
				twist.linear.x = 0.16
				twist.angular.z = 0.5
			elif self.left == False and self.right == True:
				twist.linear.x = 0.16
				twist.angular.z = -0.5
			elif self.left == False and self.right == False and self.lrState == 1:
					self.get_logger().info("left")
					twist.linear.x = -0.1
					twist.angular.z = 0.0
					time.sleep(0.1)
					self.publisher_.publish(twist)
					twist.linear.x = 0.0
					twist.angular.z = 1.0
					time.sleep(0.1)
					self.publisher_.publish(twist)
					while self.right == False:
						print(self.sideL, self.left, self.right, self.sideR)
						rclpy.spin_once(self)
					twist.linear.x = 0.0
					twist.angular.z = 0.0
			elif self.left == False and self.right == False and self.lrState == 2:
					self.get_logger().info("right")
					#twist.linear.x = 0.1
					#twist.angular.z = 0.0
					#time.sleep(0.1)
					#self.publisher_.publish(twist)
					twist.linear.x = 0.0
					twist.angular.z = -1.0
					time.sleep(0.1)
					self.publisher_.publish(twist)
					while self.left == False:
						rclpy.spin_once(self)
					twist.linear.x = 0.0
					twist.angular.z = 0.0
			if self.nfcval == True and self.triggered == False:
				print("nfc")
				self.triggered = True
				twist.linear.x = 0.0
				twist.angular.z = 0.0
				time.sleep(0.1)
				self.publisher_.publish(twist)
				post_response = requests.post(url_post, json=new_data)
				time.sleep(0.1)
				post_response_json = post_response.json()
				check = str(post_response_json)
				#twist.linear.x = 0.12
				#time.sleep(0.1)
				#self.publisher_.publish(twist)
				#time.sleep(0.05)
				if "1" in check:
					#twist.linear.x = 0.1
					#time.sleep(0.1)
					#self.publisher_.publish(twist);
					#time.sleep(0.05)
					self.get_logger().info('left door')
					#self.left == False
					time.sleep(0.1)
					twist.angular.z = 0.4
					twist.linear.x = 0.0
					time.sleep(0.1)
					self.publisher_.publish(twist)
					time.sleep(0.1)
					#self.left == False
					self.right = GPIO.input(24)
					while self.right == False:
						time.sleep(0.1)
						rclpy.spin_once(self)
						#time.sleep(0.1)
					twist.linear.x = 0.0
					twist.angular.z = 0.0
				else:
					#twist.linear.x = 0.1
					#time.sleep(0.1)
					#self.publisher_.publish(twist)
					#time.sleep(0.05)
					self.get_logger().info('right door')
					time.sleep(0.1)
					#self.right == False
					twist.angular.z = -0.4
					twist.linear.x = 0.0
					time.sleep(0.1)
					self.publisher_.publish(twist)
					time.sleep(0.1)
					#self.right == False
					self.left = GPIO.input(23)
					while self.left == False:
						time.sleep(0.1)
						rclpy.spin_once(self)
						#time.sleep(0.1)
					twist.linear.x = 0.0
					twist.angular.z = 0.0
			if self.shootval == True:
				twist.linear.x = 0.0
				twist.angular.z = 0.0
				time.sleep(0.1)
				self.publisher_.publish(twist)
				time.sleep(2)
				pwm.ChangeDutyCycle(12.5)
				time.sleep(1)
			#time.sleep(0.1)
			self.publisher_.publish(twist)
			rclpy.spin_once(self)

def main(args=None):
	rclpy.init(args=args)

	linemove = LineMove()
	linemove.move()

	linemove.destroy_node()
	rclpy.shutdown()


if __name__ == '__main__':
	main()
