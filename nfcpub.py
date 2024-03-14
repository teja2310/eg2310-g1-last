import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool
from std_msgs.msg import Int32
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.spi import PN532_SPI

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = DigitalInOut(board.D5)
pn532 = PN532_SPI(spi, cs_pin, debug=False)

pn532.SAM_configuration()

class Nfc(Node):

    def __init__(self):
        super().__init__('nfc')
        self.publisher_ = self.create_publisher(Bool, 'nfc', 10)
	self.httppub = self.create_publisher(Int32, 'nfc', 10)
        timer_period = 0.5  # seconds
        #self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = Bool()
	hmsg = Bool()
        uid = pn532.read_passive_target(timeout=0.5)
        if uid is None:
            msg.data = False
        elif uid[0] == 4 and uid[1] == 229:
            msg.data = True
        else:
            msg.data = False

'''        if uid is None:
            hmsg.data = 0
        elif uid[0] == and uid[1] == :
            hmsg.data = 1
        else:
            hmsg.data = 0
'''
        self.publisher_.publish(msg)
	#self.httppub.publish(hmsg)


def main(args=None):
    rclpy.init(args=args)

    nfc = Nfc()

    rclpy.spin(nfc)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    nfc.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
