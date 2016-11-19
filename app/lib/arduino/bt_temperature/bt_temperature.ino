
int val = 0;
char tempSensor[] = "wallace_temp_1";
char resistSensor[] = "resistSens";
String message;

#define TEMP_PIN 0
#define TEMP_SENSOR_NAME "cupboard_T_001"

void setup() {
  Serial.begin(9600); // Fix the baudrate
  pinMode(13, OUTPUT); // Will be used for basic signalling.
}

void loop() {
  // Listen first.
  // Capability is not currently used.
  while(Serial.available())
  {
    message+=char(Serial.read()); // Store the output.
  }
  message=""; // Not used; clear it out.

  // Take a temperature reading and send it back.
  int temperature = get_temperature();
  String output = prepare_reading(TEMP_SENSOR_NAME, temperature);
  Serial.println(output);
  delay(1000); 
}

int get_temperature() {
  int val;
  int dat;
  val = analogRead(TEMP_PIN);
  dat = (125 * val) >> 8;
  return dat;
}

String prepare_reading(String tag, int value) {
  String output = tag + "," + value + ",";
  return output;
}


