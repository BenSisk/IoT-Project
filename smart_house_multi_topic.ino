#include <WiFi.h>
#include <WiFiClient.h>
#include <analogWrite.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>

Servo servo1;
Servo servo2;

int minUs = 500;
int maxUs = 2400;

// Your WiFi credentials.
// Set password to "" for open networks.


//char ssid[] = "iotsmarthome";
//char pwd[] = "raspberry";

// MQTT client
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
//if in doubt swap back to hive
char mqttServer [] = "broker.hivemq.com";
//char mqttServer [] = "192.168.50.193";
int mqttPort = 1883;

int heating = 4;
int light = 17;
int servo1Pin = 21;
int servo2Pin = 23;

int pos = 0;      // position in degrees

void connectToWiFi() {
  Serial.print("Connecting to ");

  WiFi.begin(ssid, pwd);
  Serial.println(ssid);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.print("Connected.");
}

void setupMQTT() {
  mqttClient.setServer(mqttServer, mqttPort);
  // set the callback function
  mqttClient.setCallback(callback);
}

void reconnect() {
  Serial.println("Connecting to MQTT Broker...");
  while (!mqttClient.connected()) {
      Serial.println("Reconnecting to MQTT Broker..");
      String clientId = "ESP32Client-";
      clientId += String(random(0xffff), HEX);
     
      if (mqttClient.connect(clientId.c_str())) {
        Serial.println("Connected.");
        // subscribe to topic
        uint16_t packIdSub = mqttClient.subscribe("NorthumbriaUniIoTSmartHome/Heating");
        uint16_t packIdSub2 = mqttClient.subscribe("NorthumbriaUniIoTSmartHome/Motion");
        uint16_t packIdSub3 = mqttClient.subscribe("NorthumbriaUniIoTSmartHome/Blind");
        uint16_t packIdSub4 = mqttClient.subscribe("NorthumbriaUniIoTSmartHome/Window");
      }
  }
}

// This function is called every time the Virtual Pin 0 state changes
void heatingon()
{
    digitalWrite(heating, HIGH);
}
void heatingoff()
{
    digitalWrite(heating, LOW);
}
void lighton()
{
    digitalWrite(light, HIGH);
}
void lightoff()
{
    digitalWrite(light, LOW);
}

void blindcontrol(int val){
  servo1.attach(servo1Pin, minUs, maxUs);
  servo1.write(val);                  
  delay(200);                           
  servo1.detach();
}
void windowcontrol(int val){
  servo2.attach(servo2Pin, minUs, maxUs);
  servo2.write(val);                  
  delay(200);                          
  servo2.detach();
}


void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Callback - ");
  Serial.print("Message:");
  for (int i = 0; i < length; i++) {
    Serial.print(topic);
    Serial.println((char)payload[i]);

    if (strcmp(topic, "NorthumbriaUniIoTSmartHome/Heating") == 0){
      switch((char)payload[i]){
        case '0':
          heatingoff();
          break;
        case '1':
          heatingon();
          break;
        default:
          break;
      }
    }
    if (strcmp(topic, "NorthumbriaUniIoTSmartHome/Motion") == 0){
      switch((char)payload[i]){
        case '0':
          lightoff();
          break;
        case '1':
          lighton();
          break;
        default:
          break;
      }
    }
    if (strcmp(topic, "NorthumbriaUniIoTSmartHome/Blind") == 0){
      switch((char)payload[i]){
        case '0':
          blindcontrol(230);
          break;
        case '1':
          blindcontrol(1);        
          break;
        default:
          break;
      }
    }
        if (strcmp(topic, "NorthumbriaUniIoTSmartHome/Window") == 0){
      switch((char)payload[i]){
        case '0':
          windowcontrol(10);
          break;
        case '1':
          windowcontrol(160);        
          break;
        default:
          break;
      }
    }
  }
}

void setup()
{
  // Allow allocation of all timers
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  // Debug console
  Serial.begin(115200);
  servo1.setPeriodHertz(50);      // Standard 50hz servo
  servo2.setPeriodHertz(50);      // Standard 50hz servo
  connectToWiFi();
  setupMQTT();

  // Set all the motor control pins to outputs
  pinMode(heating, OUTPUT);
  pinMode(light, OUTPUT);
}

void loop()
{ 
  if (!mqttClient.connected())
    reconnect();
  mqttClient.loop();
}
