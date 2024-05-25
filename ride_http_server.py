import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep
from queue import Queue
from schedule import Scheduler
from controller import Controller
from rides import setup_controller_events, setup_clock_events, ClockRideStateMachine, SingleRideStateMachine
from threading import Thread, current_thread

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
  )

controller = Controller()
events = Queue()
scheduler = Scheduler()

setup_controller_events(controller, events)
setup_clock_events(scheduler, events)

clock = ClockRideStateMachine(controller)
single = SingleRideStateMachine(controller)

stateMachine = None

hostName = "localhost"
serverPort = 8080

class DrahaController(BaseHTTPRequestHandler):
  def do_POST(self):
    global current, single, clock
    if self.path.endswith('/single'):
      single.ride()
      stateMachine = single
      self.send_response(200)
    elif self.path.endswith('/clock'):
      clock.ride()
      stateMachine = clock
      self.send_response(200)
    elif self.path.endswith('/stop'):
      stateMachine = None
      self.send_response(200)
    else:
      self.send_response(404)
    pass

webServer = HTTPServer((hostName, serverPort), DrahaController)
logging.info("Server started http://%s:%s" % (hostName, serverPort))

def schedulerLoopFn():
  global scheduler, events, stateMachine
  while True:
    scheduler.run_pending()
    if not events.empty():
      event = events.get_nowait()
      if stateMachine != None:
        stateMachine.process_event(event)
    sleep(0.01)
    pass
  pass

schedulerLoop = Thread(target=schedulerLoopFn)

schedulerLoop.start()
controller.start()
try:
  webServer.serve_forever()
except KeyboardInterrupt:
  pass

controller.stop()
webServer.server_close()
logging.info("Server stopped.")

