from statemachine import StateMachine, State

class CartStateMachine(StateMachine):
  "Cart state machine"
  initial=State(initial=True)

  on_lift=State()
  arrived_on_top=State()
  begin_ride=State()
  riding=State()
  finished_ride=State()
  at_weel=State()
  at_station=State()

  initialize_on_lift = initial.to(on_lift)
  initialize_at_station = initial.to(at_station)

  transitions = (
    on_lift.to(arrived_on_top)
    | arrived_on_top.to(begin_ride)
    | begin_ride.to(riding)
    | riding.to(finished_ride)
    | finished_ride.to(at_weel)
    | at_weel.to(at_station)
    | at_station.to(on_lift)
  )



