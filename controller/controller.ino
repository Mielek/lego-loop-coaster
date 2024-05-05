void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(57600);
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
  Serial.println('1');
  if (Serial.peek() > -1) {
    Serial.println((char) Serial.read());
  }
}
