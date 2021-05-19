#include <Adafruit_NeoPixel.h>

#define LED_PIN 6  // pin the LED strip is connected to
#define LED_NUMBER 15  // number of LEDs in a strip
#define DIMMING_STEP 1  // dim LEDs by this step when there is no data coming in
#define MAXIMUM_BRIGHTNESS 100  // 

// initialise the LED strip
// docs: https://adafruit.github.io/Adafruit_NeoPixel/html/class_adafruit___neo_pixel.html
Adafruit_NeoPixel strip = Adafruit_NeoPixel(LED_NUMBER, LED_PIN, NEO_GRB + NEO_KHZ800);
byte led_index = 0;
byte led_red = 0;
byte led_green = 0;
byte led_blue = 0;
byte led_brightness = MAXIMUM_BRIGHTNESS;
int unavailable_count = 0;

//////////////////////////////////
///////       MAIN        ////////
//////////////////////////////////
void setup() {
    // initialise the LED strip
    strip.begin();
    strip.setBrightness(led_brightness);
    strip.show();
    // initialise serial communication
    Serial.begin(9600);
}

void loop() {
    while (Serial.available() > 0) {
        if (Serial.read() != '>') continue;  // wait for the starting character
        unavailable_count = 0;

        // starting character encountered, read the next 12 characters
        led_index = readSerialThreeDigitNumber();
        led_red = readSerialThreeDigitNumber();
        led_green = readSerialThreeDigitNumber();
        led_blue = readSerialThreeDigitNumber();

        // update an LED value accordingly
        updateLEDValue(led_index, led_red, led_green, led_blue);
    }

    unavailable_count++;
    delay(10);
    if (unavailable_count > 100) {
        switchOffAllLEDs();
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


void updateLEDValue(byte i, byte r, byte g, byte b) {
    // set the value of an LED and refresh the strip
    strip.setPixelColor(i, strip.Color(r,g,b));
    strip.show();
}


void switchOffAllLEDs() {
    for (int i = 0; i < LED_NUMBER; i++) updateLEDValue(i, 0, 0, 0);
    strip.show();
}
