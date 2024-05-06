/*

*/

const int PWM1Pin = 5;
const int PWM2Pin = 6;

const uint8_t cartDownDSP = 2;
const uint8_t cartOnLiftDSP = 12;
const uint8_t cartTopDSP = 9;
const uint8_t cartStationASP = A4;

const uint8_t liftUpDSP = 11;
const uint8_t liftMiddle1DSP = 10;
const uint8_t liftMiddle2ASP = A0;
const uint8_t liftMiddle3ASP = A1;
const uint8_t liftMiddle4ASP = A2;
const uint8_t liftMiddle5ASP = A3;
const uint8_t liftDownDSP = 3;

int cartDownValue = 0;
int cartOnLiftValue = 0;
int cartTopValue = 0;
int cartStationValue = 0;

int liftUpValue = 0;
int liftMiddle1Value = 0;
int liftMiddle2Value = 0;
int liftMiddle3Value = 0;
int liftMiddle4Value = 0;
int liftMiddle5Value = 0;
int liftDownValue = 0;

uint8_t cartFlags = 0;
uint8_t liftFlags = 0;

void setup() {
  pinMode(PWM1Pin, OUTPUT);
  pinMode(PWM2Pin, OUTPUT);
  analogWrite(PWM1Pin, 0);
  analogWrite(PWM2Pin, 0);

  pinMode(cartDownDSP, INPUT);
  pinMode(cartOnLiftDSP, INPUT);
  pinMode(cartTopDSP, INPUT);
  pinMode(liftUpDSP, INPUT);
  pinMode(liftMiddle1DSP, INPUT);
  pinMode(liftDownDSP, INPUT);

  pinMode(cartStationASP, INPUT_PULLUP);
  pinMode(liftMiddle2ASP, INPUT_PULLUP);
  pinMode(liftMiddle3ASP, INPUT_PULLUP);
  pinMode(liftMiddle4ASP, INPUT_PULLUP);
  pinMode(liftMiddle5ASP, INPUT_PULLUP);

  Serial.begin(57600);
}

void printState() {
  // Serial.print(cartDownValue);
  // Serial.print(',');
  // Serial.print(cartOnLiftValue);
  // Serial.print(',');
  // Serial.print(cartTopValue);
  // Serial.print(',');
  // Serial.print(cartStationValue);
  // Serial.print(',');
  // Serial.print(liftDownValue);
  // Serial.print(',');
  // Serial.print(liftMiddle1Value);
  // Serial.print(',');
  // Serial.print(liftMiddle2Value);
  // Serial.print(',');
  // Serial.print(liftMiddle3Value);
  // Serial.print(',');
  // Serial.print(liftMiddle4Value);
  // Serial.print(',');
  // Serial.print(liftMiddle5Value);
  // Serial.print(',');
  // Serial.print(liftUpValue);
  // Serial.print(',');
  Serial.print(cartFlags, BIN);
  Serial.print(',');
  Serial.print(liftFlags, BIN);
  Serial.println();
}

int digitalReadTreshlod(uint8_t pin, int treshold) {
  return analogRead(pin) < treshold ? 1 : 0;
}

void readState() {
  cartDownValue = !digitalRead(cartDownDSP);
  cartOnLiftValue = !digitalRead(cartOnLiftDSP);
  cartTopValue = !digitalRead(cartTopDSP);
  cartStationValue = digitalReadTreshlod(cartStationASP, 850);

  cartFlags = cartDownValue
              | cartOnLiftValue << 1
              | cartTopValue << 2
              | cartStationValue << 3
              | 1 << 7;

  liftUpValue = !digitalRead(liftUpDSP);
  liftMiddle1Value = !digitalRead(liftMiddle1DSP);
  liftMiddle2Value = digitalReadTreshlod(liftMiddle2ASP, 850);
  liftMiddle3Value = digitalReadTreshlod(liftMiddle3ASP, 850);
  liftMiddle4Value = digitalReadTreshlod(liftMiddle4ASP, 850);
  liftMiddle5Value = digitalReadTreshlod(liftMiddle5ASP, 850);
  liftDownValue = digitalRead(liftDownDSP);

  liftFlags = liftUpValue
              | liftMiddle1Value << 1
              | liftMiddle2Value << 2
              | liftMiddle3Value << 3
              | liftMiddle4Value << 4
              | liftMiddle5Value << 5
              | liftDownValue << 6
              | 1 << 7;
}

uint8_t lastLiftState = 0;
uint8_t lastCartState = 0;
char serialRead = 0;
void loop() {
  readState();
  if (lastLiftState != liftFlags || lastCartState != cartFlags) {
    printState();
    lastLiftState = liftFlags;
    lastCartState = cartFlags;
  }
  if (Serial.peek() > -1) {
    serialRead = Serial.read();
    Serial.println(serialRead);

    if (serialRead == 'S') {
      analogWrite(PWM2Pin, 128);
    }

    if (serialRead == 'T') {
      analogWrite(PWM2Pin, 0);
    }
  }
  delay(10);
}
