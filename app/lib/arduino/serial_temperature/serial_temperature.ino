#include <Time.h>

int analogPins[] = {0, 1};
int val = 0;
char tempSensor[] = "wallace_temp_1";
char resistSensor[] = "resistSens";

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  int val;
  int dat;
  val = analogRead(analogPins[0]);
  dat = (125 * val) >> 8;
  Serial.print(tempSensor);
  Serial.print(",");
  Serial.print(dat);
  Serial.print("\n");
  val = analogRead(analogPins[1]);
  Serial.print(resistSensor);
  Serial.print(",");
  Serial.print(val);
  Serial.print(",");
  Serial.print("\n");
  delay(500);
}
