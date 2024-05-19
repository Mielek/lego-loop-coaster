import serial
from threading import Thread, current_thread
import logging
from queue import Queue

logger = logging.getLogger("controller")

Lift_Down     = 0b00000001
Lift_Middle_1 = 0b00000010
Lift_Middle_2 = 0b00000100
Lift_Middle_3 = 0b00001000
Lift_Middle_4 = 0b00010000
Lift_Middle_5 = 0b00100000
Lift_Top      = 0b01000000

Cart_RideStart  = 0b00000001
Cart_RideFinish = 0b00000010
Cart_Station    = 0b00000100
Cart_Lift       = 0b00001000

Command_Stop      = b'\x00'
Command_Forward   = b'\x01'
Command_Backward  = b'\x02'
Command_Probe     = b'\x03'
Command_Treshhold = b'\x04'
Command_Mode      = b'\x05'

class ControllerEvent:
  def __init__(self, key, value = None):
    self.key = key
    self.value = value

class Controller(Thread):
  _connection = serial.Serial('/dev/ttyUSB0', baudrate=57600)
  _connection.close()

  _input = Queue()

  _last_lift_state = 0b00000000
  _last_cart_state = 0b00000000
  _motor_state = Command_Stop
  _motor_speed = 0

  _is_available = False

  on_lift_bottom = None
  on_lift_middle_1 = None
  on_lift_middle_2 = None
  on_lift_middle_3 = None
  on_lift_middle_4 = None
  on_lift_middle_5 = None
  on_lift_top = None

  on_cart_ride_start = None
  on_cart_ride_finish = None
  on_cart_station = None
  on_cart_lift = None

  def start(self):
    super().start()
    while not self._is_available:
      pass

  def stop(self):
    self._input.put(ControllerEvent("exit"))
    if current_thread().name != self.name:
      self.join()
    self._connection.close()

  def motor_stop(self):
    self._input.put(ControllerEvent("stop"))

  def motor_forward(self, speed: int):
    self._input.put(ControllerEvent("forward", speed))

  def motor_backward(self, speed: int):
    self._input.put(ControllerEvent("backward", speed))

  def change_proble(self, speed: int):
    self._input.put(ControllerEvent("probe", speed))

  def change_threshold(self, speed: int):
    self._input.put(ControllerEvent("threshold", speed))

  def fire_lift_events(self, state):
    changed_lift_state = self.last_lift_state ^ state

    def process(flag, action):
      if changed_lift_state & flag > 0:
        value = True if state & flag > 0 else False
        logging.debug("Lift {} flag change {} -> {}".format(flag, not value, value))
        if action is not None:
          action(value)

    process(Lift_Down, self.on_lift_bottom)
    process(Lift_Middle_1, self.on_lift_middle_1)
    process(Lift_Middle_2, self.on_lift_middle_2)
    process(Lift_Middle_3, self.on_lift_middle_3)
    process(Lift_Middle_4, self.on_lift_middle_4)
    process(Lift_Middle_5, self.on_lift_middle_5)
    process(Lift_Top, self.on_lift_top)

    self.last_lift_state = state

  def fire_cart_events(self, state):
    changed_cart_state = self.last_cart_state ^ state

    def process(flag, action):
      if changed_cart_state & flag > 0:
        value = True if state & flag > 0 else False
        logger.debug("Cart {} flag change {} -> {}".format(flag, not value, value))
        if action is not None:
          action(value)

    process(Cart_RideStart, self.on_cart_ride_start)
    process(Cart_RideFinish, self.on_cart_ride_finish)
    process(Cart_Station, self.on_cart_station)
    process(Cart_Lift, self.on_cart_lift)

    self.last_cart_state = state

  def run(self):
    self._connection.open()
    state = self._connection.read(4)
    logger.debug("Initial state {}".format(state))
    self.last_lift_state = int.from_bytes(state[0:1])
    self.last_cart_state = int.from_bytes(state[1:2])
    self.motor_state = int.from_bytes(state[2:3])
    self.motor_speed = int.from_bytes(state[3:4])

    self._is_available = True
    while self._is_available:
      state = self._connection.read(4)
      # logger.debug("New state {}".format(state))

      new_lift_state = int.from_bytes(state[0:1])
      new_cart_state = int.from_bytes(state[1:2])
      self.motor_state = int.from_bytes(state[2:3])
      self.motor_speed = int.from_bytes(state[3:4])

      self.fire_lift_events(new_lift_state)
      self.fire_cart_events(new_cart_state)

      if not self._input.empty():
        action = self._input.get()
        key = action.key
        if key == "forward":
          value = action.value.to_bytes(1, 'little')
          logger.debug("Sending forward command {}".format(value))
          self._connection.write(Command_Forward)
          self._connection.write(value)
          pass

        elif key == "backward":
          value = action.value.to_bytes(1, 'little')
          logger.debug("Sending backward command {}".format(value))
          self._connection.write(Command_Backward)
          self._connection.write(value)
          pass

        elif key == "stop":
          logger.debug("Sending stop command")
          self._connection.write(Command_Stop)
          self._connection.write(b'\x00')
          pass

        elif key == "probe":
          value = action.value.to_bytes(1, 'little')
          logger.debug("Sending probe command ({})".format(value))
          self._connection.write(Command_Probe)
          self._connection.write(value)
          pass

        elif key == "threshold":
          value = action.value.to_bytes(1, 'little')
          logger.debug("Sending threshold command ({})".format(value))
          self._connection.write(Command_Treshhold)
          self._connection.write(value)
          pass

        elif key == "exit":
          logger.debug("Sending stop command")
          self._connection.write(Command_Stop)
          self._connection.write(b'\x00')

          logger.debug("Exiting sensor loop")
          self._is_available = False
        else:
          logger.warning("Unknow action {}".format(action))

      pass
