import logging
from controller import Controller
from statemachine import StateMachine, State

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s',
  )

controller = Controller()
states = {
  "lift_down": False,
  "rode": False
}

def on_lift_down(value):
  global states, controller
  states["lift_down"] = value

def on_cart_lift(value):
  global states, controller
  if value and states["lift_down"]:
    controller.motor_forward(126)
    on_lift = True

def on_lift_top(value):
  global states, controller
  controller.motor_stop()

def on_cart_ride_finish(value):
  global states, controller
  if value:
    states["rode"] = True
    controller.motor_forward(96)

def on_cart_station(value):
  global states, controller
  if value and states["rode"]:
    controller.stop()


controller.on_cart_lift = on_cart_lift
controller.on_lift_top = on_lift_top
controller.on_lift_down = on_lift_down
controller.on_cart_ride_finish = on_cart_ride_finish
controller.on_cart_station = on_cart_station

controller.start()

controller.motor_forward(128)

try:
  controller.join()
except KeyboardInterrupt:
  controller.stop()
  pass
