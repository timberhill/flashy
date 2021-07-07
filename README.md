# flashy
A very forced acronym for ```Fun LED Array Screen Halo yisss```

This is a wee pet project aimed to send the colour/brightness data from the monitor edges to some LEDs. 
The idea is that, for instance, if your monitor is standing in front of a wall, the LEDs will create a glow based on what is happening on the screen.
It's a work in progress and will be improved. Maybe. Maybe not though.

### How it works

There are two components to this - one is the code running on the arduino board (_receiver_), the other is a script running on the PC (_transmitter_).
The two communicate via serial communication over USB.

Transmitter runs one or more threads getting the pixel colours from the screen using [`BitBlt`](https://docs.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-bitblt) function and adding them to the queue.
Another thread grabs those values from the queue and send them to the board.
Receiver constantly waits for the pixel data and uses it to colour the LEDs.

### Demo:
[![FLASHY demo](https://img.youtube.com/vi/d4MCt0d6sZ0/0.jpg)](https://youtu.be/d4MCt0d6sZ0 "FLASHY demo")

## Requirements

Some coding exp because this is DIY af.

### Software

- Windows / MacOS

- [Arduino IDE](https://www.arduino.cc/en/guide/windows) to upload the code to a board

- Python 3+ and some packages:

    - Windows:`pip install pyserial pywin32 pyimage`

    - MacOS:`pip install pyserial pyobjc-framework-Quartz`

### Hardware

I use Adafruit Flora as it is the one I had lying around.
It can be any Arduino board that supports serial communication though - might just need to update the receiver code.

In addition, of course, you need a strip of LEDs connected.
Currently the onboard script only supports addressable LEDs and requires only one pin on the board.

## Setup

I used this setup (different board, of course):
![board setup](https://www.eerkmans.nl/wp-content/uploads/2016/02/arduino_2.png)

There are lots of tutorials on programming the boards that can help, like 
[this](https://learn.adafruit.com/getting-started-with-flora/blink-onboard-neopixel), 
[this](https://learn.adafruit.com/adafruit-neopixel-uberguide/powering-neopixels) 
and/or [this](https://www.eerkmans.nl/powering-lots-of-leds-from-arduino/).

1. Create or use a profile in `settings/profiles/` and reference it in the settings
    - you can also put the profile json into the settings file directly
2. Connect the board with the LEDs to the PC
3. Connect the board and upload the receiver code
    - make sure that the variables like the length of the LED strip and pin number are set correctly for your setup

## Usage

1. Connect the board to USB
2. Open `powershell`/`bash`/`cmd`, cd into the repo directory and run the script: `python -m transmitter`
    - OR just run the batch script in this repo (`flashy.bat`)
    - The LEDs should light up at this point if it was set up correctly
3. Adjust the settings in `settings/settings.json` if necessary
    - you can try different profiles, or a different number of screen reader threads (just one works best on my laptop though)
