import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from roller_coaster import Coaster
from ride_single import SingleRideStateMachine
from ride_clock import ClockRideStateMachine

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
  )

coaster = Coaster()
coaster.start()

clockRide = ClockRideStateMachine(coaster)
singleRide = SingleRideStateMachine(coaster)

hostName = "localhost"
serverPort = 8080

class DrahaController(BaseHTTPRequestHandler):
  def do_POST(self):
    global current, single, clock
    if self.path.endswith('/single'):
      clockRide.stop()
      singleRide.start()
      self.send_response(200)
    elif self.path.endswith('/clock'):
      singleRide.stop()
      clockRide.start()
      self.send_response(200)
    elif self.path.endswith('/stop'):
      singleRide.stop()
      clockRide.stop()
      self.send_response(200)
    else:
      self.send_response(404)
    pass

webServer = HTTPServer((hostName, serverPort), DrahaController)
logging.info("Server started http://%s:%s" % (hostName, serverPort))

try:
  webServer.serve_forever()
except KeyboardInterrupt:
  pass

webServer.server_close()
coaster.stop()
clockRide.stop()
singleRide.stop()
logging.info("Server stopped.")

