#include <WiFi.h>
#include <WiFiClient.h>
#include <analogWrite.h>
#include <PubSubClient.h>

// Your WiFi credentials.
// Set password to "" for open networks.
char ssid[] = "VM5241752";
char pwd[] = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX";

// MQTT client
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
char mqttServer [] = "broker.hivemq.com";
int mqttPort = 1883;

int heating = 21;
int light = 22;
int blind = 19;


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
void blindon()
{
    digitalWrite(blind, HIGH);
}
void blindoff()
{
    digitalWrite(blind, LOW);
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
          blindoff();
          break;
        case '1':
          blindon();
          break;
        default:
          break;
      }
    }
   

  }
}

void setup()
{
  // Debug console
  Serial.begin(115200);
  connectToWiFi();
  setupMQTT();

  // Set all the motor control pins to outputs
  pinMode(heating, OUTPUT);
  pinMode(light, OUTPUT);
  pinMode(blind, OUTPUT);

}

void loop()
{
  if (!mqttClient.connected())
    reconnect();
  mqttClient.loop();
}
