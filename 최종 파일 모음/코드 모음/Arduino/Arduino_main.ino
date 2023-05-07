// jetson -> arduino : 1 2 3 4 수신받은 메세지
// arduino -> jetson : A B C D 송신하는 메세지

#include <Servo.h> // 서보모터
#include <SoftwareSerial.h> // 시리얼 통신

// 핀 설정
Servo fishDivider_ServoA; // A ~ C분류 서보모터
Servo fishDivider_ServoB;
Servo fishDivider_ServoC;

const int LED_A = 4; // A ~ D 통로별 LED (A ~ C : Green / D : Red)
const int LED_B = 5;
const int LED_C = 6;
const int LED_D = 7; // Red

const int fishDivider_numA = 8; // A ~ C 분류 모터
const int fishDivider_numB = 9;
const int fishDivider_numC = 10;

const int resetSW_PIN = 13; // 서보모터 reset 버튼

// 논리 변수
int photoThreshold = 100; // 광센서 threshold
bool detectValue = 0; // 최초로 컨베이어 벨트의 물고기 감지
bool objectDetect = 1;
const int detectPhotoSensor = 0; // 최초의 물고기 인식 광센서
int lazer_count = 0; // 불완전한 레이저 작동 오류를 방지하기 위한 카운트
bool divide_result = 1; // 광센서 분류 결과

bool divide_state = 0; // 메인에서 분리 State ON/OFF
int count = 0; // LED Timer Delay
int main_state = 1; // 메인 함수 switch문 작동

// 물고기 감지 설정 관련 타이머 변수
unsigned long currentTime = 0;
unsigned long stateChangeStartTime = 0;
const unsigned long undetectedTime = 20000; // 20초간 물체 미감지시 작동

// 데이터 저장 공간
char fishDivide = {}; // 물고기 분류값
char jetsonSend = {}; // 젯슨에서 보낸 메세지

// 최초로 컨베이어 벨트의 물고기 감지
void firstDetect() {
    int firstPhotoSensor = analogRead(detectPhotoSensor); // 물체 인식 센서 작동
    if (firstPhotoSensor > photoThreshold) {
        detectValue = 0;
    }
    else if (firstPhotoSensor <= photoThreshold) {
        detectValue = 1;
    }
}

void divide(bool divide_state) { // 물고기 분류 시작 - 종료 - Jetson으로 결과 송신
    if (divide_state == 1) {
        if (fishDivide == '1') { // 1번 모터 작동
            fishDivider_ServoA.attach(fishDivider_numA);
            fishDivider_ServoA.write(123); // 통로로 물고기가 들어가게 모터 작동
            photoState(1);
        }
        else if (fishDivide == '2') {
            fishDivider_ServoB.attach(fishDivider_numB);
            fishDivider_ServoB.write(123);
            photoState(2);
        }
        else if (fishDivide == '3') {
            fishDivider_ServoC.attach(fishDivider_numC);
            fishDivider_ServoC.write(123);
            photoState(3);
        }
        else {
            photoState(4);
        }
        divide_state = 0; // 분류 완료
    }
}

// 광센서로 물고기 감지 이후 카운터 및 서보모터 작동
int photoState(int photoSensorNum) {
    divide_result = 1;
    while (1) {
        int photoValue = analogRead(photoSensorNum);  // photoSensorNum : 1 ~ 4 = A1 ~ A4
        if (photoValue < photoThreshold) {
            break; // 물고기 감지시 while문 탈출
        }
        else {
            currentTime = millis(); // 현재 시간 실시간 갱신
            if (currentTime - stateChangeStartTime >= undetectedTime) { // 설정한 시간이 지났을때 실행
                stateChangeStartTime = currentTime; // 변경 시간 갱신
                divide_result = 0;
                main_state = 2; // 메인 함수 변경
                break;
            }
            continue;
        }
    }

    if (divide_result == 1) {
        if (photoSensorNum == 1) { // 1번 수조 카운트
            fishDivider_ServoA.write(90); // 문 닫기
            delay(50);
            fishDivider_ServoA.detach();
            digitalWrite(LED_A, HIGH);
            Serial.print('A');
        }
        else if (photoSensorNum == 2) { // 2번 수조 카운트
            fishDivider_ServoB.write(90);
            delay(50);
            fishDivider_ServoB.detach();
            digitalWrite(LED_B, HIGH);
            Serial.print('B');
        }
        else if (photoSensorNum == 3) { // 3번 수조 카운트
            fishDivider_ServoC.write(90);
            delay(50);
            fishDivider_ServoC.detach();
            digitalWrite(LED_C, HIGH);
            Serial.print('C');
        }
        else if (photoSensorNum == 4) { // 4번 수조 카운트
            digitalWrite(LED_D, HIGH);
            Serial.print('D');
        }
    }

    fishDivide = '0';
    count = 0; // LED를 Off하기 위한 초기화 변수
}

void LEDdelay_Off() { // LED 모두 Off하는 함수
    if (count == 20000) {
        digitalWrite(LED_A, LOW); digitalWrite(LED_B, LOW);
        digitalWrite(LED_C, LOW); digitalWrite(LED_D, LOW);
    }
    count++;
}

// 서보모터 및 통신 세팅
void setup() {
    Serial.begin(9600); // 화면 출력
    //fishDivider_ServoA.attach(fishDivider_numA); // 모터 A ~ C 세팅
    //fishDivider_ServoB.attach(fishDivider_numB);
    //fishDivider_ServoC.attach(fishDivider_numC);
    pinMode(LED_A, OUTPUT); pinMode(LED_B, OUTPUT); // LED A ~ D 세팅
    pinMode(LED_C, OUTPUT); pinMode(LED_D, OUTPUT);
    pinMode(resetSW_PIN, INPUT);
}

// 메인 함수
void loop() {
    switch (main_state) {
    case 1:
        firstDetect(); // 최초로 컨베이어 벨트의 물고기 감지

        if ((detectValue == 1) && (objectDetect == 1)) { // 물체 감지시 jetson으로 메세지 송신
            Serial.print('S'); // 최초에 물고기 감지시 'S'를 jetson으로 송신
            objectDetect = 0;
        }
        else if ((detectValue == 0) && (objectDetect == 0) && (lazer_count > 100)) {
            objectDetect = 1;
            lazer_count = 0;
            return;
        }

        if (Serial.available()) { // 통신이 확인 되었을때 시행
            fishDivide = Serial.read();
            stateChangeStartTime = millis(); // 데이터 입력된 시간 설정
            divide_state = 1;
        }
        else {
            divide_state = 0;
        }

        divide(divide_state); // 물고기 분류 시작 - 종료 - Jetson으로 결과 송신
        LEDdelay_Off(); // LED A ~ D Off
        lazer_count++;
        break;

    case 2: // 물고기가 일정 시간동안 감지가 안되었을 경우 LED 4개 ON
        divide_result = 0;
        digitalWrite(LED_A, HIGH); digitalWrite(LED_B, HIGH);
        digitalWrite(LED_C, HIGH); digitalWrite(LED_D, HIGH);
        if (digitalRead(resetSW_PIN)) { // 스위치를 누르면 해제 및 초기화
            digitalWrite(LED_A, LOW); digitalWrite(LED_B, LOW);
            digitalWrite(LED_C, LOW); digitalWrite(LED_D, LOW);
            fishDivider_ServoA.attach(fishDivider_numA);
            fishDivider_ServoA.write(90);
            delay(50);
            fishDivider_ServoA.detach();

            fishDivider_ServoB.attach(fishDivider_numB);
            fishDivider_ServoB.write(90);
            delay(50);
            fishDivider_ServoB.detach();
            
            fishDivider_ServoC.attach(fishDivider_numC);
            fishDivider_ServoC.write(90);
            delay(50);
            fishDivider_ServoC.detach();
            main_state = 1;
        }
    }
}