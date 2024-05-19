import logging
from time import sleep
from controller import Controller
from queue import Queue
from rides import setup_controller_events, SingleRideStateMachine

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
  )

events = Queue()
controller = Controller()
setup_controller_events(controller, events)

stateMachine = SingleRideStateMachine(controller)

controller.start()

logging.info("Single ride")
stateMachine.ride()

try:

  while not stateMachine.finished:
    if not events.empty():
      stateMachine.process_event(events.get_nowait())
    sleep(0.01)

  logging.info("Ride finished")
  controller.stop()

except KeyboardInterrupt:
  controller.stop()
  pass
