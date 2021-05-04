# flashy
A very forced acronym for ```Fun LED Array Screen Halo yisss```

This is a wee pet project aimed to send the colour/brightness data from the monitor edges to some LEDs. 
The idea is that, for instance, if your monitor is standing in front of a wall, the LEDs will create a glow based on what is happening on the screen.
It's a work in progress and will be improved. Maybe.
Current aim is:

- read the colour values off a screen
- send them to the microcontroller
- light up the LEDs accordingly
- PROFIT

## Requirements

Some coding exp because this project is in its infancy. Feel free to contact me though. Good luck.

### Software

- Arduino IDE
- Python 3+

### Hardware

I use Adafruit Flora as it is the one I had lying around.
It can be any Arduino board that supports serial communication though - might just need to update the [onboard code](receiver/receiver.ino).
Currently it just uses the onboard LED as a test, but eventually it will use an LED strip with as many pixels as you can power.


## TO DO

- Figure out the most efficient way of getting the pixel data off the screen (Windows only for now)
- Create a settings file and manager (possibly json?)
- Create "profiles" support - files with the LED-pixel to screen pixel relations
- Optimise getting the screen data from profiles to not read the pixel data twice

    ...
