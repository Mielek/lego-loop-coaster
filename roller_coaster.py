import serial
from threading import Thread, current_thread
import logging
from queue import Queue
from dataclasses import dataclass
from enum import Enum

class Command(Enum):
  Stop      = b'\x00'
  Forward   = b'\x01'
  Backward  = b'\x02'
  Probe     = b'\x03'
  Treshhold = b'\x04'
  Mode      = b'\x05'
  Exit      = b'\xFF'

@dataclass
class InputEvent:
  key: Command
  value: int = 0

class Sensor(Enum):
  Lift_Down       = 0
  Lift_Middle_1   = 1
  Lift_Middle_2   = 2
  Lift_Middle_3   = 3
  Lift_Middle_4   = 4
  Lift_Middle_5   = 5
  Lift_Top        = 6
  Cart_RideStart  = 7
  Cart_RideFinish = 8
  Cart_Station    = 9
  Cart_Lift       = 10

class SensorEventType(Enum):
  Exit  = 0
  Enter = 1

@dataclass(eq=True, frozen=True)
class SensorEvent:
  sensor: Sensor
  type: SensorEventType

@dataclass
class SensorState:
  lift: int
  cart: int
  motor: int
  motor_speed: int

  def __init__(self, state: bytes):
    self.lift = int.from_bytes(state[0:1])
    self.cart = int.from_bytes(state[1:2])
    self.motor = int.from_bytes(state[2:3])
    self.motor_speed = int.from_bytes(state[3:4])

class Coaster(Thread):
  def __init__(self):
    super().__init__(name='Coaster', target=self._run)
    self._logger = logging.getLogger('Coster')
    self._connection = serial.Serial('/dev/ttyUSB0', baudrate=57600)
    self._connection.close()
    self._is_available = False
    self._current_state = SensorState(bytes(b'\x00\x00\x00\x00'))
    self._input = Queue()
    self._flags = {
      Sensor.Lift_Down:       0b00000001,
      Sensor.Lift_Middle_1:   0b00000010,
      Sensor.Lift_Middle_2:   0b00000100,
      Sensor.Lift_Middle_3:   0b00001000,
      Sensor.Lift_Middle_4:   0b00010000,
      Sensor.Lift_Middle_5:   0b00100000,
      Sensor.Lift_Top:        0b01000000,
      Sensor.Cart_RideStart:  0b00000001,
      Sensor.Cart_RideFinish: 0b00000010,
      Sensor.Cart_Station:    0b00000100,
      Sensor.Cart_Lift:       0b00001000,
    }

    self.output = Queue()

  def start(self):
    super().start()
    while not self._is_available:
      pass

  def stop(self):
    self._input.put(InputEvent(Command.Exit))
    if current_thread().name != self.name:
      self.join()
    self._connection.close()
    self._logger.info("Coaster controller stopped")

  def motor_stop(self):
    self._input.put(InputEvent(Command.Stop))
    self._logger.debug("Sending motor stop command")

  def motor_forward(self, speed: int):
    self._input.put(InputEvent(Command.Forward, speed))
    self._logger.debug("Sending motor forward command ({})".format(speed))

  def motor_backward(self, speed: int):
    self._input.put(InputEvent(Command.Backward, speed))
    self._logger.debug("Sending motor backward command ({})".format(speed))

  def change_proble(self, speed: int):
    self._input.put(InputEvent(Command.Probe, speed))
    self._logger.debug("Sending probe command ({})".format(speed))

  def change_threshold(self, value: int):
    self._input.put(InputEvent(Command.Treshhold, value))
    self._logger.debug("Sending threshhold command ({})".format(value))

  def _fire_event(self, sensor: Sensor, changed_state: int, new_state: int):
    flag = self._flags[sensor]
    if changed_state & flag > 0:
      event = SensorEvent(sensor, SensorEventType.Enter if new_state & flag > 0 else SensorEventType.Exit)
      self._logger.debug("Sending event ({})".format(event))
      self.output.put_nowait(event)

  def _read_state(self):
    state = self._connection.read(4)
    return SensorState(state)

  def _handle_sensor(self):
    state = self._read_state()
    changed_lift_state = self._current_state.lift ^ state.lift
    changed_cart_state = self._current_state.cart ^ state.cart

    self._fire_event(Sensor.Lift_Down, changed_lift_state, state.lift)
    self._fire_event(Sensor.Lift_Middle_1, changed_lift_state, state.lift)
    self._fire_event(Sensor.Lift_Middle_2, changed_lift_state, state.lift)
    self._fire_event(Sensor.Lift_Middle_3, changed_lift_state, state.lift)
    self._fire_event(Sensor.Lift_Middle_4, changed_lift_state, state.lift)
    self._fire_event(Sensor.Lift_Middle_5, changed_lift_state, state.lift)
    self._fire_event(Sensor.Lift_Top, changed_lift_state, state.lift)

    self._fire_event(Sensor.Cart_RideStart, changed_cart_state, state.cart)
    self._fire_event(Sensor.Cart_RideFinish, changed_cart_state, state.cart)
    self._fire_event(Sensor.Cart_Station, changed_cart_state, state.cart)
    self._fire_event(Sensor.Cart_Lift, changed_cart_state, state.cart)

    self._current_state = state

  def _handle_input(self):
    if not self._input.empty():
      action = self._input.get()
      if action.key != Command.Exit:
        self._connection.write(action.key.value)
        self._connection.write(action.value.to_bytes(1, 'little'))
      else:
        self._connection.write(Command.Stop.value)
        self._connection.write(b'\x00')
        self._is_available = False

  def _run(self):
    self._logger.info('Coaster controller started')
    self._connection.open()
    self._current_state = self._read_state()
    self._logger.debug('Initial state {}'.format(self._current_state))

    self._is_available = True
    while self._is_available:
      self._handle_sensor()
      self._handle_input()
