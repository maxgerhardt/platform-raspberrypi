/**
 * Copyright (c) 2020 Raspberry Pi (Trading) Ltd.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */
#include <stdio.h>
#include "pico/stdlib.h"
#include "pico/status_led.h"

// Pico W devices use a GPIO on the WIFI chip for the LED,
// so when building for Pico W, CYW43_WL_GPIO_LED_PIN will be defined
#ifdef CYW43_WL_GPIO_LED_PIN
#include "pico/cyw43_arch.h"
#endif

#ifndef LED_DELAY_MS
#define LED_DELAY_MS 250
#endif

// Perform initialisation
int pico_led_init(void) {
#if defined(PICO_DEFAULT_LED_PIN)
    // A device like Pico that uses a GPIO for the LED will define PICO_DEFAULT_LED_PIN
    // so we can use normal GPIO functionality to turn the led on and off
    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
#elif defined(CYW43_WL_GPIO_LED_PIN)
    // For Pico W devices we need to initialise the driver etc
    int ret = cyw43_arch_init();
    if (ret != PICO_OK) {
        return ret;
    }
#endif
    // colored status LED in addition to regular one
#if defined (PICO_COLORED_STATUS_LED_AVAILABLE)
    if(!status_led_init()) {
        printf("Failed to initialize status led!\n");
        return PICO_ERROR_IO;
    } else {
        printf("Colored status LED init OK!\n");
    }
#else
    printf("No colored status LED defined!\n");
#endif
    return PICO_OK;
}

// Turn the led on or off
void pico_set_led(bool led_on) {
#if defined(PICO_DEFAULT_LED_PIN)
    // Just set the GPIO on or off
    gpio_put(PICO_DEFAULT_LED_PIN, led_on);
#elif defined(CYW43_WL_GPIO_LED_PIN)
    // Ask the wifi "driver" to set the GPIO on or off
    cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, led_on);
#endif
#if defined (PICO_COLORED_STATUS_LED_AVAILABLE)
    if(led_on) {
        /* green */
        colored_status_led_set_on_with_color(
            PICO_COLORED_STATUS_LED_COLOR_FROM_WRGB(128, 0, 255, 0)
        );
    } else {
        colored_status_led_set_state(false);
    }
#endif
}

int main() {
    stdio_init_all(); // via USB or UART as configured in platformio.ini
    int rc = pico_led_init();
    hard_assert(rc == PICO_OK);
    while (true) {
        printf("Hello, world!\n");
        pico_set_led(true);
        sleep_ms(LED_DELAY_MS);
        pico_set_led(false);
        sleep_ms(LED_DELAY_MS);
    }
}