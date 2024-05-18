import logging
from controller import Controller
from statemachine import StateMachine, State

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s',
  )

controller = Controller()

class State:
  lift_bottom = False
  rode = False

state = State()

def on_lift_bottom(value):
  global state, controller
  state.lift_bottom = value

def on_cart_lift(value):
  global state, controller
  if value and state.lift_bottom:
    controller.motor_forward(126)
    on_lift = True

def on_lift_top(value):
  global state, controller
  controller.motor_stop()

def on_cart_ride_finish(value):
  global state, controller
  if value:
    state.rode = True
    controller.motor_forward(96)

def on_cart_station(value):
  global state, controller
  if value and state.rode:
    controller.stop()


controller.on_cart_lift = on_cart_lift
controller.on_lift_top = on_lift_top
controller.on_lift_bottom = on_lift_bottom
controller.on_cart_ride_finish = on_cart_ride_finish
controller.on_cart_station = on_cart_station

controller.start()

logging.info("Single ride")
controller.motor_forward(128)

try:
  controller.join()
  logging.info("Ride finished")
except KeyboardInterrupt:
  controller.stop()
  pass
