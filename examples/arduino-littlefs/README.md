How to build PlatformIO based project
=====================================

1. [Install PlatformIO Core](https://docs.platformio.org/page/core.html)
2. Download [development platform with examples](https://github.com/platformio/platform-raspberrypi/archive/develop.zip)
3. Extract ZIP archive
4. Run these commands:

```shell
# Change directory to example
$ cd platform-raspberrypi/examples/arduino-littlefs

# Build project
$ pio run

# Upload firmware
$ pio run --target upload

# Clean build files
$ pio run --target clean
```

## Notes

Take care to use the project task "Upload Filesystem Image" to actually upload the LittleFS filesystem image onto your microcontroller. Otherwise, the firmware will not find the expected file. See documentation

https://arduino-pico.readthedocs.io/en/latest/platformio.html#filesystem-uploading

This also serves as test to build a unified UF2 image that contains both firmware and filesystem. To build it, use the project task "Build unified FW + FS UF2 Image", or

```sh
$ pio run --target buildunified
```