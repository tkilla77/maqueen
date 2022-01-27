from microbit import *
import utime
import machine

    
i2cAddr = 16 # Adresse des Motor-Controllers
motor_connected = False
def init_motor():
    global motor_connected, i2cAddr
    if motor_connected:
        return
    while i2cAddr not in i2c.scan():
        sleep(50)
    motor_connected = True
    print("Motor connection established")

def motor_run(motors=0, direction=0x00, speed=0):
    """Runs the maqueen wheels: direction: 0 = forward, 1 = backward
       speed range: 0...255"""
    init_motor()
    global i2cAddr
    i2cBuf = bytearray([motors, direction, speed])
    if motors == 0:  # left motor
        i2cBuf[0] = 0x00
        i2c.write(i2cAddr, i2cBuf)
    if motors == 1:  # right motor
        i2cBuf[0] = 0x02
        i2c.write(i2cAddr, i2cBuf)
    if motors == 2:  # both motors
        i2cBuf[0] = 0x00
        i2c.write(i2cAddr, i2cBuf)
        i2cBuf[0] = 0x02
        i2c.write(i2cAddr, i2cBuf)

def stop():
    motor_run(2,0,0)
    
def drive(centimeters, speed=50):
    motor_run(2,0,speed)
    # 5000 multiplier determined experimentally.
    delay = 5000 * centimeters / speed
    sleep(delay)
    stop()

def driveForever(speed=50):
    motor_run(2,0,speed)

def turn(degrees, speed=50):
    motor = 0  # default: turn right, operate left motor
    if degrees < 0:
        # Negative angle: turn left, operate right motor
        motor = 1
        degrees = -1 * degrees
    # 600 was determined experimentally....
    time = degrees * 600 / speed
    motor_run(motor, 0, speed)
    sleep(time)
    stop()
    
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

