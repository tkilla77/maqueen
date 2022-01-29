from microbit import *
import utime
import machine
import neopixel

class Wheel:
    """A single wheel on the maqueen chassis."""
    _i2cAddress = 0x10
    _connected = False

    def _connect():
        if Wheel._connected:
            return
        while _i2cAddress not in i2c.scan():
            sleep(50)
        Wheel._connected = True
        print("Motor connection established")

    def __init__(self, address):
        self.buf = bytearray([address,0,0])

    def set_speed(self, speed):
        """Sets the speed of the wheel in the range [-255,255]."""
        Wheel._connect()
        direction = 0
        if (speed < 0):
            direction = 1
            speed *= -1
        self.buf[1] = direction
        self.buf[2] = speed
        i2c.write(Wheel._i2cAddress, self.buf)
    
    def stop(self):
        self.set_speed(0)

class Chassis:
    """The maqueen chassis consisting of two wheels."""
    _wheelbase = 8  # Radstand: 8cm

    def __init__(self, left_wheel=Wheel(0x00), right_wheel=Wheel(0x02)):
        self.left = left_wheel
        self.right = right_wheel
    
    def forward(self, speed=50):
        """Sets both wheels in forward motion (backwards if speed is negative)."""
        self.left.set_speed(speed)
        self.right.set_speed(speed)

    def backward(self, speed=50):
        """Sets both wheels in backward motion (forward if speed is negative)."""
        self.forward(-1*speed)
    
    def left(self, speed=50, radius_cm=0):
        """Sets both wheels in motion. The speed is the speed of the outer 
           (right) wheel, the radius describes the inner circle of the left
           wheel. A radius of zero means the left wheel will stop."""
        self.left.set_speed(radius_cm*speed/(radius_cm + Chassis._wheelbase))
        self.right.set_speed(speed)

    def right(self, speed=50, radius_cm=0):
        """Sets both wheels in motion. The speed is the speed of the outer 
           (left) wheel, the radius describes the inner circle of the right
           wheel. A radius of zero means the right wheel will stop."""
        self.right.set_speed(radius_cm*speed/(radius_cm + Chassis._wheelbase))
        self.left.set_speed(speed)
    
    def rotate(self, speed):
        """Lets the chassis rotate clockwise on place with given speed, counter
           clockwise if speed is negative."""
        self.left.set_speed(speed)
        self.right.set_speed(-1*speed)

    def stop(self):
        """Stops both wheels."""
        self.left.stop()
        self.right.stop()

class Driver:
    """High-level driving interface for the maqueen chassis. The 
       methods are blocking, i.e. the control flow only returns once
       the given distance / curve are completed."""
    def __init__(self, chassis=Chassis()):
        self.chassis = chassis
        
    def stop(self):
        """Stops the robot."""
        self.chassis.stop()
        
    def drive(self, centimeters, speed=50):
        """Drives forward for approximately the given distance in centimeters.
           Negative distance results in backward driving."""
        self.chassis.forward(speed)
        delay = 5000 * centimeters / speed
        sleep(delay)
        self.stop()

    def left(self, degrees, radius_cm=0, speed=50):
        """Makes a left turn with the given radius (measured from the inner wheel)
           and angle. Negative angle results in a right turn."""
        self.right(-1*degrees, radius_cm, speed)

    def right(self, degrees, radius_cm=0, speed=50):
        """Makes a right turn with the given radius (measured from the inner wheel)
           and angle. Negative angle results in a left turn."""
        self.chassis.right(speed, radius_cm)
        # 500 was determined experimentally....
        time = (1 + radius_cm / Chassis._wheelbase) * degrees * 500 / speed
        sleep(time)
        self.stop()
    
class FloorSensor:
    """Combines two bottom-mounted brightness sensors that can detect a bright
       vs. dark (or missing) floor."""
    def __init__(self, left_pin=pin13, right_pin=pin14):
        self.left_pin = left_pin
        self.right_pin = right_pin

    def left(self):
        """Returns the status of the left sensor. 0 for dark / no floor, 1 for
           bright floor detected."""
        return self.left_pin.read_digital()

    def right(self):
        """Returns the status of the right sensor. 0 for dark / no floor, 1 for
           bright floor detected."""
        return self.right_pin.read_digital()

    def read(self):
        """Returns the status of the left and right floor sensors."""
        return (self.left(), self.right())

class UltrasonicSensor:
    def __init__(self, send_pin=pin1, echo_pin=pin2):
        self.send_pin = send_pin
        self.echo_pin = echo_pin

    def distance(attempts = 1):
        """Returns the ultrasonic distance in front of the maqueen in cm.
           Returns -1 if the distance cannot be reliably measured."""
        distance = 1000
        # Avoid returning bogus distance - should be less than 8m.
        while distance > 800 and attempts > 0:
            attempts -= 1
            self.send_pin.write_digital(1)   # Pin 1 (Trigger) HIGH für...
            utime.sleep_us(10)      # ...10 µs...
            self.send_pin.write_digital(0)   # ...und wieder LOW.
            echoPulse = machine.time_pulse_us(self.echo_pin, 1) # Messe, wie lange der Echo-Impuls an Pin 2 dauert.
            distance = echoPulse * 0.017 # Rechne Zeit in Distanz um.
            sleep(5)   # warte (verhindern, dass ein zu häufiges Aufrufen
                    # in kurzer Zeit zu Fehlern führt)
        return distance if distance > 800 else -1

class Frontlights:
    def set_lights(left=0,right=0):
        """Control left and right LEDs of maqueen. 0=off, 1=on."""
        pin8.write_digital(left)
        pin12.write_digital(right)

class Maqueen:
    def __init__(self):
        self.chassis = Chassis()
        self.driver = Driver(self.chassis)
        self.floor_sensor = FloorSensor()
        self.front_sensor = UltrasonicSensor()
        self.front_lights = Frontlights()
        self.bottom_leds = neopixel.NeoPixel(pin15,4)
