
#define SLOW_SPEED 40


#include <stdint.h> //uint

struct motorInfo {
    MeMegaPiDCMotor motor;
    MeEncoderOnBoard encoder;
    long position;
};



//main move function
void moveTo(int motorNum, long target, uint16_t speed){

    struct motorInfo toMove;

    //get motor info for given motor number
    switch(motorNum){
        case 1:
            toMove.motor = motor1;
            toMove.encoder = Encoder_1;
            toMove.position = encoder_pos1;
            break;
        case 2:
            toMove.motor = motor2;
            toMove.encoder = Encoder_2;
            toMove.position = encoder_pos2;
            break;
        case 3:
            toMove.motor = motor3;
            toMove.encoder = Encoder_3;
            toMove.position = encoder_pos3;
            break;
        default:
        //uh oh
    }

    //positive case
    if (target > toMove.position)
        movePos(toMove, target, speed);
    //negative case
    else
        moveNeg(toMove, target, speed);

}//moveTo



void movePos(motorInfo toMove, long target, uint16_t speed){

    //move until at or past target position - 50 units
    while(target - 50 >= toMove.position){
        toMove.motor.run(abs(speed));
    }

    //slow down for final bit
    movePosSlow(toMove, target);


}//movePos


void movePosSlow(motorInfo toMove, long target){

    int speed = SLOW_SPEED;

    //move until at or past target position
    while(target >= toMove.position){
        toMove.motor.run(abs(speed));
    }

}//movePosSlow










void moveNeg(motorInfo toMove, long target, uint16_t speed){

    //move until at or past target position - 50 units
    while(target + 50 <= toMove.position){
        toMove.motor.run(-abs(speed));
    }

    //slow down for final bit
    movePosSlow(toMove, target);


}//moveNeg


void moveNegSlow(motorInfo toMove, long target){

    int speed = SLOW_SPEED;

    //move until at or past target position
    while(target <= toMove.position){
        toMove.motor.run(-abs(speed));
    }

}//moveNegSlow

