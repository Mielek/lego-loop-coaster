import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from queue import Queue
from schedule import Scheduler
from controller import Controller
from rides import setup_controller_events, setup_clock_events, ClockRideStateMachine, SingleRideStateMachine

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

hostName = "localhost"
serverPort = 8080

class DrahaController(BaseHTTPRequestHandler):
  def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
  def do_POST(self):
    pass


webServer = HTTPServer((hostName, serverPort), DrahaController)
logging.info("Server started http://%s:%s" % (hostName, serverPort))

try:
  webServer.serve_forever()
except KeyboardInterrupt:
  pass

webServer.server_close()
logging.info("Server stopped.")

