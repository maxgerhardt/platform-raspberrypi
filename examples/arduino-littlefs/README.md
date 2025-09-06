How to build PlatformIO based project
=====================================

1. [Install PlatformIO Core](https://docs.platformio.org/page/core.html)
2. Download [development platform with examples](https://github.com/platformio/platform-raspberrypi/archive/develop.zip)
3. Extract ZIP archive
4. Run these commands:

```shell
# Change directory to example
$ cd platform-raspberrypi/examples/arduino-blink

# Build project
$ pio run

# Upload firmware
$ pio run --target upload

# Clean build files
$ pio run --target clean
```

## Notes

For Raspberry Pi Pico devices, two Arduino cores exist:
* https://github.com/arduino/ArduinoCore-mbed
* https://github.com/earlephilhower/arduino-pico

This examples showcases how to use both of these cores in the `platformio.ini`.