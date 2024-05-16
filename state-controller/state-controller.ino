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

enum MotorState
{
  Motor_Stopped = B00000000,
  Motor_Forward = B00000001,
  Motor_Backward = B00000010,
} motorState;
byte motorSpeed = 0;

void motorForward(byte speed)
{
  motorState = Motor_Forward;
  motorSpeed = speed;
  analogWrite(Pin_PWM_1, 0);
  analogWrite(Pin_PWM_2, speed);
}

void motorBackward(byte speed)
{
  motorState = Motor_Backward;
  motorSpeed = speed;
  analogWrite(Pin_PWM_1, speed);
  analogWrite(Pin_PWM_2, 0);
}

void motorStop()
{
  motorState = Motor_Stopped;
  motorSpeed = 0;
  analogWrite(Pin_PWM_1, 0);
  analogWrite(Pin_PWM_2, 0);
}

void setupMotorPins()
{
  pinMode(Pin_PWM_1, OUTPUT);
  pinMode(Pin_PWM_2, OUTPUT);
  motorStop();
}

static const int threshhold = 900;

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

int sensorRawLiftDown = 0;
int sensorRawLiftMiddel1 = 0;
int sensorRawLiftMiddle2 = 0;
int sensorRawLiftMiddle3 = 0;
int sensorRawLiftMiddle4 = 0;
int sensorRawLiftMiddle5 = 0;
int sensorRawLiftUp = 0;

int sensorRawCartRideStart= 0;
int sensorRawCartRideFinish = 0;
int sensorRawCartAtStation = 0;
int sensorRawCartOnLift = 0;

int liftFlags = 0;
int cartFlags = 0;

void updateSensorState()
{
  sensorRawLiftDown = digitalRead(Pin_Lift_Down);
  sensorRawLiftMiddel1 = digitalRead(Pin_Lift_Middle_1);
  sensorRawLiftMiddle2 = analogRead(Pin_Lift_Middle_2);
  sensorRawLiftMiddle3 = analogRead(Pin_Lift_Middle_3);
  sensorRawLiftMiddle4 = analogRead(Pin_Lift_Middle_4);
  sensorRawLiftMiddle5 = analogRead(Pin_Lift_Middle_5);
  sensorRawLiftUp = digitalRead(Pin_Lift_Up);

  sensorRawCartRideStart = digitalRead(Pin_Cart_Ride_Start);
  sensorRawCartRideFinish = digitalRead(Pin_Cart_Ride_Finish);
  sensorRawCartAtStation = analogRead(Pin_Cart_At_Station);
  sensorRawCartOnLift = digitalRead(Pin_Cart_On_Lift);

  liftFlags = sensorRawLiftDown << 0
  | !sensorRawLiftMiddel1 << 1
  | (sensorRawLiftMiddle2 < threshhold ? 1 : 0) << 2
  | (sensorRawLiftMiddle3 < threshhold ? 1 : 0) << 3
  | (sensorRawLiftMiddle4 < threshhold ? 1 : 0) << 4
  | (sensorRawLiftMiddle5 < threshhold ? 1 : 0) << 5
  | !sensorRawLiftUp << 6;

  cartFlags = !sensorRawCartRideStart << 0
  | !sensorRawCartRideFinish << 1
  | (sensorRawCartAtStation < threshhold ? 1 : 0) << 2
  | !sensorRawCartOnLift << 3;
}


void setup()
{
  setupSensorsPins();
  setupMotorPins();
  Serial.setTimeout(100);
  Serial.begin(9600);
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
    case Motor_Forward:
      motorForward(buffer[1]);
      break;
    case Motor_Backward:
      motorBackward(buffer[1]);
      break;
    case Motor_Stopped:
      motorStop();
      break;
    default:
      break;
    }
  }
}

void sendState()
{
  Serial.write(liftFlags);
  Serial.write(cartFlags);
  Serial.write(motorState);
  Serial.write(motorSpeed);
}

void loop()
{
  unsigned long currTime = millis();

  updateSensorState();
  sendState();
  readCommand();

  unsigned long delta = 10UL + currTime - millis();
  delay(delta);
}
