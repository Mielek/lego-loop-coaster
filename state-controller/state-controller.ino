/**
 * Arduino state controller for lego loop coster
*/

/**
 * Pins
*/

// motor
static const byte Pin_PWM_1 = 5;
static const byte Pin_PWM_2 = 6;

// Lift sensors
static const byte Pin_Lift_Down = 3;
static const byte Pin_Lift_Middle_1 = 10;
static const byte Pin_Lift_Middle_2 = A0;
static const byte Pin_Lift_Middle_3 = A1;
static const byte Pin_Lift_Middle_4 = A2;
static const byte Pin_Lift_Middle_5 = A3;
static const byte Pin_Lift_Up = 11;

// Cart sensors
static const byte Pin_Cart_Ride_Finish = 2;
static const byte Pin_Cart_Ride_Start = 9;
static const byte Pin_Cart_On_Lift = 12;
static const byte Pin_Cart_At_Station = A4;

struct LiftFlags
{
  uint8_t bottom  : 1;
  uint8_t middle1 : 1;
  uint8_t middle2 : 1;
  uint8_t middle3 : 1;
  uint8_t middle4 : 1;
  uint8_t middle5 : 1;
  uint8_t up      : 1;
};

struct CartFlags
{
  uint8_t rideStart  : 1;
  uint8_t rideFinish : 1;
  uint8_t atStation  : 1;
  uint8_t onLift     : 1;
};
enum MotorState
{
  Stopped   = B00000000,
  Forward   = B00000001,
  Backward  = B00000010,
};

struct Sensors
{
  struct LiftFlags liftFlags;
  struct CartFlags cartFlags;
  enum MotorState motorState;
  uint8_t motorSpeed;

  uint8_t rawLiftDown;
  uint8_t rawLiftMiddle1;
  uint16_t rawLiftMiddle2;
  uint16_t rawLiftMiddle3;
  uint16_t rawLiftMiddle4;
  uint16_t rawLiftMiddle5;
  uint8_t rawLiftUp;

  uint8_t rawCartRideStart;
  uint8_t rawCartRideFinish;
  uint8_t rawCartOnLift;
  uint16_t rawCartAtStation;
};
static const size_t basicSize = 4;
static const size_t fullSize = 20;

union State
{
  struct Sensors sensors;
  char buff[fullSize];
} state;

unsigned long probeSleep = 20UL;
uint16_t threshhold = 750;

enum SerialMode
{
  Default = B00000000,
  Full = B00000001,
} serialMode;

enum Commands
{
  Command_Motor_Stop        = B00000000,
  Command_Motor_Forward     = B00000001,
  Command_Motor_Backward    = B00000010,
  Command_Set_Probe_Sleep   = B00000011,
  Command_Set_Threshhold    = B00000100,
  Command_Set_Mode          = B00000101,
};

void motorForward(byte speed)
{
  state.sensors.motorState = MotorState::Forward;
  state.sensors.motorSpeed = speed;
  analogWrite(Pin_PWM_1, 0);
  analogWrite(Pin_PWM_2, speed);
}

void motorBackward(byte speed)
{
  state.sensors.motorState = MotorState::Backward;
  state.sensors.motorSpeed = speed;
  analogWrite(Pin_PWM_1, speed);
  analogWrite(Pin_PWM_2, 0);
}

void motorStop()
{
  state.sensors.motorState = MotorState::Stopped;
  state.sensors.motorSpeed = 0;
  analogWrite(Pin_PWM_1, 0);
  analogWrite(Pin_PWM_2, 0);
}

void setupMotorPins()
{
  pinMode(Pin_PWM_1, OUTPUT);
  pinMode(Pin_PWM_2, OUTPUT);
  motorStop();
}

void setupSensorsPins()
{
  pinMode(Pin_Lift_Down, INPUT);
  pinMode(Pin_Lift_Middle_1, INPUT);
  pinMode(Pin_Lift_Middle_2, INPUT_PULLUP);
  pinMode(Pin_Lift_Middle_3, INPUT_PULLUP);
  pinMode(Pin_Lift_Middle_4, INPUT_PULLUP);
  pinMode(Pin_Lift_Middle_5, INPUT_PULLUP);
  pinMode(Pin_Lift_Up, INPUT);

  pinMode(Pin_Cart_Ride_Start, INPUT);
  pinMode(Pin_Cart_Ride_Finish, INPUT);
  pinMode(Pin_Cart_At_Station, INPUT_PULLUP);
  pinMode(Pin_Cart_On_Lift, INPUT);
}

void updateSensorState()
{
  state.sensors.rawLiftDown = digitalRead(Pin_Lift_Down);
  state.sensors.rawLiftMiddle1 = digitalRead(Pin_Lift_Middle_1);
  state.sensors.rawLiftMiddle2 = analogRead(Pin_Lift_Middle_2);
  state.sensors.rawLiftMiddle3 = analogRead(Pin_Lift_Middle_3);
  state.sensors.rawLiftMiddle4 = analogRead(Pin_Lift_Middle_4);
  state.sensors.rawLiftMiddle5 = analogRead(Pin_Lift_Middle_5);
  state.sensors.rawLiftUp = digitalRead(Pin_Lift_Up);

  state.sensors.rawCartRideStart = digitalRead(Pin_Cart_Ride_Start);
  state.sensors.rawCartRideFinish = digitalRead(Pin_Cart_Ride_Finish);
  state.sensors.rawCartAtStation = analogRead(Pin_Cart_At_Station);
  state.sensors.rawCartOnLift = digitalRead(Pin_Cart_On_Lift);

  state.sensors.liftFlags.bottom  = state.sensors.rawLiftDown & B1;
  state.sensors.liftFlags.middle1 = !(state.sensors.rawLiftMiddle1 & B1);
  state.sensors.liftFlags.middle2 = state.sensors.rawLiftMiddle2 < threshhold ? B1 : B0;
  state.sensors.liftFlags.middle3 = state.sensors.rawLiftMiddle3 < threshhold ? B1 : B0;
  state.sensors.liftFlags.middle4 = state.sensors.rawLiftMiddle4 < threshhold ? B1 : B0;
  state.sensors.liftFlags.middle5 = state.sensors.rawLiftMiddle5 < threshhold ? B1 : B0;
  state.sensors.liftFlags.up      = !(state.sensors.rawLiftUp & B1);

  state.sensors.cartFlags.rideStart   = !(state.sensors.rawCartRideStart & B1);
  state.sensors.cartFlags.rideFinish  = !(state.sensors.rawCartRideFinish & B1);
  state.sensors.cartFlags.atStation   = state.sensors.rawCartAtStation < threshhold ? B1 : B0;
  state.sensors.cartFlags.onLift      = !(state.sensors.rawCartOnLift & B1);
}

void setup()
{
  setupSensorsPins();
  setupMotorPins();
  Serial.setTimeout(100);
  Serial.begin(57600);
}

void readCommand()
{
  if (Serial.peek() > -1)
  {
    char buffer[2] = {0, 0};
    byte read = 0;
    Serial.readBytes(buffer, 2);

    switch (buffer[0])
    {
    case Command_Motor_Forward:
      motorForward(buffer[1]);
      break;
    case Command_Motor_Backward:
      motorBackward(buffer[1]);
      break;
    case Command_Motor_Stop:
      motorStop();
      break;
    case Command_Set_Probe_Sleep:
      probeSleep = buffer[1];
      break;
    case Command_Set_Threshhold:
      threshhold = ((uint16_t) buffer[1]) * 10;
      break;
    case Command_Set_Mode:
      serialMode = (SerialMode)buffer[1];
      break;
    default:
      break;
    }
  }
}

void sendState()
{
  if(serialMode == SerialMode::Default)
  {
    Serial.write(state.buff, basicSize);
  }
  else if (serialMode == SerialMode::Full)
  {
    Serial.write(state.buff, fullSize);
  }
}

void loop()
{
  unsigned long currTime = millis();

  updateSensorState();
  sendState();
  readCommand();

  unsigned long delta = probeSleep + currTime - millis();
  delay(delta);
}
