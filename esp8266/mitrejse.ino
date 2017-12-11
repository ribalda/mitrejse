/*
MIT License

Copyright (c) 2017 Ricardo Ribalda, Qtechnology A/S

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPUpdateServer.h>
#include <ESP8266HTTPClient.h>
#include "Adafruit_GFX.h"
#include "Adafruit_SSD1306.h"

const char* ssid = "***";
const char* password = "****";
const char* url = "http://****:1414/station?name=Work%20C&esp=1";

#define OLED_MOSI  13   //D1
#define OLED_CLK   14   //D0
#define OLED_DC    2
#define OLED_CS    15
#define OLED_RESET 16
#define LED_PIN 2

ESP8266WebServer server(80);
ESP8266HTTPUpdateServer httpUpdater;

Adafruit_SSD1306 display(OLED_MOSI, OLED_CLK, OLED_DC, OLED_RESET, OLED_CS);

static String hostname(void)
{
	String result;
	uint8_t mac[6];
	WiFi.macAddress(mac);
	for (int i = 0; i < 6; ++i) {
		result += String(mac[i], 16);
	}
	return result;
}

void setup_oled() {
	display.begin(SSD1306_SWITCHCAPVCC);
	display.display();
	display.clearDisplay();
	display.setTextSize(1);
	display.setTextColor(WHITE);
	display.setCursor(0,0);
}

void show() {
	display.display();
	display.clearDisplay();
	display.setCursor(0,0);
}

void setup_wifi() {
	// Connect to WiFi network
	WiFi.mode(WIFI_STA);
	display.print("Connecting to ");
	display.println(ssid);

	// Set the hostname
	WiFi.hostname(hostname());
	WiFi.begin(ssid, password);
	while (WiFi.status() != WL_CONNECTED) {
		delay(500);
		display.print(".");
		display.display();
	}
	display.clearDisplay();

	// Start the server
	httpUpdater.setup(&server);
	server.begin();

	display.setCursor(0,0);
	// Print the IP address
	display.println("OTA URL: ");
	display.print("http://");
	display.print(WiFi.localIP());
	display.println("/update");
	show();
}

void setup() {
	// Setup serial-output
	Serial.begin(115200);
	delay(10);

	// Pin 2 has an integrated LED - configure it, and turn it off
	pinMode(LED_PIN, OUTPUT);
	digitalWrite(LED_PIN, HIGH);

	setup_oled();
	setup_wifi();
	display.setTextSize(5);

}

void loop() {
	HTTPClient http;

	server.handleClient();

	http.begin(url);
	if (http.GET() == HTTP_CODE_OK) {
		display.printf(" %2.d ", atoi(http.getString().c_str()));
		show();
		delay(30*1000);
	}
	http.end();
}

