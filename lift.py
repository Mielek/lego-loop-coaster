from statemachine import StateMachine, State

class LiftStateMachine(StateMachine):
  "Lift state machine"
  initial=State(initial=True)

  at_bottom=State()
  at_middle_1=State()
  at_middle_2=State()
  at_middle_3=State()
  at_middle_4=State()
  at_middle_5=State()
  at_top=State()

  moving_down=State()
  moving_up=State()

  initialize_bottom = initial.to(at_bottom)
  initialize_middle_1 = initial.to(at_middle_1)
  initialize_middle_2 = initial.to(at_middle_2)
  initialize_middle_3 = initial.to(at_middle_3)
  initialize_middle_4 = initial.to(at_middle_4)
  initialize_middle_5 = initial.to(at_middle_5)
  initialize_top = initial.to(at_top)
  initialize_moving_up = initial.to(moving_up)
  initialize_moving_down = initial.to(moving_down)

  move_up = (
    at_bottom.to(moving_up)
    | at_middle_1.to(moving_up)
    | at_middle_2.to(moving_up)
    | at_middle_3.to(moving_up)
    | at_middle_4.to(moving_up)
    | at_middle_5.to(moving_up)
  )

  move_down = (
    at_top.to(moving_down)
    | at_middle_5.to(moving_down)
    | at_middle_4.to(moving_down)
    | at_middle_3.to(moving_down)
    | at_middle_2.to(moving_down)
    | at_middle_1.to(moving_down)
  )

  stop_at_bottom = moving_down.to(at_bottom)
  stop_on_top = moving_up.to(at_top)
  stop_at_middle_1 = (moving_up.to(at_middle_1) | moving_down.to(at_middle_1))
  stop_at_middle_2 = (moving_up.to(at_middle_2) | moving_down.to(at_middle_2))
  stop_at_middle_3 = (moving_up.to(at_middle_3) | moving_down.to(at_middle_3))
  stop_at_middle_4 = (moving_up.to(at_middle_4) | moving_down.to(at_middle_4))
  stop_at_middle_5 = (moving_up.to(at_middle_5) | moving_down.to(at_middle_5))
