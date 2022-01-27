from microbit import *
import utime
import machine

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

    def __init__(self):
        self.left = Wheel(0x00)
        self.right = Wheel(0x02)
    
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
    def __init__(self):
        self.chassis = Chassis()
        
    def stop(self):
        self.chassis.stop()
        
    def drive(self, centimeters, speed=50):
        self.chassis.forward(speed)
        delay = 5000 * centimeters / speed
        sleep(delay)
        self.stop()

    def turn(self, degrees, radius_cm=0, speed=50):
        self.chassis.right(speed, radius_cm)
        # 500 was determined experimentally....
        time = (1 + radius_cm / Chassis._wheelbase) * degrees * 500 / speed
        sleep(time)
        self.stop()
    
def floorDistance():
    """Returns the status of the left and right floor sensors."""
    return (pin13.read_digital(), pin14.read_digital())
    
def frontDistance(attempts = 1):
    """Returns the ultrasonic distance in front of the maqueen in cm."""
    distance = 1000
    # Avoid returning bogus distance - should be less than 8m.
    while distance > 800 and attempts > 0:
        attempts -= 1
        pin1.write_digital(1)   # Pin 1 (Trigger) HIGH für...
        utime.sleep_us(10)      # ...10 µs...
        pin1.write_digital(0)   # ...und wieder LOW.
        echoPulse = machine.time_pulse_us(pin2, 1) # Messe, wie lange der Echo-Impuls an Pin 2 dauert.
        distance = echoPulse * 0.017 # Rechne Zeit in Distanz um.
        sleep(5)   # warte (verhindern, dass ein zu häufiges Aufrufen
                   # in kurzer Zeit zu Fehlern führt)
    return distance

def frontLights(left=0,right=0):
    """Control left and right LEDs of maqueen. 0=off, 1=on."""
    pin8.write_digital(left)
    pin12.write_digital(right)

