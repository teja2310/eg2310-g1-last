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

url_post = "http://192.168.6.87/openDoor"

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16,GPIO.IN) #front left 16
GPIO.setup(18,GPIO.IN) #front right 18
GPIO.setup(22,GPIO.IN) #right 22
GPIO.setup(15,GPIO.IN) #left 15

class LineMove(Node):

	triggered = False
	shootval = Bool()
	nfcval = Bool()
	left = GPIO.input(16)
	right = GPIO.input(18)
	sideL = GPIO.input(15)
	sideR = GPIO.input(22)

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
		self.left = GPIO.input(16)
		self.right = GPIO.input(18)
		self.sideL = GPIO.input(15)
		self.sideR = GPIO.input(22)

	def move(self):
		while True:
			print(self.sideL,self.left, self.right,self.sideR)
			
			twist = Twist()
			if self.left ==  True and self.right == True:
				twist.linear.x = -0.3
				twist.angular.z = 0.0

			elif self.left == True and self.right == False:
				twist.linear.x = -0.15
				twist.angular.z = 0.17
			elif self.left == False and self.right == True:
				twist.linear.x = -0.15
				twist.angular.z = -0.17
			elif self.left == False and self.right == False:
				#twist.linear.x = -1.0
				#twist.angular.z = 0.0
				#time.sleep(1)
				#self.publisher_.publish(twist)
				#twist.linear.x = 0.0
				#time.sleep(0.1)
				#self.publisher_.publish(twist)
				if self.sideL == True:
					self.get_logger().info("left")
					twist.linear.x = -0.3
					twist.angular.z = 0.0
					time.sleep(0.1)
					self.publisher_.publish(twist)
					time.sleep(0.1)
					twist.linear.x = 0.0
					twist.angular.z = 0.3
					time.sleep(0.1)
					self.publisher_.publish(twist)
					while self.right == False:
						print(self.sideL, self.left, self.right, self.sideR)
						rclpy.spin_once(self)
						time.sleep(0.1)
					twist.linear.x = 0.0
					twist.angular.z = 0.0
				elif self.sideR == True:
					twist.linear.x = -0.3
					twist.angular.z = 0.0
					time.sleep(0.1)
					self.publisher_.publish(twist)
					time.sleep(0.1)
					twist.linear.x = 0.0
					twist.angular.z = -0.3
					time.sleep(0.1)
					self.publisher_.publish(twist)
					while self.left == False:
						rclpy.spin_once(self)
						time.sleep(0.1)
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
				time.sleep(1)
				post_response_json = post_response.json()
				time.sleep(0.5)
				check = str(post_response_json)
				if "1" in check:
					self.get_logger().info('left door')
					twist.angular.z = 0.2
					time.sleep(0.1)
					self.publisher_.publish(twist)
					while self.left == False or self.right == False:
						rclpy.spin_once(self)
						time.sleep(0.1)
					twist.linear.x = 0.0
					twist.angular.z = 0.0
					#go left door
				else:
					self.get_logger().info('right door')
					time.sleep(0.1)
					twist.angular.z = -0.2
					time.sleep(0.1)
					self.publisher_.publish(twist)
					while self.left == False or self.right == False:
						rclpy.spin_once(self)
						time.sleep(0.1)
					twist.linear.x = 0.0
					twist.angular.z = 0.0
					#go right door
				'''else:
                                twist.linear.x = -1.0
                                twist.angular.z = 0.0
                                time.sleep(0.5)
                                self.publisher_.publish(twist)
                                twist.linear.x = 0.0
                                time.sleep(0.1)
                                self.publisher_.publish(twist)
                                if self.sideL == True:
                                        twist.angular.z = 0.2
                                        time.sleep(0.1)
                                        self.publisher_.publish(twist)
                                        while self.left == False or self.right >
                                                rclpy.spin_once(self)
                                                time.sleep(0.1)
                                        twist.linear.x = 0.0
                                        twist.angular.z = 0.0
                                elif self.sideR == True:
                                        twist.angular.z = -0.2
					time.sleep(0.1)
                                        self.publisher_.publish(twist)
                                        while self.left == False or self.right >
						rclpy.spin_once(self)
					time.sleep(0.1)
					twist.linear.x = 0.0
					twist.angular.z = 0.0'''
			time.sleep(0.1)
			self.publisher_.publish(twist)
			rclpy.spin_once(self)

def main(args=None):
	rclpy.init(args=args)

	linemove = LineMove()
	linemove.move()

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
	linemove.destroy_node()
	rclpy.shutdown()


if __name__ == '__main__':
	main()
