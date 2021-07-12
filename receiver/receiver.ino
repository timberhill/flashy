#include <Adafruit_NeoPixel.h>

//////////// USER SETTINGS ////////////

#define LED_PIN 12                // pin the LED strip is connected to [INT]
#define LED_NUMBER 1              // number of LEDs in a strip [INT]
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
    // old timey tv shutdown animation, sort of
    int middle_pixel = LED_NUMBER / 2; // define the middle pixel
    int wait = 100 / LED_NUMBER;       // defines animation speed, independent of the length of the strip
    byte middle_pixel_brightness = 0;

    // turn off the pixels starting from the edges of the strip
    // at the same time, brighten the middle pixel
    for (int i = 0; i < middle_pixel; i++)
    {
        if (Serial.available() > 0)
            return; // stop the animation if there is serial data coming in

        strip.setPixelColor(i, strip.Color(0, 0, 0));
        strip.setPixelColor(LED_NUMBER - i - 1, strip.Color(0, 0, 0));

        middle_pixel_brightness = map(i, 0, middle_pixel - 1, 0, 255);
        strip.setPixelColor(middle_pixel, strip.Color(middle_pixel_brightness, middle_pixel_brightness, middle_pixel_brightness));

        strip.show();

        // wait for the next animation frame
        // the map() makes the animation accelerate
        delay(map(i, 0, middle_pixel-1, wait*5, wait/5));
    }

    // fade out the middle pixel
    for (int i = 0; i < LED_NUMBER * 3; i++)
    {
        if (Serial.available() > 0)
            return; // stop the animation if there is serial data coming in

        middle_pixel_brightness = map(i, 0, LED_NUMBER * 3 - 1, 255, 0);
        strip.setPixelColor(middle_pixel, strip.Color(middle_pixel_brightness, middle_pixel_brightness, middle_pixel_brightness));
        onboard_pixel.setPixelColor(0, strip.Color(middle_pixel_brightness, middle_pixel_brightness, middle_pixel_brightness));
        onboard_pixel.show();
        strip.show();

        // wait for the next animation frame
        delay(wait);
    }
}
