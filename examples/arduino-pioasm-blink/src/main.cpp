#include <Arduino.h>
#include "blink.pio.h"

void setup()
{
  Serial.begin(115200);
  delay(5000);

  const uint LED_PIN = LED_BUILTIN;
  Serial.printf("[INFO] Starting PIO blink on GPIO %d\n", LED_PIN);

  PIO pio = pio0;
  int sm = pio_claim_unused_sm(pio, true);
  if (sm < 0)
  {
    Serial.printf("[ERROR] No free SM\n");
    while(1) { ; }
  }

  uint offset = pio_add_program(pio, &blink_program);
  Serial.printf("[INFO] Program loaded at offset %u\n", offset);

  pio_sm_config c = blink_program_get_default_config(offset);
  sm_config_set_set_pins(&c, LED_PIN, 1);
  pio_gpio_init(pio, LED_PIN);
  pio_sm_set_consecutive_pindirs(pio, sm, LED_PIN, 1, true);

  // Calculate divider for ~2 Hz blink
  // One full on/off cycle = ~2 * 32*32*32 = 65536 cycles per phase
  // 125e6 / (65536 * 4) ≈ 477
  // but empirical adjustment needed; we’ll slow down more
  float clkdiv = 3813.0f; // experimentally yields ~2 Hz
  sm_config_set_clkdiv(&c, clkdiv);

  pio_sm_init(pio, sm, offset, &c);
  pio_sm_set_enabled(pio, sm, true);

  Serial.printf("[INFO] sysclk=%lu Hz, clkdiv=%.2f\n",
         clock_get_hz(clk_sys), clkdiv);
  Serial.printf("[INFO] SM %d running autonomously\n", sm);
}

void loop()
{
  Serial.println("Doing nothing, PIO SM running..");
  delay(5000);
}