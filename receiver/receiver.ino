#include <Adafruit_NeoPixel.h>

#define LED_PIN 8  // pin the LED strip is connected to
#define LED_NUMBER 1  // number of LEDs in a strip

// initialise the LED strip
Adafruit_NeoPixel strip = Adafruit_NeoPixel(LED_NUMBER, LED_PIN, NEO_GRB + NEO_KHZ800);


//////////////////////////////////
///////       MAIN        ////////
//////////////////////////////////
void setup() {
    // initialise the LED strip
    strip.begin();
    strip.setBrightness(100);
    strip.show();
    // initialise serial communication
    Serial.begin(9600);
}

void loop() {
    while (Serial.available() > 0) {
        // wait for the starting character
        char start = Serial.read();
        if (start != '>') {
            continue;
        }

        // starting character encountered, read the next 12 characters
        byte led_index = readSerialThreeDigitNumber();
        byte led_red = readSerialThreeDigitNumber();
        byte led_green = readSerialThreeDigitNumber();
        byte led_blue = readSerialThreeDigitNumber();

        // update an LED value accordingly
        updateLedValue(led_index, led_red, led_green, led_blue);
    }
}
//////////////////////////////////


byte readSerialThreeDigitNumber() {
    // read and parse 3 consecutive characters into a byte value
    char a = Serial.read();
    char b = Serial.read();
    char c = Serial.read();
    return (byte) (((byte)a - 48)*100 + ((byte)b - 48)*10 + ((byte)c - 48));
}


void updateLedValue(byte i, byte r, byte g, byte b) {
    // set the value of an LED and refresh the strip
    strip.setPixelColor(i, strip.Color(r,g,b));
    strip.show();
}
