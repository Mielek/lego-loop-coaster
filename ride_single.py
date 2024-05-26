import logging
from time import sleep
from threading import Thread
from roller_coaster import Coaster, SensorEvent, Sensor, SensorEventType

class SingleRideStateMachine:
  _lift_bottom = False
  _rode = False
  _finished = True

  def __init__(self, coaster: Coaster):
    self._logger = logging.getLogger('Single ride')
    self._thread = None
    self._coaster = coaster
    self._handlers = {
      SensorEvent(Sensor.Lift_Down, SensorEventType.Enter): self._handle_enter_lift_down,
      SensorEvent(Sensor.Lift_Down, SensorEventType.Exit): self._handle_exit_lift_down,
      SensorEvent(Sensor.Lift_Top, SensorEventType.Enter): self._handle_enter_lift_top,
      SensorEvent(Sensor.Lift_Top, SensorEventType.Exit): self._handle_exit_lift_top,
      SensorEvent(Sensor.Cart_RideFinish, SensorEventType.Enter): self._handle_enter_ride_finish,
      SensorEvent(Sensor.Cart_Station, SensorEventType.Enter): self._handle_enter_station,
      SensorEvent(Sensor.Cart_Lift, SensorEventType.Enter): self._handle_enter_lift,
    }

  def start(self):
    if self._finished:
      self._lift_bottom = False
      self._rode = False
      self._finished = False
      self._coaster.motor_forward(255)
      self._thread = Thread(name='Single ride', target=self._run)
      self._thread.start()

  def stop(self):
    self._finished = True
    if self._thread != None:
      self._thread.join()

  def _run(self):
    self._logger.info("Starting single ride")
    while not self._finished:
      event = self._coaster.output.get()
      handler = self._handlers.get(event)
      if handler != None:
        handler()
    self._logger.info("Finished single ride")

  def _handle_enter_lift_down(self):
    self._lift_bottom = True

  def _handle_exit_lift_down(self):
    self._lift_bottom = False

  def _handle_enter_lift_top(self):
    self._coaster.motor_stop()

  def _handle_exit_lift_top(self):
    self._coaster.motor_stop()

  def _handle_enter_ride_finish(self):
    self._coaster.motor_forward(126)
    self._rode = True

  def _handle_enter_station(self):
    if self._rode:
      self._coaster.motor_stop()
      self._finished = True

  def _handle_enter_lift(self):
    if self._lift_bottom:
      self._coaster.motor_forward(255)

if __name__ == '__main__':
  logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    )

  coaster = Coaster()
  coaster.start()
  try:
    ride = SingleRideStateMachine(coaster)
    ride.start()
    ride._thread.join()
  except KeyboardInterrupt:
    pass

  coaster.stop()
