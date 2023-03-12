#include <Arduino.h>
#include <MeMegaPi.h>
#include <Wire.h>
#include "MeEEPROM.h"
#include <HardwareSerial.h>

#define SLOW_SPEED 40

#define TICKS_PER_FULL_ROTATION_1   2576
#define TICKS_PER_FULL_ROTATION_2   3312

#define ARM_1_LENGTH 35.5
#define ARM_2_LENGTH 25


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
// 
void getBotAngles( double x, double y, double *theta1, double *theta2){

  double l1 = ARM_1_LENGTH;
  double l2 = ARM_2_LENGTH;

  double r = sqrt(pow(x,2) + pow(y,2));   // Get the hypotenus. 
  *theta2 = acos( ( pow(r, 2) - pow(l1, 2) - pow(l2, 2) ) / 2*l1*l2 );            // compute theta 2 (offset angle of theta 1)
  *theta1 = atan(y/x) - atan( (l2 * sin(*theta2)) / (l1 + l2*cos(*theta2) ));     // compute theta 1
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




void setup()
{
  attachInterrupt(Encoder_1.getIntNum(), isr_process_encoder1, RISING);
  attachInterrupt(Encoder_2.getIntNum(), isr_process_encoder2, RISING);
  pinMode(interruptPin, INPUT_PULLUP);
  pinMode(NE1, INPUT);
  Serial.begin(9600);   

  double theta1, theta2;

  // getBotAngles(15, -15, &theta1, &theta2);

  // int ticks1 = (int) theta1 * TICKS_PER_FULL_ROTATION_1;
  // int ticks2 = (int) theta2 * TICKS_PER_FULL_ROTATION_2;

  // Serial.println(ticks1);
  // Serial.println(ticks2);


  // Encoder_1.move(ticks1, 200, 0, (cb) changeDir);
  // Encoder_2.move(ticks2, 200, 1, (cb) changeDir2);
}





void loop()
{

    long pos1 = encoder_pos1;
    char mystr[40];

    Serial.print("Current:");
    Serial.println(pos1);

    char* input;  //buffer for user input
    int input1;  //holds input data for which motor to move
    int input2;  //holds input data for how far to move
    bool inputValid = false; //boolean for whether input is valid or not

    int motorToMove;  //which motor number to move
    int degToMove;    //degrees to move
    long radToMove;   //degrees to move converted to radians

    //get user input for motor to move, and how much
    while (!inputValid){
      //wait for user input
      while(Serial.available() == 0);

      //read in input, assume format: <motorNum>,<rotationInDegrees>
      strcpy(input, (Serial.readStringUntil(',')).c_str());
      input1 = strtol(input, '\0', 0);
      strcpy(input, (Serial.readString()).c_str());
      input2 = strtol(input, '\0', 0);

      //ensure motor selection is 1, 2, or 3
      switch(input1){
        case(1):
          motorToMove = 1;
          inputValid = true;
          break;
        case(2):
          motorToMove = 2;
          inputValid = true;
          break;
        case(3):
          motorToMove = 3;
          inputValid = true;
        default:
          Serial.println("Please give motor number as 1, 2, or 3, followed by a comma.");
          inputValid = false;
      }

      //ensure that angle to move is within desired range
      if(-180<=input2 && input2<=180){
        degToMove = input2;
        inputValid = true; 
      }
      else{
        Serial.println("Please give motor movement as degree between +/- 180.");
        inputValid = false;
      }

      if(!inputValid){
        Serial.println("Example: 2,-90");
      }

    
    }//waiting for valid input

    //output what input was
    Serial.print("moving motor ");
    Serial.print(char(motorToMove));
    Serial.print(", ");
    Serial.print(char(degToMove));
    Serial.println(" degrees.");

    //approximate radians to move
    radToMove = (degToMove*71)/4068






    // while(1){

    //   Encoder_1.loop();
    //   Encoder_2.loop();

      //Encoder_2.setMotorPwm(-100);

    // }
      
}

