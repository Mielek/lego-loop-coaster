import logging
from http.server import SimpleHTTPRequestHandler, HTTPServer
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

hostName = "0.0.0.0"
serverPort = 8080

class DrahaController(SimpleHTTPRequestHandler):
  def do_GET(self):
    self.path = 'index.html'
    return SimpleHTTPRequestHandler.do_GET(self)
  def do_POST(self):
    global current, single, clock
    if self.path.endswith('/single'):
      clockRide.stop()
      singleRide.start()
    elif self.path.endswith('/clock'):
      singleRide.stop()
      clockRide.start()
    elif self.path.endswith('/stop'):
      singleRide.stop()
      clockRide.stop()

    return self.do_GET()

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

