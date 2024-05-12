import logging
from controller import Controller

logging.basicConfig(
  level=logging.DEBUG,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  )

controller = Controller()

def on_lift_up(value):
  if value:
    controller.motor_stop()
    controller.stop()

controller.on_lift_up =on_lift_up

controller.start()
while not controller.is_avaliable:
  pass

controller.motor_forward(255)

try:
  controller.wait()
except KeyboardInterrupt:
  controller.stop()
  pass
