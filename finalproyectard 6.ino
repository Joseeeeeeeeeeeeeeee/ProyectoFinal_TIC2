int sensor = 7;
int val;
int led = 12;
int buz = 10;

void setup() {
  // put your setup code here, to run once:
  pinMode(sensor,INPUT);
  Serial.begin(9600);
  pinMode(led, OUTPUT);
  pinMode(buz, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  val = digitalRead(sensor);
  if (val == LOW){
    digitalWrite(led, HIGH);
    delay(100);
    tone(buz, 2000, 64);
    delay(100);
    Serial.println("FLAP");
  }
  else {
    digitalWrite(led, LOW);
    delay(100);
  }
}
