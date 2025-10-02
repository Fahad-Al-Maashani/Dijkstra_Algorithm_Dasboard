#include "packet.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

Packet* create_packet(uint32_t id, const uint8_t *src, const uint8_t *dst,
                     uint16_t size, PacketPriority priority) {
    Packet *packet = (Packet*)malloc(sizeof(Packet));
    if (!packet) return NULL;

    packet->packet_id = id;
    memcpy(packet->src_mac, src, 6);
    memcpy(packet->dst_mac, dst, 6);
    packet->payload_size = size;
    packet->priority = priority;
    packet->retries = 0;

    // Allocate payload
    packet->payload = (uint8_t*)malloc(size);
    if (!packet->payload) {
        free(packet);
        return NULL;
    }

    // Initialize payload with dummy data
    for (int i = 0; i < size; i++) {
        packet->payload[i] = (uint8_t)(i & 0xFF);
    }

    // Set arrival timestamp
    clock_gettime(CLOCK_MONOTONIC, &packet->arrival_time);

    return packet;
}

void destroy_packet(Packet *packet) {
    if (packet) {
        if (packet->payload) {
            free(packet->payload);
        }
        free(packet);
    }
}

void print_packet(const Packet *packet) {
    if (!packet) return;

    const char *priority_str[] = {"BG", "BE", "VIDEO", "VOICE"};

    printf("Packet ID: %u | Priority: %s | Size: %u bytes | MAC: %02X:%02X:%02X:%02X:%02X:%02X -> %02X:%02X:%02X:%02X:%02X:%02X\n",
           packet->packet_id,
           priority_str[packet->priority],
           packet->payload_size,
           packet->src_mac[0], packet->src_mac[1], packet->src_mac[2],
           packet->src_mac[3], packet->src_mac[4], packet->src_mac[5],
           packet->dst_mac[0], packet->dst_mac[1], packet->dst_mac[2],
           packet->dst_mac[3], packet->dst_mac[4], packet->dst_mac[5]);
}

double get_packet_age_ms(const Packet *packet) {
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);

    double age = (now.tv_sec - packet->arrival_time.tv_sec) * 1000.0;
    age += (now.tv_nsec - packet->arrival_time.tv_nsec) / 1000000.0;

    return age;
}
