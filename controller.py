import serial
from enum import Enum
import threading
import logging

Lift_Down     = 0b00000001
Lift_Middle_1 = 0b00000010
Lift_Middle_2 = 0b00000100
Lift_Middle_3 = 0b00001000
Lift_Middle_4 = 0b00010000
Lift_Middle_5 = 0b00100000
Lift_Up       = 0b01000000

Cart_RideStart  = 0b00000001
Cart_RideFinish = 0b00000010
Cart_Station    = 0b00000100
Cart_Lift       = 0b00001000

Command_Stop      = b'\x00'
Command_Forward   = b'\x01'
Command_Backward  = b'\x02'

class Controller:
  connection = serial.Serial('/dev/ttyUSB0')
  connection.close()

  last_lift_state = 0b00000000
  last_cart_state = 0b00000000

  on_lift_down = None
  on_lift_middle_1 = None
  on_lift_middle_2 = None
  on_lift_middle_3 = None
  on_lift_middle_4 = None
  on_lift_middle_5 = None
  on_lift_up = None

  on_cart_ride_start = None
  on_cart_ride_finish = None
  on_cart_station = None
  on_cart_lift = None

  is_avaliable = False

  def __init__(self):
    self.thread = threading.Thread(name="Controller thread", target=self.loop)

  def start(self):
    self.thread.start()

  def wait(self):
    self.thread.join()

  def stop(self):
    self.motor_stop()
    self.is_avaliable = False
    self.connection.close()

  def motor_stop(self):
    self.connection.write(Command_Stop)

  def motor_forward(self, speed: int):
    self.connection.write(Command_Forward)
    self.connection.write(speed.to_bytes(1, 'little'))

  def motor_backward(self, speed: int):
    self.connection.write(Command_Backward)
    self.connection.write(speed.to_bytes(1, 'little'))

  def fire_lift_events(self, state):
    changed_lift_state = self.last_lift_state ^ state

    if changed_lift_state & Lift_Down > 0 and self.on_lift_down is not None:
      self.on_lift_down(True if state & Lift_Down > 0 else False)
    if changed_lift_state & Lift_Middle_1 > 0 and self.on_lift_middle_1 is not None:
      self.on_lift_middle_1(True if state & Lift_Middle_1 > 0 else False)
    if changed_lift_state & Lift_Middle_2 > 0 and self.on_lift_middle_2 is not None:
      self.on_lift_middle_2(True if state & Lift_Middle_2 > 0 else False)
    if changed_lift_state & Lift_Middle_3 > 0 and self.on_lift_middle_3 is not None:
      self.on_lift_middle_3(True if state & Lift_Middle_3 > 0 else False)
    if changed_lift_state & Lift_Middle_4 > 0 and self.on_lift_middle_4 is not None:
      self.on_lift_middle_4(True if state & Lift_Middle_4 > 0 else False)
    if changed_lift_state & Lift_Middle_5 > 0 and self.on_lift_middle_5 is not None:
      self.on_lift_middle_5(True if state & Lift_Middle_5 > 0 else False)
    if changed_lift_state & Lift_Up > 0 and self.on_lift_up is not None:
      self.on_lift_up(True if state & Lift_Up > 0 else False)

    self.last_lift_state = state

  def fire_cart_events(self, state):
    changed_cart_state = self.last_cart_state ^ state

    if changed_cart_state & Cart_RideStart > 0 and self.on_cart_ride_start is not None:
      self.on_cart_ride_start(True if state & Cart_RideStart > 0 else False)
    if changed_cart_state & Cart_RideFinish > 0 and self.on_cart_ride_finish is not None:
      self.on_cart_ride_finish(True if state & Cart_RideFinish > 0 else False)
    if changed_cart_state & Cart_Station > 0 and self.on_cart_station is not None:
      self.on_cart_station(True if state & Cart_Station > 0 else False)
    if changed_cart_state & Cart_Lift > 0 and self.on_cart_lift is not None:
      self.on_cart_lift(True if state & Cart_Lift > 0 else False)

    self.last_cart_state = state


  def loop(self):
    self.connection.open()
    self.connection.read(4)
    self.is_avaliable = True
    while self.is_avaliable:
      state = self.connection.read(4)
      # logging.debug("State {}".format(state))

      new_lift_state = int.from_bytes(state[0:1])
      new_cart_state = int.from_bytes(state[1:2])
      motor_state = int.from_bytes(state[2:3])
      motor_speed = int.from_bytes(state[3:4])

      self.fire_lift_events(new_lift_state)
      self.fire_cart_events(new_cart_state)
      pass
