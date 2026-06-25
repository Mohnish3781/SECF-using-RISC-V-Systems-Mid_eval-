#ifndef PACKET_H
#define PACKET_H

#include <stdint.h>

#define MAGIC_HEADER 0xABCD1234
#define MAX_PAYLOAD 256

typedef struct {
    uint32_t header;
    uint8_t type;
    uint16_t length;
    uint8_t payload[MAX_PAYLOAD];
    uint32_t seq;
} Packet;

#endif