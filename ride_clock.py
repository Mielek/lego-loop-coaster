import logging
from time import sleep
from threading import Thread
from schedule import Scheduler
from roller_coaster import Coaster, SensorEvent, Sensor, SensorEventType
from queue import Queue
from datetime import datetime

class ClockRideStateMachine:
  def __init__(self, coaster: Coaster):
    self._logger = logging.getLogger('Clock ride')
    self._running = False
    self._scheduler = Scheduler()
    self._scheduler_events = Queue()
    self._coaster = coaster
    self._coaster_event_handlers = {
      SensorEvent(Sensor.Lift_Down, SensorEventType.Enter): self._on_enter_bottom,
      SensorEvent(Sensor.Lift_Down, SensorEventType.Exit): self._on_exit_bottom,
      SensorEvent(Sensor.Lift_Middle_1, SensorEventType.Enter): lambda: self._on_level_enter(1),
      SensorEvent(Sensor.Lift_Middle_2, SensorEventType.Enter): lambda: self._on_level_enter(2),
      SensorEvent(Sensor.Lift_Middle_3, SensorEventType.Enter): lambda: self._on_level_enter(3),
      SensorEvent(Sensor.Lift_Middle_4, SensorEventType.Enter): lambda: self._on_level_enter(4),
      SensorEvent(Sensor.Lift_Middle_5, SensorEventType.Enter): lambda: self._on_level_enter(5),
      SensorEvent(Sensor.Lift_Top, SensorEventType.Enter): self._on_enter_top,
      SensorEvent(Sensor.Lift_Top, SensorEventType.Exit): self._on_exit_top,
      SensorEvent(Sensor.Cart_RideFinish, SensorEventType.Enter): self._on_enter_ride_finish,
      SensorEvent(Sensor.Cart_RideStart, SensorEventType.Enter): self._on_enter_ride_start,
      SensorEvent(Sensor.Cart_Lift, SensorEventType.Enter): self._on_enter_lift
    }

  def start(self):
    self._cart_top = False
    self._cart_riding = False
    self._cart_finished = False

    self._lift_going_down = False
    self._lift_at_bottom = False
    self._actual_level = -1

    self._scheduler.every().hour.at(':00').do(lambda: self._scheduler_events.put(0))
    self._scheduler.every().hour.at(':10').do(lambda: self._scheduler_events.put(1))
    self._scheduler.every().hour.at(':20').do(lambda: self._scheduler_events.put(2))
    self._scheduler.every().hour.at(':30').do(lambda: self._scheduler_events.put(3))
    self._scheduler.every().hour.at(':40').do(lambda: self._scheduler_events.put(4))
    self._scheduler.every().hour.at(':50').do(lambda: self._scheduler_events.put(5))

    if not self._running:
      self._running = True
      self._thread = Thread(name='Clock ride', target=self._run)
      self._thread.start()

    self._handle_scheduler_event((int)(datetime.now().minute / 10) % 6)

  def stop(self):
    self._running = False

  def _run(self):
    self._logger.info('Starting clock ride')
    while self._running:
      self._scheduler.run_pending()
      if not self._coaster.output.empty():
        self._handle_coaster_event(self._coaster.output.get_nowait())
      if not self._scheduler_events.empty():
        self._handle_scheduler_event(self._scheduler_events.get_nowait())
      sleep(0.01)
    self._logger.info('Finished clock ride')

  def _handle_coaster_event(self, event):
    handler = self._coaster_event_handlers.get(event)
    if handler != None:
      handler()

  def _handle_scheduler_event(self, event):
    self._expected_level = event
    self._coaster.motor_forward(126)
    self._logger.info('Move lift from {} to {}'.format(self._actual_level, self._expected_level))

  def _on_level_enter(self, level):
    self._actual_level = level
    if self._actual_level == self._expected_level and not self._lift_going_down:
      self._coaster.motor_stop()
      self._logger.info('Stopping lift on {} level'.format(self._actual_level))
    else:
      self._logger.info('Lift passing {} level'.format(self._actual_level))
    pass

  def _on_enter_top(self):
    self._actual_level = 6
    self._cart_top = True
    self._coaster.motor_stop()
    self._logger.info('Lift reached top level')

  def _on_exit_top(self):
    self._lift_going_down = True
    self._coaster.motor_stop()
    self._logger.info('Lift going down')

  def _on_enter_bottom(self):
    self._lift_going_down = False
    self._lift_at_bottom = True
    self._actual_level = 0
    self._logger.info('Lift reach bottom')

  def _on_exit_bottom(self):
    self.lift_at_bottom = False

  def _on_enter_ride_finish(self):
    if not self._lift_going_down:
      self._coaster.motor_forward(96)
    self._logger.info('Ride finished')

  def _on_enter_ride_start(self):
    self._coaster.motor_stop()
    self._logger.info('Riding! Weeeee!')

  def _on_enter_lift(self):
    if self._lift_at_bottom:
      self._logger.info('Cart loaded on lift')
      if self._actual_level != self._expected_level:
        self._coaster.motor_forward(126)


if __name__ == '__main__':
  logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    )

  coaster = Coaster()
  coaster.start()
  clockRide = ClockRideStateMachine(coaster)
  clockRide.start()
  try:
    clockRide._thread.join()
  except KeyboardInterrupt:
    pass

  clockRide.stop()
  coaster.stop()
