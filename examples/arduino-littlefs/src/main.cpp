#include <Arduino.h>
#include <LittleFS.h>

void setup() {
  Serial.begin(115200);
  delay(5000);
  Serial.println("Initializing LittleFS...");
  // We want to explicitly test that uploading a filesystem image works.
  FSConfig cfg = FSConfig();
  cfg.setAutoFormat(false);
  LittleFS.setConfig(cfg);
  if(!LittleFS.begin()) {
    while(1) {
      Serial.println("LittleFS mount failed. Did you forget to upload a filesystem image?");
      delay(5000); 
    }
  }
  Serial.println("LittleFS mounted successfully");
}

void loop() {
  Serial.println("------ Reading file1.txt -------");
  File i = LittleFS.open("file1.txt", "r");
  if (i) {
    while (i.available()) {
      Serial.write(i.read());
    }
    Serial.println();
    Serial.println("------ file read successfully -------");
    i.close();
  } else {
    Serial.println("file1.txt not found");
  }
  delay(3000);
}