'''
Notes:
- callback function is only called when values change
- SD adapter has a physical lock (switch up)
- changing credentials only worked on windows
'''

import socket, time, json, math, random
from typing import TypedDict

class Button:
  '''
    represents a M5Stack button. the states are:
    0 -> button is not pressed
    1 -> button is pressed
  '''
  def __init__(self) -> None:
      self.status = 0
      self._threshold = 0.8

  def rand_switch(self, one_sec_mark: bool) -> None:
    '''
      this function switches the status of the buttom from 0 to 1 and vice versa.
      the relative temporal interval between a switch should always be the same.
      it should not be dependant of the ticks per second. therefore we
      'COUNTER % TICKS_PER_SEC == 0' results in True (one_sec_mark) just once a second. also, the 
      function should not be called with the same interval, therefore we set a
      threshold to 0.8 and the status change only happens if random.random() exceeds 0.8.
    '''
    if one_sec_mark and random.random() > self._threshold:
      self.status = 1 - self.status

class Accelerometer:
  '''
    Notes:
    - acceleration is normalised to 1.00 for the earths gravitational field of 9.81m/s^2.
    - values can be negative and exceed 1.00.
    - if the z-axis of the M5Stack is parallel to the earths gravitational axis, it is 1.00
    while x-axis and y-axis are 0.00.
    - if you move it up and down the z-axis, it resembles a sine wave.
    - M5Stack sends float values with 2 digits after decimal point.
    - accelerometer sends values in 3 axis. (e.g. {'x': 0.01, 'y': -0.07, 'z': 0.96} )
  '''

  T_Input_State = TypedDict('InputState', { 'x': str, 'y': str, 'z': str })

  def __init__(self) -> None:
    self.x, self.y, self.z = 0, 0, 0
    '''
      adding different frequencies to the sine functions. starting with 1 too prevent all
      zero values for an axis.
    '''
    self._freq_variation = 100
    self._freq_x = 1 / random.randint(1, self._freq_variation)
    self._freq_y = 1 / random.randint(1, self._freq_variation)
    self._freq_z = 1 / random.randint(1, self._freq_variation)

    self._noise_variation = 0.03

  def update(self, counter: int) -> None:
    '''
      x, y and z values are dependant of COUNTER. they also have a frequency which is a random
      int between 1 and 100. Adding a small portion of noise to each axis.
    '''
    noise_x = random.uniform(-1, 1) * self._noise_variation
    noise_y = random.uniform(-1, 1) * self._noise_variation
    noise_z = random.uniform(-1, 1) * self._noise_variation

    self.x = math.sin(counter * 2 * math.pi * self._freq_x) + noise_x
    self.y = math.sin(counter * 2 * math.pi * self._freq_y) + noise_y
    self.z = math.sin(counter * 2 * math.pi * self._freq_z) + noise_z
  
  def to_dict(self) -> T_Input_State:
    '''
      returns x, y and z values in dictionary format so that it resembles the format
      of M5Stack. Numbers are formated to two digits after decimal point.
    '''
    return {
        "x": "{0:,.2f}".format(self.x),
        "y": "{0:,.2f}".format(self.y),
        "z": "{0:,.2f}".format(self.z)
      }


IP = '127.0.0.1'
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

TICKS_PER_SEC = 10
LOOP_INTERVAL = 1 / TICKS_PER_SEC
COUNTER = 0
  
random.seed(time.time())
button_1 = Button()
accelerometer = Accelerometer()

while True:
  one_sec_mark = COUNTER % TICKS_PER_SEC == 0

  accelerometer.update(COUNTER)
  button_1.rand_switch(one_sec_mark)
  
  message = json.dumps({ "accelerometer": accelerometer.to_dict(), "button_1": button_1.status })

  sock.sendto(message.encode(), (IP, PORT))

  COUNTER += 1
  time.sleep(LOOP_INTERVAL)