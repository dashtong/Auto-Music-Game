#include <Servo.h>
#define LINE 5

#define MID          0
#define DOWN         1
#define USED_TIME  150

#define DOWN_DIFF  -10
#define LEFT_DIFF   23
#define RIGHT_DIFF -15

Servo myservo[LINE][2];

uint32_t timer[LINE], startTime;
uint8_t servo_pos[LINE][2] = {{90, 90}};
uint8_t state[LINE] = {0};
const uint8_t servo_init_pos[LINE][2] = {{40, 10}, {40, 16}, {40, 16}, {40, 24}, {40, 22}}; // {{40, 13}, {40, 13}, {40, 19}, {40, 14}, {40, 19}};

void init_pos(uint8_t servo_line) {
  if (servo_line >= 0 && servo_line < LINE) {
    servo_pos[servo_line][MID] = servo_init_pos[servo_line][MID];
    servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN];
  }
}

void tap(uint8_t servo_line) {
  if (servo_line >= 0 && servo_line < LINE) {
    if (millis() - timer[servo_line] < USED_TIME)
      servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN] + DOWN_DIFF;
    else init_pos(servo_line);
  }
}

void hold(uint8_t servo_line) {
  if (servo_line >= 0 && servo_line < LINE) {
    servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN] + DOWN_DIFF;
  }
}

void left(uint8_t servo_line) {
  if (servo_line >= 0 && servo_line < LINE) {
    if (millis() - timer[servo_line] < USED_TIME / 2) {
      servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN] + DOWN_DIFF;
    }
    else if (millis() - timer[servo_line] < USED_TIME) {
      servo_pos[servo_line][MID] = servo_init_pos[servo_line][MID] + LEFT_DIFF;
      if (servo_line == 3 || servo_line == 2) servo_pos[servo_line][MID] = servo_init_pos[servo_line][MID] + LEFT_DIFF + 10;
      servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN] + DOWN_DIFF;
    }
    else if (millis() - timer[servo_line] < USED_TIME * 1.2) {
      servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN];
    }
    else init_pos(servo_line);
  }
}

void right(uint8_t servo_line) {
  if (servo_line >= 0 && servo_line < LINE) {
    if (millis() - timer[servo_line] < USED_TIME / 2) {
      servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN] + DOWN_DIFF;
    }
    else if (millis() - timer[servo_line] < USED_TIME) {
      servo_pos[servo_line][MID] = servo_init_pos[servo_line][MID] + RIGHT_DIFF;
      if (servo_line == 0 || servo_line == 4 || servo_line == 2) servo_pos[servo_line][MID] = servo_init_pos[servo_line][MID] + RIGHT_DIFF - 10;
      servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN] + DOWN_DIFF;
    }
    else if (millis() - timer[servo_line] < USED_TIME * 1.2) {
      servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN];
    }
    else init_pos(servo_line);
  }
}

void leftRight(uint8_t servo_line) {
  if (servo_line >= 0 && servo_line < LINE) {
    if (millis() - timer[servo_line] < USED_TIME / 2) {
      servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN] + DOWN_DIFF;
    }
    else if (millis() - timer[servo_line] < USED_TIME) {
      servo_pos[servo_line][MID] = servo_init_pos[servo_line][MID] + LEFT_DIFF;
      if (servo_line == 3 || servo_line == 1) servo_pos[servo_line][MID] = servo_init_pos[servo_line][MID] + LEFT_DIFF + 10;
      servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN] + DOWN_DIFF;
    }
    else if (millis() - timer[servo_line] < USED_TIME * 1.5) {
      servo_pos[servo_line][MID] = servo_init_pos[servo_line][MID] + RIGHT_DIFF;
      servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN] + DOWN_DIFF;
    }
    else init_pos(servo_line);
  }
}

void rightLeft(uint8_t servo_line) {
  if (servo_line >= 0 && servo_line < LINE) {
    if (millis() - timer[servo_line] < USED_TIME / 2) {
      servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN] + DOWN_DIFF;
    }
    else if (millis() - timer[servo_line] < USED_TIME) {
      servo_pos[servo_line][MID] = servo_init_pos[servo_line][MID] + RIGHT_DIFF;
      if (servo_line == 1) servo_pos[servo_line][MID] = servo_init_pos[servo_line][MID] + RIGHT_DIFF - 10;
      servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN] + DOWN_DIFF;
    }
    else if (millis() - timer[servo_line] < USED_TIME * 1.5) {
      servo_pos[servo_line][MID] = servo_init_pos[servo_line][MID] + LEFT_DIFF;
      //      if (servo_line == 3) servo_pos[servo_line][MID] = servo_init_pos[servo_line][MID] + LEFT_DIFF + 10;
      servo_pos[servo_line][DOWN] = servo_init_pos[servo_line][DOWN] + DOWN_DIFF;
    }
    else init_pos(servo_line);
  }
}

void testAll() {
  for (int i = LINE - 1; i >= 0; i--) {
    timer[i] = millis();
    while (millis() - timer[i] <= 500) {
      tap(i);
      executeAct();
    }
    timer[i] = millis();
    while (millis() - timer[i] <= 500) {
      left(i);
      executeAct();
    }
    timer[i] = millis();
    while (millis() - timer[i] <= 700) {
      right(i);
      executeAct();
    }
    //    timer[i] = millis();
    //    while (millis() - timer[i] <= 700) {
    //      hold(i);
    //      executeAct();
    //    }
    //    timer[i] = millis();
    //    while (millis() - timer[i] <= 500) {
    //      tap(i);
    //      executeAct();
    //    }
  }
}

void getAct() {
  for (int i = 0; i < LINE; i++) {
    if ((i + 1) % 2 == 0) {
      switch (state[i]) {
        case 1: case 6: case 0: tap(i); break;
        case 2: case 4: case 7: case 9: left(i); break;
        case 3: case 8: right(i); break;
        case 5: hold(i); break;
        case 10: leftRight(i); break;
        case 11: rightLeft(i); break;
      }
    }
    else {
      switch (state[i]) {
        case 1: case 6: case 0: tap(i); break;
        case 2: case 4: case 7: case 9: right(i); break;
        case 3: case 8: left(i); break;
        case 5: hold(i); break;
        case 10: rightLeft(i); break;
        case 11: leftRight(i); break;
      }
    }
  }
}

void executeAct() {
  for (int j = 0; j < LINE; j++) {
    for (int i = 0; i < 2; i++) {
      myservo[j][i].write(servo_pos[j][i]);
    }
  }
}

void setup() {
  Serial.begin(115200);
  for (uint8_t j = 0; j < LINE; j++) {
    init_pos(j);
    for (uint8_t i = 0; i < 2; i++) {
      myservo[j][i].attach(j * 2 + i + 2);
      myservo[j][i].write(servo_init_pos[j][i]);
    }
  }
  for (uint8_t j = 0; j < LINE; j++) {
    timer[j] = millis();
  }
}

void loop() {
  if (Serial.available() > 0 ) {
    // Position
    uint8_t pos = 0;
    String tmp = Serial.readStringUntil(10);
    if (tmp[0] == '1' || tmp[0] == '2' || tmp[0] == '3' || tmp[0] == '4' || tmp[0] == '5') {
      pos = tmp[0] - 49;
    }
    else if (tmp[0] == 't') {
      testAll();
    }
    // Action
    if (tmp[1] == '1' || tmp[1] == '2' || tmp[1] == '3' || tmp[1] == '4' || tmp[1] == '5' || tmp[1] == '6' || tmp[1] == '7' || tmp[1] == '8' || tmp[1] == '9' || tmp[1] == ':' || tmp[1] == ';') {
      state[pos] = tmp[1] - 48;
      timer[pos] = millis();
    }
    if (tmp.length() > 2) {
      if (tmp[2] == '1' || tmp[2] == '2' || tmp[2] == '3' || tmp[2] == '4' || tmp[2] == '5') {
        pos = tmp[2] - 49;
      }
      // Action
      if (tmp[3] == '1' || tmp[3] == '2' || tmp[3] == '3' || tmp[3] == '4' || tmp[3] == '5' || tmp[3] == '6' || tmp[3] == '7' || tmp[3] == '8' || tmp[3] == '9' || tmp[3] == ':' || tmp[3] == ';') {
        state[pos] = tmp[3] - 48;
        timer[pos] = millis();
      }
    }
  }

  getAct();
  executeAct();
}
