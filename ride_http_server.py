import logging
from datetime import datetime
from queue import Queue
from schedule import Scheduler
from controller import Controller

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
  )

controller = Controller()
events = Queue()
scheduler = Scheduler()

setup_controller_events(controller, events)
setup_clock_events(scheduler, events)


