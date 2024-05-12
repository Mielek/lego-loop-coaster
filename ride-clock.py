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

controller = Controller()
lift_state = 8
q = Queue()

def currentTimeToLevel():
  now = datetime.now()
  if now.minute >= 0 and now.minute < 10:
    return 0
  elif now.minute >= 10 and now.minute < 20:
    return 1
  elif now.minute >= 20 and now.minute < 30:
    return 2
  elif now.minute >= 30 and now.minute < 40:
    return 3
  elif now.minute >= 40 and now.minute < 50:
    return 4
  else:
    return 5

def level_reached(level, value):
  if value:
    logging.info("Reached level {}".format(level))
    q.put(level)
    controller.motor_stop()

def on_lift_up(value):
  if not value:
    q.put(0)
    controller.motor_stop()
  else:
    logging.info("Reached top")

def on_lift_down(value):
  if value:
    logging.info("Reached bottom")

controller.on_lift_down = on_lift_down
controller.on_lift_middle_1 = lambda value: level_reached(1, value)
controller.on_lift_middle_2 = lambda value: level_reached(2, value)
controller.on_lift_middle_3 = lambda value: level_reached(3, value)
controller.on_lift_middle_4 = lambda value: level_reached(4, value)
controller.on_lift_middle_5 = lambda value: level_reached(5, value)
controller.on_lift_top = on_lift_up

controller.start()

def move_to(current, expected):
  logging.info("Movig from {} to {}".format(current, expected))
  while current != expected:
    controller.motor_forward(128)
    while q.empty():
      pass
    current = q.get()

  lift_state = current
  logging.info("Reached level {}".format(lift_state))

schedule.every().hour.at(":00").do(lambda: move_to(lift_state, 0))
schedule.every().hour.at(":10").do(lambda: move_to(lift_state, 1))
schedule.every().hour.at(":20").do(lambda: move_to(lift_state, 2))
schedule.every().hour.at(":30").do(lambda: move_to(lift_state, 3))
schedule.every().hour.at(":40").do(lambda: move_to(lift_state, 4))
schedule.every().hour.at(":50").do(lambda: move_to(lift_state, 5))

try:
  move_to(lift_state, currentTimeToLevel())

  while True:
    schedule.run_pending()
    sleep(1)

except KeyboardInterrupt:
  controller.stop()
  pass
