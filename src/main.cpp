#include <Arduino.h>
#include <MeMegaPi.h>
#include <Wire.h>
#include "MeEEPROM.h"
#include <HardwareSerial.h>

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

const byte interruptPin =18;
const byte NE1=31;

uint8_t motorSpeed = 100;

long count=0;

unsigned long time;
unsigned long last_time;

MeMegaPiDCMotor motor1(PORT1B);

MeEncoderOnBoard Encoder_1(SLOT1);
MeEncoderOnBoard Encoder_2(SLOT2);


volatile long encoder_pos1 = 0;

void isr_process_encoder1(void)
{
  //Serial.println("hit interupt");
  if(digitalRead(Encoder_1.getPortB()) == 0)
  {
    //Serial.println("hit interupt + 1");
    encoder_pos1 -= 1;
  }
  else
  {
    //Serial.println("hit interupt - 1");
    encoder_pos1 += 1;
  }
}

void isr_process_encoder2(void)
{
  if(digitalRead(Encoder_2.getPortB()) == 0)
  {
    Encoder_2.pulsePosMinus();
  }
  else
  {
    Encoder_2.pulsePosPlus();
  }
}

// Takes the requested position as input and returns the bot's coordinates needed to accompilsh that. 
// theta 2 is the offset of theta1.
// 
void getBotAngles( double x, double y, double l1, double l2, double *theta1, double *theta2){

  double r = sqrt(pow(x,2) + pow(y,2));   // Get the hypotenus. 
  *theta2 = acos( ( pow(r, 2) - pow(l1, 2) - pow(l2, 2) ) / 2*l1*l2 );            // compute theta 2 (offset angle of theta 1)
  *theta1 = atan(y/x) - atan( (l2 * sin(*theta2)) / (l1 + l2*cos(*theta2) ));     // compute theta 1
}

void setup()
{
  attachInterrupt(Encoder_1.getIntNum(), isr_process_encoder1, RISING);
  attachInterrupt(Encoder_2.getIntNum(), isr_process_encoder2, RISING);
  pinMode(interruptPin, INPUT_PULLUP);
  pinMode(NE1, INPUT);
  Serial.begin(9600);   
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

void loop()
{

    long pos1 = encoder_pos1;
    char mystr[40];

    Serial.print("Current:");
    Serial.println(pos1);
    while(1){
      
      moveto(200, 50);


      delay(2000);


      moveto(-400, 50);

      delay(2000);

    }
    
    motor1.stop();
  
}

