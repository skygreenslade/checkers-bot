#include <Arduino.h>
#include <MeMegaPi.h>
#include <Wire.h>
#include "MeEEPROM.h"
#include <HardwareSerial.h>

#define SLOW_SPEED 40
#define DEBUG

#define TICKS_PER_FULL_ROTATION_2   2576/(2*PI)
#define TICKS_PER_FULL_ROTATION_1   3312/(2*PI)
#define TICKS_PER_FULL_ROTATION_3   5400/(2*PI)

#define BUTTON_PRESS_DURATION 70

#define ENCODER_BOARD 61
  //Read type
#define ENCODER_BOARD_POS    0x01
#define ENCODER_BOARD_SPEED  0x02

#define ENCODER_PID_MOTION     62
  //Secondary command
#define ENCODER_BOARD_POS_MOTION_MOVE    0x01
#define ENCODER_BOARD_SPEED_MOTION       0x02
#define ENCODER_BOARD_PWM_MOTION         0x03
#define ENCODER_BOARD_SET_CUR_POS_ZERO   0x04
#define ENCODER_BOARD_CAR_POS_MOTION     0x05
#define ENCODER_BOARD_POS_MOTION_MOVETO  0x06

// Pin configuration for SoftwareSerial (RX, TX)

// Circular buffer and index
const int BUFFER_SIZE = 22;     // Twice the needed size
byte buffer[BUFFER_SIZE];
int bufferIndex = 0;

// Joint angles (floating point)
float joint1, joint2;

// Packet markers
const byte PACKET_START = 0x7E; // '~'
const byte PACKET_END = 0x7F;   // ''

const byte interruptPin =18;
const byte NE1=31;

uint8_t motorSpeed = 100;

long count=0;

unsigned long time;
unsigned long last_time;

MeMegaPiDCMotor motor1(PORT1B);
MeMegaPiDCMotor motor2(PORT1A);

MeEncoderOnBoard Encoder_1(SLOT1);
MeEncoderOnBoard Encoder_2(SLOT2);
MeEncoderOnBoard Encoder_3(SLOT3);
MeMegaPiDCMotor Gripper(PORT4B);            // indeed

volatile long encoder_pos1 = 0;
volatile long encoder_pos2 = 0;
volatile long encoder_pos3 = 0;

bool notbeencalled = 1;
bool joint1_complete = true;
bool joint2_complete = true;

volatile int target_joint_ticks1 = 0;
volatile int target_joint_ticks2 = 0;
volatile int target_joint_ticks3 = 0;

struct motorInfo {
    MeMegaPiDCMotor *motor;
    MeEncoderOnBoard *encoder;
    volatile long *position;
};

enum arm_states{
  RAISED_RELEASED = 0,
  LOWERED_RELEASED,
  LOWERED_GRIPPING,
  RAISED_GRIPPING
};
arm_states arm = RAISED_RELEASED;

enum bot_states{
  MOVING = 0,
  RECEIVING_MESSAGE,
  PICKUP_ROUTINE,
  DROP_ROUTINE = 4
};
bot_states bot_state = RECEIVING_MESSAGE;


void isr_process_encoder1(void)
{
  //Serial.println("hit interupt");
  if(digitalRead(Encoder_1.getPortB()) == 0)
  {
    //Serial.println("hit interupt + 1");
    Encoder_1.pulsePosMinus();
    encoder_pos1--;
  }
  else
  {
    //Serial.println("hit interupt - 1");
    Encoder_1.pulsePosPlus();
    encoder_pos1++;
  }

}

void isr_process_encoder2(void)
{
  if(digitalRead(Encoder_2.getPortB()) == 0)
  {
    Encoder_2.pulsePosMinus();
    encoder_pos2--;
  }
  else
  {
    Encoder_2.pulsePosPlus();
    encoder_pos2++;
  }
}

void isr_process_encoder3(void)
{
  if(digitalRead(Encoder_3.getPortB()) == 0)
  {
    encoder_pos3--;
  }
  else
  {
    encoder_pos3++;
  }
}


// Takes the requested position as input and returns the bot's coordinates needed to accompilsh that. 
// theta 2 is the offset of theta1.
// l1 and l2 measured in cm
void getBotAngles( double x, double y, double l1, double l2, double *theta1, double *theta2){

    double temp1 = 0, temp2 = 0;

    double r = sqrt(pow(x, 2) + pow(y, 2));  // Get the hypotenuse
    temp1 = (l1*l1 + l2*l2 - r*r) / (2 * l1 * l2);

    *theta2 = PI - acos(temp1);  // Compute theta 2 (offset angle of theta 1)
    

    temp2 = (l2 * sin(*theta2)) / (l1 + l2 * cos(*theta2));

    *theta1 = atan2(y, x) - atan2(temp2, 1);  // Compute theta 1

}


float bytesToFloat(byte *data, int startIndex) {
  union {
    byte b[4];
    float f;
  } converter;

  for (int i = 0; i < 4; i++) {
    converter.b[i] = data[(startIndex + i) % BUFFER_SIZE];
  }

  return converter.f;
}

void printBuffer() {

  Serial.print("Buffer: ");
  for (int i = 0; i < BUFFER_SIZE; i++) {
    Serial.print(buffer[i], HEX);
    Serial.print(" ");
  }
  Serial.println();
}


void waitForButtonState(int state){
  int cnt = 0;
  bool waiting = true;
  while(waiting){
    //wait
    Serial.println("Waiting for press");
    //Button pressed
    if(digitalRead(PIN_A12) == state){
      cnt++;
    }
    else{
      cnt = 0;
    }

    if(cnt > BUTTON_PRESS_DURATION){
      waiting = false;
    }
  }
}


void waitForMessage(){

  bool waiting_for_message = true;

  while (waiting_for_message) {
    // Read the next byte from the serial port
    while(Serial.available() == 0){
      // Do nothing
      _NOP();        
    }
    byte data = Serial.read();

    // Add the byte to the circular buffer
    buffer[bufferIndex] = data;

    if(data == PACKET_END){
      printBuffer();
      #ifdef DEBUG
      Serial.print("Compare 1: ");
      Serial.println(buffer[(bufferIndex)], HEX);
      Serial.print("Compare 2: ");
      Serial.println(buffer[(bufferIndex - 10)], HEX);
      Serial.print("buffer index: ");
      Serial.println(bufferIndex);
      #endif DEBUG

    }
   
  
    // Check if a complete packet is in the buffer
    if (bufferIndex >= 10 && buffer[(bufferIndex)] == PACKET_END && buffer[(bufferIndex - 10)] == PACKET_START) {
      // Calculate checksum
      // Process message
      joint1 = bytesToFloat(buffer, (bufferIndex - 9) % BUFFER_SIZE);
      joint2 = bytesToFloat(buffer, (bufferIndex - 5) % BUFFER_SIZE);
      bot_state = static_cast<bot_states>(buffer[bufferIndex-1]);
        
      Serial.print("Joint1: ");
      Serial.println(joint1, 3);
      Serial.print("Joint2: ");
      Serial.println(joint2, 3);
      Serial.print("bot state: ");
      Serial.println(bot_state, 3);

      target_joint_ticks1 = - joint1*PI/180 * TICKS_PER_FULL_ROTATION_1;
      target_joint_ticks2 = joint2*PI/180 * TICKS_PER_FULL_ROTATION_2;

      joint1_complete = false;
      joint2_complete = false;

      waiting_for_message = false;        // End the loop
    }
   
    bufferIndex = (bufferIndex + 1) % BUFFER_SIZE;

  }

}

// Blocking function which moves the motors 
void moveto(long dist, uint16_t motorSpeed){

  long starting_dist = encoder_pos1;
  long ref_distance = encoder_pos1;
  while(ref_distance > dist + 100  || ref_distance < dist - 100){
    Serial.print("ref dist: ");
    Serial.println(ref_distance);

    if(ref_distance < dist){
      motor1.run(-abs(motorSpeed));
    }
    else{
      motor1.run(abs(motorSpeed));
    }
    ref_distance = encoder_pos1 - starting_dist;
  }

}

void motor1_loop(){
    if(encoder_pos1 < target_joint_ticks1 - 1){
      Encoder_1.setMotorPwm(25);
    }

    else if((encoder_pos1 > target_joint_ticks1 + 1)){
      Encoder_1.setMotorPwm(-25);
    }
    else{
      joint1_complete = true;
      Encoder_1.setMotorPwm(0);
    }

}


void motor2_loop(){
    if(encoder_pos2 < target_joint_ticks2- 1){
      Encoder_2.setMotorPwm(30);
    }

    else if((encoder_pos2 > target_joint_ticks2 + 1)){
      Encoder_2.setMotorPwm(-30);
    }

    else{
      joint2_complete = true;
      Encoder_2.setMotorPwm(0);
    }

}

void motor3_loop(){
    if(encoder_pos3 < target_joint_ticks3 - 1){
      Encoder_3.setMotorPwm(45);
    }

    else if((encoder_pos3 > target_joint_ticks3 + 1)){
      Encoder_3.setMotorPwm(-45);
    }
    else{
      Encoder_3.setMotorPwm(0);
    }

}


void updateDropRoutine(){

  switch (arm)
  {
    case RAISED_GRIPPING:
      // Code to move it to lowered state
      target_joint_ticks3 = -25*PI/180*TICKS_PER_FULL_ROTATION_3;
      Serial.print(encoder_pos3);
      Serial.print(" ");
      Serial.println(target_joint_ticks3);

      if(encoder_pos3 < target_joint_ticks3+5 && encoder_pos3 > target_joint_ticks3-5){
        arm = LOWERED_GRIPPING;   // Switch states
        Encoder_3.setMotorPwm(0);

        Serial.println("Lowered");
      }

      break;
    case LOWERED_GRIPPING:
      // Move to gripping state

      Serial.println("LOWERED_RELEASED");
      Gripper.run(-250);
      Encoder_3.setMotorPwm(0);
      delay(900);
      Gripper.run(0);

      arm = LOWERED_RELEASED;   // trigger this once gripped

      break;

    case LOWERED_RELEASED:
      target_joint_ticks3 = 0;
      Serial.print(encoder_pos3);
      Serial.print(" ");
      Serial.println(target_joint_ticks3);

      if(encoder_pos3 < target_joint_ticks3+5 && encoder_pos3 > target_joint_ticks3-5){
        arm = RAISED_RELEASED;   // Switch states
        Encoder_3.setMotorPwm(0);

        Serial.println("RAISED_GRIPPED");

      }
      // Move to raised gripping state
      break;

    case RAISED_RELEASED:
      Serial.println("RAISED_GRIPPING");
      // Done!
      Serial.println("Completed pickup routine");

      break;
  
      default:
        break;
  }

}


void updatePickupRoutine(){

  switch (arm)
  {
    case RAISED_RELEASED:
      // Code to move it to lowered state
      target_joint_ticks3 = -25*PI/180*TICKS_PER_FULL_ROTATION_3;
      Serial.print(encoder_pos3);
      Serial.print(" ");
      Serial.println(target_joint_ticks3);

      if(encoder_pos3 < target_joint_ticks3+5 && encoder_pos3 > target_joint_ticks3-5){
        arm = LOWERED_RELEASED;   // Switch states
        Encoder_3.setMotorPwm(0);

        Serial.println("Lowered");
      }

      break;
    case LOWERED_RELEASED:
      // Move to gripping state

      Serial.println("LOWERED_RELEASED");
      Gripper.run(250);
      Encoder_3.setMotorPwm(0);
      delay(900);
      Gripper.run(0);

      arm = LOWERED_GRIPPING;   // trigger this once gripped

      break;

    case LOWERED_GRIPPING:
      target_joint_ticks3 = 0;
      Serial.print(encoder_pos3);
      Serial.print(" ");
      Serial.println(target_joint_ticks3);

      if(encoder_pos3 < target_joint_ticks3+5 && encoder_pos3 > target_joint_ticks3-5){
        arm = RAISED_GRIPPING;   // Switch states
        Encoder_3.setMotorPwm(0);

        Serial.println("RAISED_GRIPPED");

      }
      // Move to raised gripping state
      break;

    case RAISED_GRIPPING:
      Serial.println("RAISED_GRIPPING");
      // Done!
      Serial.println("Completed pickup routine");

      break;
  
      default:
        break;
  }

}


void setup()
{
  attachInterrupt(Encoder_1.getIntNum(), isr_process_encoder1, RISING);
  attachInterrupt(Encoder_2.getIntNum(), isr_process_encoder2, RISING);
  attachInterrupt(Encoder_3.getIntNum(), isr_process_encoder3, RISING);

  pinMode(interruptPin, INPUT_PULLUP);
  pinMode(PIN_A15, OUTPUT);
  pinMode(PIN_A12, INPUT_PULLUP); // Set the button pin as an input
  pinMode(NE1, INPUT);

  digitalWrite(PIN_A15, HIGH);
  Serial.begin(115200);   

  waitForButtonState(1);

  Serial.print("First motor spinning");
  
  waitForButtonState(0);
  Encoder_1.setMotorPwm(25);
  waitForButtonState(1);
  Encoder_1.setMotorPwm(0);

  Serial.print("Second motor spinning");

  waitForButtonState(0);
  Encoder_2.setMotorPwm(25);
  waitForButtonState(1);
  Encoder_2.setMotorPwm(0);

  Serial.print("Third motor spinning");

  waitForButtonState(0);
  Encoder_3.setMotorPwm(-40);
  waitForButtonState(1);
  Encoder_3.setMotorPwm(0);
  encoder_pos3 = 0;
  target_joint_ticks3 = 25*PI/180*TICKS_PER_FULL_ROTATION_3;     // Set the 
  while(!(encoder_pos3 < target_joint_ticks3+5 && encoder_pos3 > target_joint_ticks3-5)){
    motor3_loop();
  }
  target_joint_ticks3 = 0;
  Serial.print("motors done");

  encoder_pos1 = (long)-0.0872665*TICKS_PER_FULL_ROTATION_1;       // Starting offset of roughly 5 degrees
  encoder_pos2 = (long) 3.66519142919*TICKS_PER_FULL_ROTATION_2;       // Starting offset of 6 deg
  encoder_pos3 = 0;
}


void loop()
{

    switch(bot_state){

      case MOVING:

        #ifdef DEBUG
        Serial.print("Encoder 1: ");
        Serial.print(encoder_pos1);
        Serial.print(", Target 1: ");
        Serial.print(target_joint_ticks1);
        Serial.print(", Encoder 2: ");
        Serial.print(encoder_pos2);
        Serial.print(", Target 2: ");
        Serial.println(target_joint_ticks2);
        #endif



        if(joint1_complete && joint2_complete){
          bot_state = RECEIVING_MESSAGE;
          joint1_complete = false;              // reset flags
          joint2_complete = false;
        }
      break;

      case RECEIVING_MESSAGE:
        Serial.println("Waiting for message");
        Encoder_1.setMotorPwm(0);             // Stop the motors (double check theyre stopped)
        Encoder_2.setMotorPwm(0);
        Encoder_3.setMotorPwm(0);

        waitForMessage();                     // block until message received
        Serial.println("recv");
      break;

      case PICKUP_ROUTINE:
        updatePickupRoutine();    // Update pickup routine state

        if(arm == RAISED_GRIPPING){
          bot_state = RECEIVING_MESSAGE;
        }
      break;

      case DROP_ROUTINE:
        updateDropRoutine();    // Update pickup routine state
        
        if(arm == RAISED_RELEASED){
          bot_state = RECEIVING_MESSAGE;
        }
      break;


    }

    motor1_loop();
    motor2_loop();
    motor3_loop();            // Update motor to execute picktup routine state


}

