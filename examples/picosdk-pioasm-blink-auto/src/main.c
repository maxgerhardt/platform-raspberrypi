#include "pico/stdlib.h"
#include "hardware/clocks.h"
#include "hardware/pio.h"
#include "hardware/claim.h"
#include <stdio.h>
#include "blink.pio.h"

int main() {
    stdio_init_all();
    sleep_ms(3000);

    const uint LED_PIN = PICO_DEFAULT_LED_PIN;
    printf("[INFO] Starting PIO blink on GPIO %d\n", LED_PIN);

    PIO pio = pio0;
    int sm = pio_claim_unused_sm(pio, true);
    if (sm < 0) {
        printf("[ERROR] No free SM\n");
        return 1;
    }

    uint offset = pio_add_program(pio, &blink_program);
    printf("[INFO] Program loaded at offset %u\n", offset);

    pio_sm_config c = blink_program_get_default_config(offset);
    sm_config_set_set_pins(&c, LED_PIN, 1);
    pio_gpio_init(pio, LED_PIN);
    pio_sm_set_consecutive_pindirs(pio, sm, LED_PIN, 1, true);

    // Calculate divider for ~2 Hz blink
    // One full on/off cycle = ~2 * 32*32*32 = 65536 cycles per phase
    // 125e6 / (65536 * 4) ≈ 477
    // but empirical adjustment needed; we’ll slow down more
    float clkdiv = 3813.0f;   // experimentally yields ~2 Hz
    sm_config_set_clkdiv(&c, clkdiv);

    pio_sm_init(pio, sm, offset, &c);
    pio_sm_set_enabled(pio, sm, true);

    printf("[INFO] sysclk=%lu Hz, clkdiv=%.2f\n",
           clock_get_hz(clk_sys), clkdiv);
    printf("[INFO] SM %d running autonomously\n", sm);

    while (1)
        tight_loop_contents();
}
