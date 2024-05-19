import logging
from queue import Queue
from schedule import Scheduler
from controller import Controller
from datetime import datetime

logger = logging.getLogger("rides")

class Event:
  def __init__(self, key, data = None):
    self.key = key
    self.data = data
  pass

  def __str__(self):
    return "Event(key={}, data={})".format(self.key, self.data)

def setup_controller_events(controller: Controller, events: Queue):
  controller.on_lift_bottom   = lambda value: events.put(Event('on_enter_bottom'  if value else 'on_exit_bottom', 0))
  controller.on_lift_middle_1 = lambda value: events.put(Event('on_enter_level'   if value else 'on_exit_level' , 1))
  controller.on_lift_middle_2 = lambda value: events.put(Event('on_enter_level'   if value else 'on_exit_level' , 2))
  controller.on_lift_middle_3 = lambda value: events.put(Event('on_enter_level'   if value else 'on_exit_level' , 3))
  controller.on_lift_middle_4 = lambda value: events.put(Event('on_enter_level'   if value else 'on_exit_level' , 4))
  controller.on_lift_middle_5 = lambda value: events.put(Event('on_enter_level'   if value else 'on_exit_level' , 5))
  controller.on_lift_top      = lambda value: events.put(Event('on_enter_top'     if value else 'on_exit_top'   , 6))

  controller.on_cart_lift         = lambda value: events.put(Event('on_enter_lift' if value else 'on_exit_lift'))
  controller.on_cart_station      = lambda value: events.put(Event('on_enter_station' if value else 'on_exit_station'))
  controller.on_cart_ride_finish  = lambda value: events.put(Event('on_enter_ride_finish' if value else 'on_exit_ride_finish'))
  controller.on_cart_ride_start   = lambda value: events.put(Event('on_enter_ride_start' if value else 'on_exit_ride_start'))

class SingleRideStateMachine:
  _lift_bottom = False
  _rode = False
  finished = False

  def __init__(self, controller: Controller):
    self.controller = controller

  def __str__(self):
    return "SingleRideStateMachine(lift_bottom={}, rode={}, finished={})".format(self._lift_bottom, self._rode, self.finished)

  def ride(self):
    self.lift_bottom = False
    self.rode = False
    self.finished = False
    self.controller.motor_forward(126)
    logger.info("Single ride start")

  def process_event(self, event: Event):
    logger.debug("Processing event ({})".format(event))
    if event.key == 'on_enter_bottom':
      self._lift_bottom = True
      logger.info("Setting lift bottom on enter ({})".format(self))
      pass
    elif event.key == 'on_exit_bottom':
      self._lift_bottom = False
      logger.info("Setting lift bottom on exit ({})".format(self))
      pass
    elif event.key == 'on_enter_top':
      self.controller.motor_stop()
      logger.info("Stopping motor on top ({})".format(self))
      pass
    elif event.key == 'on_enter_ride_finish':
      self.controller.motor_forward(96)
      self._rode = True
      logger.info("Finished ride ({})".format(self))
      pass
    elif event.key == 'on_enter_station':
      if self._rode:
        self.controller.motor_stop()
        self.finished = True
      logger.info("Entering station ({})".format(self))
      pass
    elif event.key == "on_enter_ride_start":
      logging.info("Riding! Weeeee!")
      pass
    pass

def setup_clock_events(scheduler: Scheduler, events: Queue):
  scheduler.every().hour.at(":00").do(lambda: events.put(Event("move_lift", 0)))
  scheduler.every().hour.at(":10").do(lambda: events.put(Event("move_lift", 1)))
  scheduler.every().hour.at(":20").do(lambda: events.put(Event("move_lift", 2)))
  scheduler.every().hour.at(":30").do(lambda: events.put(Event("move_lift", 3)))
  scheduler.every().hour.at(":40").do(lambda: events.put(Event("move_lift", 4)))
  scheduler.every().hour.at(":50").do(lambda: events.put(Event("move_lift", 5)))

class ClockRideStateMachine:
  cart_top = False
  cart_riding = False
  cart_finished = False

  lift_going_down = False
  lift_at_bottom = False
  expected_level = -1
  actual_level = -1

  def __init__(self, controller: Controller):
    self.controller = controller

  def __str__(self):
    return "ClockRideStateMachine(actual_level={}, expected_level={}, lift_at_bottom={}, lift_going_down={}, cart_finished={}, cart_riding={}, cart_top={})".format(
      self.actual_level,
      self.expected_level,
      self.lift_at_bottom,
      self.lift_going_down,
      self.cart_finished,
      self.cart_riding,
      self.cart_top
    )

  def ride(self):
    self.cart_top = False
    self.cart_riding = False
    self.cart_finished = False

    self.lift_going_down = False
    self.lift_at_bottom = False

    self.expected_level = (int)(datetime.now().minute / 10) % 6
    self.actual_level = -1

    self.process_event(Event("move_lift", self.expected_level))
    logger.info("Clock ride start")

  def process_event(self, event: Event):
    logger.debug("Processing event ({})".format(event))

    if event.key == "move_lift":
      self.expected_level = event.data
      self.controller.motor_forward(126)
      logger.info("Move lift from {} to {}".format(self.actual_level, self.expected_level))
      pass

    elif event.key == "on_enter_level":
      self.actual_level = event.data
      if self.actual_level == self.expected_level and not self.lift_going_down:
        self.controller.motor_stop()
        logging.info("Stopping lift on {} level".format(self.actual_level))
      else:
        logging.info("Lift passing {} level".format(self.actual_level))
      pass

    elif event.key == 'on_enter_top':
      self.actual_level = 6
      self.cart_top = True
      self.controller.motor_stop()
      logging.info("Lift reached top level")
      pass

    elif event.key == 'on_exit_top':
      self.lift_going_down = True
      self.controller.motor_stop()
      logging.info("Lift going down")
      pass

    elif event.key == 'on_enter_bottom':
      self.lift_going_down = False
      self.lift_at_bottom = True
      self.actual_level = 0
      logging.info("Lift reach bottom")
      pass

    elif event.key == 'on_exit_bottom':
      self.lift_at_bottom = False
      pass

    elif event.key == 'on_enter_ride_finish':
      if not self.lift_going_down:
        self.controller.motor_forward(96)
      logging.info("Ride finished")
      pass

    elif event.key == 'on_enter_ride_start':
      self.controller.motor_stop()
      logging.info("Riding! Weeeee!")
      pass

    elif event.key == 'on_enter_station':
      logging.info("Cart at station")
      pass

    elif event.key == "on_enter_lift":
      if self.lift_at_bottom:
        logging.info("Cart loaded on lift")
        if self.actual_level != self.expected_level:
          self.controller.motor_forward(126)
      pass

    pass
  pass
