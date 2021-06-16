#include <Adafruit_NeoPixel.h>

#define LED_PIN 6              // pin the LED strip is connected to
#define LED_NUMBER 15          // number of LEDs in a strip
#define MAXIMUM_BRIGHTNESS 255 //

// initialise the LED strip
// docs: https://adafruit.github.io/Adafruit_NeoPixel/html/class_adafruit___neo_pixel.html
Adafruit_NeoPixel strip = Adafruit_NeoPixel(LED_NUMBER, LED_PIN, NEO_GRB + NEO_KHZ800);
byte led_index = 0;
byte led_red = 0;
byte led_green = 0;
byte led_blue = 0;
byte led_brightness = MAXIMUM_BRIGHTNESS;
int unavailable_count = 0;
bool offSwitch = false;

//////////////////////////////////
///////       MAIN        ////////
//////////////////////////////////
void setup()
{
    // initialise the LED strip
    strip.begin();
    strip.setBrightness(led_brightness);
    strip.show();
    // initialise serial communication
    Serial.begin(9600);
}

void loop()
{
    if (Serial.available())
    {
        // if the serial data is coming in, reset the variables used to shut down
        unavailable_count = 0;
        offSwitch = false;
    }
    while (Serial.available() > 0)
    {
        // keep reading serial data while the data is coming in
        if (Serial.read() != '>')
            continue; // wait for the starting character

        // starting character encountered, read the next 12 characters
        led_index = readSerialThreeDigitNumber();
        led_red = readSerialThreeDigitNumber();
        led_green = readSerialThreeDigitNumber();
        led_blue = readSerialThreeDigitNumber();

        // update an LED value accordingly
        updateLEDValue(led_index, led_red, led_green, led_blue);
    }

    // logic to turn off LEDs if no serial data is coming in for a while
    unavailable_count++;
    delay(10); // wait a little bit, but not so long that it would impact the framerate
    if (unavailable_count > 10 && !offSwitch)
    {
        shutdownSequence();
        offSwitch = true;
    }
}
//////////////////////////////////

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
    strip.show();
}

void shutdownSequence()
{
    // old timey tv shutdown animation
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

        // wait for the animation frame
        // the map() is so that the animation accelerates
        delay(map(i, 0, middle_pixel - 1, wait * 5, wait / 5));
    }

    // fade out the middle pixel
    for (int i = 0; i < LED_NUMBER * 3; i++)
    {
        if (Serial.available() > 0)
            return; // stop the animation if there is serial data coming in

        middle_pixel_brightness = map(i, 0, LED_NUMBER * 3 - 1, 255, 0);
        strip.setPixelColor(middle_pixel, strip.Color(middle_pixel_brightness, middle_pixel_brightness, middle_pixel_brightness));

        strip.show();

        // wait for the animation frame
        delay(wait);
    }
}
