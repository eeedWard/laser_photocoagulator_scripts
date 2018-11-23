// Laser parameters
const int outputPin = DAC0;
const int pulseLength = 1000; // Pulse length in us
const int pulseLongLength = 60000; // Pulse length in ms for proximal pose calibration
const int OValue = 3600; // Output value for laser pin (max is 3600)

// Linear Advancer (LA) parameters
#include <Wire.h>
#include <Adafruit_MotorShield.h>
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
Adafruit_StepperMotor *myMotor = AFMS.getStepper(200, 2); // Motor, wired on channel two, has 200 steps per revolution

float distance; // Distance to travel in mm
float steps; // Steps to be carried out
int RPM = 1000; // Motor speed (does not correspond to RPM, max with microstepping: 10sec/mm)

void setup() {
  // Laser
  pinMode(outputPin, OUTPUT);
  analogWriteResolution(12);

  // LA
  AFMS.begin();  // create with the default frequency 1.6KHz
  myMotor->setSpeed(RPM);

  // Serial communication
  Serial.begin(9600);
  while (!Serial);
  Serial.setTimeout(10); // Wait 10ms to parse a float, used for distance input
  Serial.println("Laser modulation and Linear Advancer Control");
  Serial.println("--- '0' fire the laser --- '1' + distance in mm to move LA --- '2' release stepper motor --- '3' laser continuous mode ---");
}

void loop() {
 // if (Serial.available()) {
    int state = Serial.read(); // Reads first byte coming to switch between laser and LA
    
    // Laser single pulse is activated when first number entered is '0' (48 in ASCII)
    if (state == 48) { 
        //Serial.println("Single pulse");
        analogWrite(outputPin, OValue);
        delayMicroseconds(pulseLength); 
        analogWrite(outputPin, 0);
    }
      // Laser continuous mode activate when entering "3"
      if (state == 51) { 
        Serial.println("Laser continuous mode, will turn off in 1 min");
        analogWrite(outputPin, OValue);
        delay(pulseLongLength); 
        analogWrite(outputPin, 0);
        Serial.println("Laser off");
    }
    // LA control is activated when first number entered is '1' (49 in ASCII)
    if (state == 49){
      distance = Serial.parseFloat();
      //Serial.print("Distance (mm): ");
      //Serial.println(distance);

      // Move forwards if distance is positive
      if (distance >= 0 && distance <= 10) {
        steps = distance / 1 * 200;
        myMotor->step(steps, FORWARD, MICROSTEP);
        Serial.println(1);
      }

      // Move backwards if distance is negative
      else if (distance < 0 && distance >= - 10) {
        steps = - distance / 1 * 200;
        myMotor->step(steps, BACKWARD, MICROSTEP); 
        Serial.println(1);
      }
      else {
        Serial.println("Motion out of range (5 mm)");
        distance = 0;
      }
    }

    // LA motor is released if '2' is sent
    if (state == 50){
      myMotor->release();
      Serial.println("Stepper motor released");
    }
    
   // If other values are entered displays error
   // if (state != 48 && state!= 49 && state != 50 && state != 51) {
     //  Serial.println("Send '0' to fire the laser, '1' followed by distance in mm to move LA, '2' to release the motor");        
    //}
  }
//}
