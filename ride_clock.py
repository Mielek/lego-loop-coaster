import logging
from time import sleep
from schedule import Scheduler
from controller import Controller
from queue import Queue
from rides import setup_controller_events, setup_clock_events, ClockRideStateMachine

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
  )

controller = Controller()
events = Queue()
scheduler = Scheduler()

setup_controller_events(controller, events)
setup_clock_events(scheduler, events)

stateMachine = ClockRideStateMachine(controller)

controller.start()
stateMachine.ride()

try:
  while True:
    scheduler.run_pending()
    if not events.empty():
      stateMachine.process_event(events.get_nowait())
    sleep(0.01)
    pass
  pass
except KeyboardInterrupt:
  controller.stop()
  pass
