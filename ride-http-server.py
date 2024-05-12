import logging
from controller import Controller

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s',
  )

controller = Controller()

def on_lift_up(value):
  if not value:
    controller.motor_stop()
    controller.stop()

controller.on_lift_top = on_lift_up

controller.start()
controller.motor_forward(125)

try:
  controller.wait()
except KeyboardInterrupt:
  controller.stop()
  pass
