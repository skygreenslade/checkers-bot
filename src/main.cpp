#include <Arduino.h>
#include <MeMegaPi.h>
#include <Wire.h>
#include "MeEEPROM.h"
#include <HardwareSerial.h>

#define SLOW_SPEED 40

#define TICKS_PER_FULL_ROTATION_1   2576/(2*PI)
#define TICKS_PER_FULL_ROTATION_2   3312/(2*PI)


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
MeMegaPiDCMotor motor2(PORT1A);

MeEncoderOnBoard Encoder_1(SLOT1);
MeEncoderOnBoard Encoder_2(SLOT2);


volatile long encoder_pos1 = 0;
volatile long encoder_pos2 = 0;

struct motorInfo {
    MeMegaPiDCMotor *motor;
    MeEncoderOnBoard *encoder;
    volatile long *position;
};


// void movePos(motorInfo toMove, long target, uint16_t speed);
// void movePosSlow(motorInfo toMove, long target);
// void moveNeg(motorInfo toMove, long target, uint16_t speed);
// void moveNegSlow(motorInfo toMove, long target);


// //main move function
// void moveTo(int motorNum, long target, uint16_t speed){

//     struct motorInfo toMove;

//     //get motor info for given motor number
//     switch(motorNum){
//         case 1:
//             toMove.motor = &motor1;
//             toMove.encoder = &Encoder_1;      // Give me a pointer!!!
//             toMove.position = &encoder_pos1;
//             break;
//         case 2:
//             toMove.motor = &motor2;
//             toMove.encoder = &Encoder_2;
//             toMove.position = &encoder_pos2;
//             break;
//         // case 3:
//         //     toMove.motor = motor3;
//         //     toMove.encoder = Encoder_3;
//         //     toMove.position = encoder_pos3;
//         //     break;
//         default:
//         //uh oh
//     }

//     //positive case
//     if (target > toMove.position)
//         movePos(toMove, target, speed);
//     //negative case
//     else
//         moveNeg(toMove, target, speed);

// }//moveTo



// void movePos(motorInfo toMove, long target, uint16_t speed){

//     //move until at or past target position - 50 units
//     while(target - 50 >= *toMove.position){
//         (*toMove.motor).run(abs(speed));
//     }

//     //slow down for final bit
//     movePosSlow(toMove, target);


// }//movePos


// void movePosSlow(motorInfo toMove, long target){

//     int speed = SLOW_SPEED;

//     //move until at or past target position
//     while(target >= *toMove.position){
//         (*toMove.motor).run(abs(speed));
//     }

// }//movePosSlow


// void moveNeg(motorInfo toMove, long target, uint16_t speed){

//     //move until at or past target position - 50 units
//     while(target + 50 <= *toMove.position){
//         (*toMove.motor).run(-abs(speed));
//     }

//     //slow down for final bit
//     movePosSlow(toMove, target);


// }//moveNeg


// void moveNegSlow(motorInfo toMove, long target){

//     int speed = SLOW_SPEED;

//     //move until at or past target position
//     while(target <= *toMove.position){
//         (*toMove.motor).run(-abs(speed));
//     }

// }//moveNegSlow



void isr_process_encoder1(void)
{
  //Serial.println("hit interupt");
  if(digitalRead(Encoder_1.getPortB()) == 0)
  {
    //Serial.println("hit interupt + 1");
    Encoder_1.pulsePosMinus();
  }
  else
  {
    //Serial.println("hit interupt - 1");
    Encoder_1.pulsePosPlus();
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

bool notbeencalled = 1;

void changeDir(){

  //Encoder_1.move(414, 200, 0, (cb) changeDir);
}

void changeDir2(){
  //Encoder_2.move(-322, 200, 1, (cb) changeDir2);
}

// Takes the requested position as input and returns the bot's coordinates needed to accompilsh that. 
// theta 2 is the offset of theta1.
// l1 and l2 measured in cm
void getBotAngles( double x, double y, double l1, double l2, double *theta1, double *theta2){

    double temp1 = 0, temp2 = 0;

    double r = sqrt(pow(x, 2) + pow(y, 2));  // Get the hypotenuse
    Serial.println(r);
    temp1 = (l1*l1 + l2*l2 - r*r) / (2 * l1 * l2);
    Serial.print("Temp1");
    Serial.println(temp1);

    *theta2 = PI - acos(temp1);  // Compute theta 2 (offset angle of theta 1)
    
    Serial.println(*theta2);

    temp2 = (l2 * sin(*theta2)) / (l1 + l2 * cos(*theta2));
    Serial.print("Temp2");
    Serial.println(temp2);  // Convert to degrees and print
    
    *theta1 = atan2(y, x) - atan2(temp2, 1);  // Compute theta 1
    
    Serial.println(*theta1);  // Convert to degrees and print


}

void waitForButton(){
  int cnt = 0;
  bool waiting = true;
  while(waiting){
    //wait
    Serial.println("Waiting for press");
    //Button pressed
    if(!digitalRead(PIN_A12)){
      cnt++;
    }
    else{
      cnt = 0;
    }

    if(cnt > 100){
      waiting = false;
    }
  }
}


double theta1, theta2;

void setup()
{
  attachInterrupt(Encoder_1.getIntNum(), isr_process_encoder1, RISING);
  attachInterrupt(Encoder_2.getIntNum(), isr_process_encoder2, RISING);
  pinMode(interruptPin, INPUT_PULLUP);
  pinMode(PIN_A15, OUTPUT);
  pinMode(PIN_A12, INPUT_PULLUP); // Set the button pin as an input
  pinMode(NE1, INPUT);

  digitalWrite(PIN_A15, HIGH);
  Serial.begin(115200);   

  waitForButton();
  

  getBotAngles(10, -10, 35.5, 25, &theta1, &theta2);

  int ticks1 =  theta1 * TICKS_PER_FULL_ROTATION_1;
  int ticks2 =  theta2 * TICKS_PER_FULL_ROTATION_2;

  Encoder_1.setMotorPwm(25);
  waitForButton();

  Encoder_2.setMotorPwm(25);
  waitForButton();


  Serial.print("Ticks1: ");
  Serial.println((int) ticks1);
  Serial.print("Ticks2: ");
  Serial.println((int) ticks2);

  Encoder_2.setPulsePos((long)0);                             // Set the positions of the robot arm
  Encoder_2.setPulsePos((long)0);

  Encoder_1.moveTo(ticks1, 100, 0, (cb) changeDir);
  Encoder_2.moveTo(ticks2, 100, 1, (cb) changeDir2);

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

    //Serial.print("Current:");
    //Serial.println(pos1);

    Encoder_1.loop();
    Encoder_2.loop();

      //Encoder_2.setMotorPwm(-100);

      
}

