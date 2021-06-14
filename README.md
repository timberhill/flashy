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

### Demo:
[![FLASHY demo](https://img.youtube.com/vi/ytjLecwWzHU/0.jpg)](https://www.youtube.com/watch?v=ytjLecwWzHU "FLASHY demo")

## Requirements

Some coding exp because this project is in its infancy.

### Software

- Windows

    - the motivation is to use it while gaming, so currently it's only for Windows

- [Arduino IDE](https://www.arduino.cc/en/guide/windows) to upload the code to a board

- Python 3+ and some packages:

    - `pip install pyserial pywin32 pyimage`

### Hardware

I use Adafruit Flora as it is the one I had lying around.
It can be any Arduino board that supports serial communication though - might just need to update the receiver code.

In addition, of course, you need a strip of LEDs connected.
Currently the onboard script only supports addressable LEDs and erquired only one pin on the board.
Non-addressable LEDs are on the [todo list](TODO.md).

## Usage

1. Create or use a profile in `settings/profiles/` and reference it in the settings
    - you can also put the profile json into the settings file directly
1. Connect the board with the LEDs to the PC
2. Upload the receiver code if not there already
    - make sure that the variables like the length of the LED strip and pin number are set correctly for your setup
3. Open `powershell` or `bash`, cd into the repo directory and run the script: `python -m transmitter`
4. Adjust the settings in `settings/settings.json` if necessary

## Configuration

The script reads the configs from `settings/settings.json` and `settings/profiles/` if needed.
Below are descriptions of the fields.

### `settings.json`

`"port": null,`

    ^ Serial port the board is connected to.
    If null, it will use the first serial device it finds.

`"baud": 9600,`

    ^ baud rate for the serial communication.
    Must be the same.

`"strip_size": 15,`

    ^ number of LEDs in the strip.

`"log_level": "INFO",`

    ^ log level.
    Values: DEBUG, INFO, WARN, ERROR, CRITICAL.
    If you don't need any logs, keep it at CRITICAL

`"threads": 4,`

    ^ how many threads to use for reading the pixel values.
    Must be less that the number of the LEDs.
    It takes about 15ms to read a pixel value, so use less than 5 threads per LED.

`"frame_delay": 10,`

    ^ delay between frames in milliseconds.
    Keep it at least 1ms for the CPU usage to stay low.

`"profile": "profiles\\bottom1_2560x1440.json"`

    ^ path to the profile to use.
    Can either contain a path to a profile or the profile contents.

### Profiles

`"description": "Row of pixels at the bottom of the screen, covering middle third of the length",`

    ^ Description of the profile.

`"map": [
    [720,  1385],
    [791,  1385],
    [862,  1385],
    [934,  1385],
    [1005, 1385],
    [1077, 1385],
    [1148, 1385],
    [1220, 1385],
    [1291, 1385],
    [1362, 1385],
    [1434, 1385],
    [1505, 1385],
    [1577, 1385],
    [1648, 1385],
    [1720, 1385]
]`

    ^ Contains a list of [x,y] coordinates on the screen pixel values to send into the corresponding LED index.
