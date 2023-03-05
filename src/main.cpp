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

void setup()
{
  attachInterrupt(Encoder_1.getIntNum(), isr_process_encoder1, RISING);
  attachInterrupt(Encoder_2.getIntNum(), isr_process_encoder2, RISING);
  pinMode(interruptPin, INPUT_PULLUP);
  pinMode(NE1, INPUT);
  Serial.begin(9600);   
}



void moveTo(long distToMove, uint16_t speed){

    long startPos = encoder_pos1;
    long distMoved = 0;

    //positive case
    if (distToMove > 0){
        while(distMoved < distToMove){
          motor1.run(-abs(speed));
          distMoved = encoder_pos1 - startPos;
        }
    }
    //negative case
    else {
        while(distMoved > distToMove){
          motor1.run(abs(speed));
          distMoved = encoder_pos1 - startPos;
        }
    }


}//moveTo






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
      delay(1000);
      moveto(-200, 50);
      delay(1000);

    }
    
    motor1.stop();
  
}

