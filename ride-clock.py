import logging
from controller import Controller
import schedule
from time import sleep
from datetime import datetime
from queue import Queue

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s',
  )

class Command:
  def __init__(self, key, value = None):
    self.key = key
    self.value = value

class State:
  cart_top = False
  cart_riding = False
  cart_finished = False

  lift_going_down = False
  lift_at_bottom = False
  expected_level = -1
  actual_level = -1


controller = Controller()
state = State()
commands = Queue()

def currentTimeToLevel():
  now = datetime.now()
  return (int)(now.minute / 10) % 6

def level_reached(level, value):
  if value:
    commands.put(Command("lift_level", level))

def on_lift_top(value):
  if value:
    commands.put(Command("lift_top"))
  else:
    commands.put(Command("lift_going_down"))

def on_lift_bottom(value):
  if value:
    commands.put(Command("lift_bottom"))
  else:
    commands.put(Command("lift_going_up"))


def on_cart_ride_start(value):
  if value:
    commands.put(Command("ride_start"))

def on_cart_ride_finish(value):
  if value:
    commands.put(Command("ride_finish"))

def on_cart_station(value):
  if value:
    commands.put(Command("cart_station"))

def on_cart_lift(value):
  if value:
    commands.put(Command("cart_lift"))

controller.on_lift_bottom = on_lift_bottom
controller.on_lift_middle_1 = lambda value: level_reached(1, value)
controller.on_lift_middle_2 = lambda value: level_reached(2, value)
controller.on_lift_middle_3 = lambda value: level_reached(3, value)
controller.on_lift_middle_4 = lambda value: level_reached(4, value)
controller.on_lift_middle_5 = lambda value: level_reached(5, value)
controller.on_lift_top = on_lift_top
controller.on_cart_ride_start = on_cart_ride_start
controller.on_cart_ride_finish = on_cart_ride_finish
controller.on_cart_station = on_cart_station
controller.on_cart_lift = on_cart_lift

controller.start()

def move_to(current, expected):
  logging.info("Movig from {} to {}".format(current, expected))
  while current != expected:
    controller.motor_forward(128)
    while commands.empty():
      pass
    current = commands.get()

  lift_state = current
  logging.info("Reached level {}".format(lift_state))

schedule.every().hour.at(":00").do(lambda: commands.put(Command("move_lift", 0)))
schedule.every().hour.at(":10").do(lambda: commands.put(Command("move_lift", 1)))
schedule.every().hour.at(":20").do(lambda: commands.put(Command("move_lift", 2)))
schedule.every().hour.at(":30").do(lambda: commands.put(Command("move_lift", 3)))
schedule.every().hour.at(":40").do(lambda: commands.put(Command("move_lift", 4)))
schedule.every().hour.at(":50").do(lambda: commands.put(Command("move_lift", 5)))

try:
  commands.put(Command("move_lift", currentTimeToLevel()))

  while True:
    schedule.run_pending()

    command = commands.get_nowait() if not commands.empty() else None
    if command != None:
      if command.key == "move_lift":
        state.expected_level = command.value
        controller.motor_forward(126)
        logging.info("Move lift from {} level to {} level".format(state.actual_level, state.expected_level))
        pass

      elif command.key == "lift_level":
        state.actual_level = command.value
        if state.actual_level == state.expected_level and not state.lift_going_down:
          controller.motor_stop()
          logging.info("Stopping lift on {} level".format(state.actual_level))
        else:
          logging.info("Lift passing {} level".format(state.actual_level))
        pass

      elif command.key == "lift_top":
        state.actual_level = 6
        state.cart_top = True
        controller.motor_stop()
        logging.info("Lift reached top level")
        pass

      elif command.key == "lift_going_down":
        state.lift_going_down = True
        controller.motor_stop()
        logging.info("Lift going down")
        pass

      elif command.key == "lift_bottom":
        state.lift_going_down = False
        state.lift_at_bottom = True
        state.actual_level = 0
        logging.info("Lift reach bottom")
        pass

      elif command.key == "ride_finish":
        if not state.lift_going_down:
          controller.motor_forward(96)
        logging.info("Ride finished")
        pass

      elif command.key == "ride_start":
        logging.info("Ride started")
        pass

      elif command.key == "cart_station":
        logging.info("Cart at station")
        pass

      elif command.key == "cart_lift":
        if state.lift_at_bottom:
          logging.info("Cart loaded on lift")
          if state.actual_level != state.expected_level:
            controller.motor_forward(126)
        pass

      elif command.key == "lift_going_up":
        state.lift_at_bottom = False
      pass

    sleep(0.01)
    pass

except KeyboardInterrupt:
  controller.stop()
  pass
