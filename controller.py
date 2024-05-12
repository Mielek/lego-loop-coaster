import serial
from threading import Thread, current_thread
import logging
from queue import Queue

Lift_Down     = 0b00000001
Lift_Middle_1 = 0b00000010
Lift_Middle_2 = 0b00000100
Lift_Middle_3 = 0b00001000
Lift_Middle_4 = 0b00010000
Lift_Middle_5 = 0b00100000
Lift_Top       = 0b01000000

Cart_RideStart  = 0b00000001
Cart_RideFinish = 0b00000010
Cart_Station    = 0b00000100
Cart_Lift       = 0b00001000

Command_Stop      = b'\x00'
Command_Forward   = b'\x01'
Command_Backward  = b'\x02'

class Controller(Thread):
  connection = serial.Serial('/dev/ttyUSB0')
  connection.close()

  action_queue = Queue()

  last_lift_state = 0b00000000
  last_cart_state = 0b00000000
  motor_state = Command_Stop
  motor_speed = 0

  on_lift_down = None
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

  is_avaliable = False

  def start(self):
    super().start()
    while not self.is_avaliable:
      pass


  def stop(self):
    self.action_queue.put({ "key": "exit" })
    if current_thread().name != self.name:
      self.join()

  def motor_stop(self):
    self.action_queue.put({ "key": "stop" })

  def motor_forward(self, speed: int):
    self.action_queue.put({ "key": "forward", "value": speed })

  def motor_backward(self, speed: int):
    self.action_queue.put({ "key": "backward", "value": speed })

  def fire_lift_events(self, state):
    changed_lift_state = self.last_lift_state ^ state
    logging.debug("{}, {}, {}".format(self.last_lift_state, state, changed_lift_state))

    def process(flag, action):
      if changed_lift_state & flag > 0:
        value = True if state & flag > 0 else False
        logger.debug("Lift {} flag chage {} -> {}",flag, not value, value)
        if action is not None:
          action(value)

    process(Lift_Down, self.on_lift_down,)
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
        logger.debug("Cart {} flag chage {} -> {}",flag, not value, value)
        if action is not None:
          action(value)

    process(Cart_RideStart, self.on_cart_ride_start)
    process(Cart_RideFinish, self.on_cart_ride_finish)
    process(Cart_Station, self.on_cart_station)
    process(Cart_Lift, self.on_cart_lift)

    self.last_cart_state = state

  def run(self):
    self.connection.open()
    state = self.connection.read(4)
    logging.debug("Initial state {}".format(state))
    self.last_lift_state = int.from_bytes(state[0:1])
    self.last_cart_state = int.from_bytes(state[1:2])
    self.motor_state = int.from_bytes(state[2:3])
    self.motor_speed = int.from_bytes(state[3:4])

    self.is_avaliable = True
    while self.is_avaliable:
      state = self.connection.read(4)
      logging.debug("New state {}".format(state))

      new_lift_state = int.from_bytes(state[0:1])
      new_cart_state = int.from_bytes(state[1:2])
      self.motor_state = int.from_bytes(state[2:3])
      self.motor_speed = int.from_bytes(state[3:4])

      self.fire_lift_events(new_lift_state)
      self.fire_cart_events(new_cart_state)

      if not self.action_queue.empty():
        action = self.action_queue.get()
        key = action["key"]
        if key == "forward":
          self.connection.write(Command_Forward)
          self.connection.write(action["value"].to_bytes(1, 'little'))
        elif key == "backward":
          self.connection.write(Command_Backward)
          self.connection.write(action["value"].to_bytes(1, 'little'))
        elif key == "stop":
          self.connection.write(Command_Stop)
          self.connection.write(b'\x00')
        elif key == "exit":
          self.connection.write(Command_Stop)
          self.connection.write(b'\x00')
          self.is_avaliable = False
        else:
          logging.warning("Unknow action {}", action)

      pass

    self.connection.close()
