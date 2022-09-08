Dieses Repository stellt Python Code bereit, um den [Maqueen Roboter](https://www.dfrobot.com/product-1783.html) zusammen mit den [BBC:Microbit](https://microbit.org/) zu steuern.

## Einbindung
Der Code kann als Python-Quellcode eingebunden werden (`maqueen.py`). Wenn du den online Python-Editor auf https://python.microbit.org/ verwendest, kannst einfach das `maqueen.hex` des neuesten [Release](https://github.com/tkilla77/maqueen/releases) in den Editor ziehen.

## API

### Motorsteuerung

Die folgenden Funktionen steuern die Motoren des Maqueen:
```python
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
```

Du kannst den Roboter auch bis auf Weiteres in Bewegung setzen und erst auf ein bestimmtes Ereignis hin wieder stoppen. Dazu nützt du die `Chassis` Klasse und zum Beispiel den Ultraschall-Sensor:

```python
from microbit import *
from maqueen import *

robot = Maqueen()
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
```

Willst du die Räder einzeln steuern, wirds komplizierter:
```python
from microbit import *
from maqueen import *

robot = Maqueen()
chassis = robot.chassis
left_wheel = chassis.left_wheel
right_wheel = chassis.right_wheel

left_wheel.set_speed(50)
right_wheel.set_speed(-50)
sleep(1000)
chassis.stop()
```

### Front LEDs
Schalte die zwei roten LEDs auf der Vorderseite ein und aus, indem du die `frontLights` Funktion verwendest:

```python
from microbit import *
from maqueen import *

robot = Maqueen()

while True:
    if button_a.was_pressed():
        # Licht an
        robot.front_lights.set_lights(1,1)
    if button_b.was_pressed():
        # Licht aus
        robot.front_lights.set_lights(0,0)
```

### Bottom LEDS

Du kannst die Farb-LEDs auf der Unterseite des Maqueens wie folgt kontrollieren. Die LEDs können im [RGB-Farbraum](https://www.farb-tabelle.de/de/farbtabelle.htm) (rot-grün-blau) programmiert werden. Jede Farbe kann Werte von 0 (aus) bis 255 annehmen.

```python
from maqueen import *

robot = Maqueen()
leds = robot.bottom_leds

# Setze das erste LED auf rot:
leds[0] = (255,0,0)
# Setze das zweite LED auf weiss (= alle Farben auf voll):
leds[1] = (255,255,255)
# Die LEDs werden erst geändert, wenn show() aufgerufen wird:
leds.show()

# Alle 4 LEDS in magenta:
leds.fill((255,0,255))
leds.show()

# Licht aus!
leds.clear()
```

### Boden-Farbe erkennen
Die `FloorSensor` Klasse gibt die Helligkeit des Bodens wieder. Beiden Werte sind entweder 0 (= Boden ist schwarz oder kein Boden sichtbar) oder 1 (= Boden ist weiss / hell) zurück. Auf der Oberseite zeigen zwei kleine blaue LEDs den Zustand der Sensoren an. Kannst du den Roboter einer Linie folgen lassen, wenn du diesen Code einbaust? 

```python
import speech
from microbit import *
from maqueen import *

robot = Maqueen()
floor_sensor = robot.floor_sensor

left, right = floor_sensor.read()
if left == 0 and right == 0:
    speech.say("all black")
elif left == 0:
    speech.say("black on the left")
elif right == 0:
    speech.say("black on the right")
else:
    speech.say("all white")
```

### Distanzmesser
Der Ultraschallsensor gibt die ungefähre Distanz bis zum nächsten Objekt wieder. Wenn du die `distance()` Funktion einbaust, kannst du vermeiden, dass der Roboter in Gegenstände fährt...

```python
from maqueen import *
from microbit import *

robot = Maqueen()
front_sensor = robot.front_sensor

dist = 10
while True:
    newdist = int(front_sensor.distance() / 10)
    if newdist != dist:
        dist = newdist
        # Show distance in decimeters
        display.show(dist)
    sleep(100)
```
