#include <Adafruit_NeoPixel.h>

//////////// USER SETTINGS ////////////

#define LED_PIN 12                // pin the LED strip is connected to [INT]
#define LED_NUMBER 86             // number of LEDs in a strip [INT]
#define MAXIMUM_BRIGHTNESS 127    // maximum brightness of all LEDs [BYTE]
#define BAUDRATE 9600             // baud rate for serial communication [INT]
#define TIMEOUT_ITERATIONS 10000  // play the shutdown animation after this many iterations without any serial data [INT]

//////////// END OF USER SETTINGS ////////////


// initialise the LED strip
// docs: https://adafruit.github.io/Adafruit_NeoPixel/html/class_adafruit___neo_pixel.html
Adafruit_NeoPixel strip = Adafruit_NeoPixel(LED_NUMBER, LED_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel onboard_pixel = Adafruit_NeoPixel(1, 8, NEO_GRB + NEO_KHZ800);

// variables
byte led_index = 0;
byte led_red = 0;
byte led_green = 0;
byte led_blue = 0;
int unavailable_count = 0;
bool onOffSwitch = true;  // false if the strip should be off
int index = 0;


void setup()
{
    // initialise the LED strip
    strip.begin();
    strip.setBrightness(MAXIMUM_BRIGHTNESS);
    strip.show();

    // initialise the onboard neopixel
    // NOTE: this is aimed at Adafruit Flora
    onboard_pixel.begin();
    onboard_pixel.setBrightness(MAXIMUM_BRIGHTNESS);
    onboard_pixel.show();

    // initialise serial communication
    Serial.begin(BAUDRATE);
}

void loop()
{
    if (Serial.available())
    { 
        // wait for the starting character
        if (Serial.read() != '>')
            return;

        // if the serial data is coming in, reset the variables used to shut down
        unavailable_count = 0;
        onOffSwitch = true;

        // read the next 12 characters
        led_index = readSerialThreeDigitNumber();
        led_red = readSerialThreeDigitNumber();
        led_green = readSerialThreeDigitNumber();
        led_blue = readSerialThreeDigitNumber();

        // update an LED value accordingly
        updateLEDValue(led_index, led_red, led_green, led_blue);

        // this block prevents from sending data to the strip for every LED update
        // because that would be too slow
        if (index >= LED_NUMBER*0.41) {
          strip.show();
          onboard_pixel.show();
          index = 0;
        } else {
          index++;
        }
    } else {
        // logic to turn off LEDs if no serial data is coming in for a while
        if (unavailable_count > TIMEOUT_ITERATIONS && onOffSwitch)
        {
            shutdownSequence();
            onOffSwitch = false;
        } else {
            unavailable_count++;
        }
    }
}

byte readSerialThreeDigitNumber()
{
    // read and parse 3 consecutive characters into a byte value
    char a = Serial.read();
    char b = Serial.read();
    char c = Serial.read();
    return (byte)(((byte)a - 48) * 100 + ((byte)b - 48) * 10 + ((byte)c - 48));
}

void updateLEDValue(byte i, byte r, byte g, byte b)
{
    // set the value of an LED and refresh the strip
    strip.setPixelColor(i, strip.Color(r, g, b));
    if (i == LED_NUMBER/2) {
        onboard_pixel.setPixelColor(0, onboard_pixel.Color(r, g, b));
    }
}

void shutdownSequence()
{
    for (int i = 0; i < LED_NUMBER / 2; i++) {
        strip.setPixelColor(i, strip.Color(0, 0, 0));
        strip.setPixelColor(LED_NUMBER - i - 1, strip.Color(0, 0, 0));
        strip.show();
    }
    onboard_pixel.setPixelColor(0, strip.Color(MAXIMUM_BRIGHTNESS/10, MAXIMUM_BRIGHTNESS/25, MAXIMUM_BRIGHTNESS/40));
    onboard_pixel.show();
    return;
}
