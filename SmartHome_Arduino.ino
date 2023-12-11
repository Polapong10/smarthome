#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
WiFiClient client;
PubSubClient mqtt(client);
DynamicJsonDocument docs(1024);
DynamicJsonDocument docs1(1024);  // doc for serialize
DynamicJsonDocument docd(1024);   // doc for de-serialize
char output[255];
char output2[255];
char input[255];


// MyData dataToStore;
#define WIFI_STA_NAME "SilverIcePhone"
#define WIFI_STA_PASS "0944091100Aa"
#define MQTT_SERVER "119.59.99.155"
#define MQTT_PORT 8883
#define MQTT_USERNAME ""
#define MQTT_PASSWORD ""
#define MQTT_NAME "B6303754_dv"
void setup() {
  Serial.begin(115200);
  // xTaskCreate(&task1, "Task 1", 2048, NULL, 5, NULL);
  pinMode(19, OUTPUT);
  pinMode(18, OUTPUT);
  pinMode(26, OUTPUT);
  pinMode(12, OUTPUT);
  ledcSetup(0, 5000, 8);
  ledcAttachPin(25, 0);
  ledcSetup(2, 5000, 8);
  ledcAttachPin(22, 2);
  ledcSetup(4, 5000, 8);
  ledcAttachPin(32, 4);
  ledcSetup(6, 5000, 8);
  ledcAttachPin(21, 6);
  // xTaskCreate(&task1, "Task 1", 2048, NULL, 5, NULL);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_STA_NAME, WIFI_STA_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    digitalWrite(2, !digitalRead(2));
  }
  digitalWrite(2, HIGH);
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  mqtt.setServer(MQTT_SERVER, MQTT_PORT);
  mqtt.setCallback(callback);
}

void callback(char *topic, byte *payload, unsigned int length) {
  String getload;
  String loadchar;
  // String sts;
  deserializeJson(docd, payload, length);
  serializeJson(docd, getload);
  Serial.println(getload);
  for (int i = 0; i < getload.length(); i++) {
    if (getload.charAt(i) == ':') {
      break;
    }
    if (getload.charAt(i) != '{' && getload.charAt(i) != '"') {
      loadchar += getload.charAt(i);
    }
  }
  Serial.println(loadchar);
  String sts = docd["" + loadchar + ""];
  if (loadchar == "bed") {
    if (sts == "ON") {
      digitalWrite(19, 1);
    } else if (sts == "OFF") {
      digitalWrite(19, 0);
    }
  }
  if (loadchar == "liv") {
    if (sts == "ON") {
      digitalWrite(18, 1);
      // Serial.println("Hello");
    } else if (sts == "OFF") {
      digitalWrite(18, 0);
    }
  }
  if (loadchar == "kitchen") {
    if (sts == "ON") {
      digitalWrite(26, 1);
    } else if (sts == "OFF") {
      digitalWrite(26, 0);
    }
  }
  if (loadchar == "fan") {
    int pwm = map(sts.toInt(), 0, 100, 0, 255);
    Serial.println("pwm = "+String(pwm)+"");
    ledcWrite(0, pwm);
  }
  if (loadchar == "R") {
    int pwm = sts.toInt();
    Serial.println("R = "+String(pwm)+"");
    ledcWrite(2, pwm);
  }
  if (loadchar == "G") {
    int pwm = sts.toInt();
    Serial.println("R = "+String(pwm)+"");
    ledcWrite(4, pwm);
  }
  if (loadchar == "B") {
    int pwm = sts.toInt();
    Serial.println("R = "+String(pwm)+"");
    ledcWrite(6, pwm);
  }
}

// void task1(void *pvParameters) {
//   while (true) {
//     docs["temp"] = random(25, 27);
//     docs["humid"] = random(65, 75);
//     docs["PM"] = random(10, 35);
//     docs["db"] = random(50, 60);
//     serializeJson(docs, output);
//     mqtt.publish("/test/py", output);
//     vTaskDelay(5000);
//     docs1["electric"] = random(200, 240);
//     docs1["water"] = random(1,3);
//     serializeJson(docs1, output2);
//     mqtt.publish("test2/influx", output2);
//     Serial.println("Mqtt2 send");
//     vTaskDelay(5000);
//   }
// }

void loop() {

  if (mqtt.connected() == false) {
    Serial.print("MQTT connection... ");
    if (mqtt.connect(MQTT_NAME, MQTT_USERNAME, MQTT_PASSWORD)) {
      Serial.println("connected");
      mqtt.subscribe("smarthome/fan");
    } else {
      Serial.println("failed");
      delay(1000);
    }
  } else {
    mqtt.loop();
    int temp = map(analogRead(33), 0, 4095, 35, 20);
    delay(10);
    int humid = map(analogRead(34), 0, 4095, 70, 40);
    delay(10);
    int co2 = map(analogRead(35),0 ,4095, 1000, 50 );
    if(co2>=500){
      digitalWrite(12,1);
    }
    else{
      digitalWrite(12,0);
    }
    delay(100);
    docs["temp"] = temp;
    docs["humid"] = humid;
    docs["co2"] = co2;
    serializeJson(docs, output);
    mqtt.publish("smarthome/sensor", output);
    digitalWrite(12,0);
    delay(500);
    // docs["temp"] = (random(2500, 2700) / 100.0);
    // docs["humid"] = (random(6500, 7500) / 100.0);
    // docs["do0"] = (random(700, 900) / 100.0);
    // docs["do1"] = (random(500, 600) / 100.0);
    // docs["do2"] = (random(300, 400) / 100.0);
    // serializeJson(docs, output);
    // mqtt.publish("v1/devices/me/telemetry", output);
    // delay(5000);
  }
}
