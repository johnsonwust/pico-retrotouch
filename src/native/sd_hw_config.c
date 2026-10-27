/* Waveshare Pico-ResTouch-LCD-2.8: SD shares SPI1 with LCD and XPT2046.
 * Adapted from upstream Apache-2.0 sd_hw_config.c (Carl John Kugler III).
 */
#include "hw_config.h"

static spi_t spis[]={{
    .hw_inst=spi1,.miso_gpio=12,.mosi_gpio=11,.sck_gpio=10,
    .baud_rate=5000000,
    .set_drive_strength=true,
    .mosi_gpio_drive_strength=GPIO_DRIVE_STRENGTH_8MA,
    .sck_gpio_drive_strength=GPIO_DRIVE_STRENGTH_8MA
}};
static sd_card_t cards[]={{
    .pcName="0:",.spi=&spis[0],.ss_gpio=22,
    .set_drive_strength=true,.ss_gpio_drive_strength=GPIO_DRIVE_STRENGTH_8MA,
    .use_card_detect=false,.card_detected_true=-1
}};
size_t sd_get_num(void) { return count_of(cards); }
sd_card_t *sd_get_by_num(size_t n) { return n<count_of(cards)?&cards[n]:NULL; }
size_t spi_get_num(void) { return count_of(spis); }
spi_t *spi_get_by_num(size_t n) { return n<count_of(spis)?&spis[n]:NULL; }
