# Copyright (c) 2012 Richard Klancer <rpk@pobox.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# The contents of this file were copied into server.py on a demo Rascal board, with the lines
# preceded by the comment "# UNCOMMENT on a working Rascal" uncommented. (These lines were commented
# for convenient development on a desktop machine not running the Rascal environment -- this is
# demo code after all!)

# The Rascal talks to a Roboteq MDC2200 motor controller over serial port 1.

class Motor:
  SERIAL_SPEED = 115200
  TIMEOUT_INTERVAL = 3

  def __init__(self):
    import time
    self.last_command_string = ""
    self.last_command_time = time.time()
    self.timed_out = False


  def send_command_string(self, command_string):
    import pytronics

    self.last_command_string = command_string
    pytronics.serialWrite(command_string, self.__class__.SERIAL_SPEED)
    print command_string


  def repeat_last_command_or_time_out(self):
    import time

    now = time.time()
    if (now - self.last_command_time) > self.__class__.TIMEOUT_INTERVAL:
      self.timed_out = True
      return

    self.send_command_string(self.last_command_string)


  def send_command(self, left, right):
    import time

    if (abs(left) > 1000) or (abs(right) > 1000):
      raise ValueError("Motor command out of range")

    self.last_command_time = time.time()
    self.timed_out = False

    command_string = "!M %d %d\r" % (-right, left)
    self.send_command_string(command_string)


def interpret_joystick_command(x, y):
  """Accepts a joystick position (x, y) where x and y represent a point within the unit circle.
     Returns a tuple (left, right) of the corresponding motor speeds for a left and right motor in
     a differential drive setup. For convenient use with the MDC2200, left and right are integers
     in the range -1000..1000"""

  from math import atan2, sin, cos, pi, sqrt
  angle = atan2(y, x) - pi/4

  # interpret the distance from the center
  speed = sqrt(x*x + y*y)
  if speed > 1.0:
    raise ValueError("Joystick input outside the unit circle")

  left = sin(angle)
  right = cos(angle)
  # scale the motor speeds so that, if the joystick is pushed to its maximum distance from the
  # center, the faster motor is at max speed regardless of the angle
  scale = 1000 * speed / max(abs(left), abs(right))
  return (int(scale * left + 0.5), int(scale * right + 0.5))


motor = Motor()

@public.route('/joystick', methods=['POST'])
def joystick():
  x = float(request.form['x'])
  y = float(request.form['y'])
  motor.send_command(*interpret_joystick_command(x, y))
  return "ok"

# UNCOMMENT on a working Rascal:
#@rbtimer(1)
def repeat_last_motor_command_or_time_out(num):
  motor.repeat_last_command_or_time_out()

