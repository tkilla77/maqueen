from microbit import *
from maqueen import *

robot = Maqueen()

# Use the high-level Driver interface.
# Drive 20cm straight, then make a few turns.
# The robot will stop after each driving command.
driver = robot.driver
driver.drive(20)
driver.left(90, 10)
driver.right(180, 10)
driver.left(90, 10)

# Use the Chassis interface to set wheel speed
# and return control flow immediately. Don't forget
# to call chassis.stop() eventually!
# Also use the ultrasonic sensor.
chassis = robot.chassis
ultrasonic_sensor = robot.front_sensor

# Forward until we reach an obstacle.
chassis.forward(speed=100)
while ultrasonic_sensor.distance() > 10:
    sleep(50)
chassis.stop()
# Turn left until path is clear.
chassis.left(180)
while ultrasonic_sensor.distance() < 20:
    sleep(50)
chassis.stop()

# Use the floor sensors to follow a line.
while True:
    left,right = robot.floor_sensor.read()
    if left == 0 and right == 0:
        # both sensors are dark - go straight
        chassis.forward()
    elif left == 0 and right == 1:
        # left dark, right bright - turn left
        chassis.left(radius_cm=5)
    elif left == 1 and right == 0:
        # left bright, right dark - turn right
        chassis.right(radius_cm=5)
    else:
        # both are bright - stop
        chassis.stop()
        break
    # sleep a little until the next sensor reading.
    sleep(50)

# Turn on the front lights (0: off, 1: on):
robot.front_lights.set_lights(left=1, right=1)

# Use the bottom color LEDs.
# Read the docs at https://microbit-micropython.readthedocs.io/en/v1.0.1/neopixel.html
# - need to call show() to switch on the configured colors
# - Colors use RGB (red-green-blue) color space. 
leds = robot.bottom_leds
# All red
leds.fill((255,0,0))
leds.show()
# All off
leds.clear()

# Set the 4 leds to red, green, blue, magenta:
leds[0] = (255,0,0)
leds[1] = (0,255,0)
leds[2] = (0,0,255)
leds[3] = (255,0,255)
leds.show()
