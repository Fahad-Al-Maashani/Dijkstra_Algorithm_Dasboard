#ifndef PACKET_H
#define PACKET_H

#include <stdint.h>
#include <time.h>

// WiFi packet priorities (802.11e QoS)
typedef enum {
    PRIORITY_BACKGROUND = 0,  // Background traffic
    PRIORITY_BEST_EFFORT = 1, // Normal traffic
    PRIORITY_VIDEO = 2,       // Video streaming
    PRIORITY_VOICE = 3        // Voice/VoIP (highest priority)
} PacketPriority;

// Packet structure simulating WiFi frame
typedef struct {
    uint32_t packet_id;           // Unique packet identifier
    uint8_t src_mac[6];           // Source MAC address
    uint8_t dst_mac[6];           // Destination MAC address
    uint16_t payload_size;        // Payload size in bytes
    PacketPriority priority;      // QoS priority
    struct timespec arrival_time; // Timestamp when packet arrived
    uint8_t *payload;             // Actual payload data
    uint8_t retries;              // Number of retransmission attempts
} Packet;

// Function prototypes
Packet* create_packet(uint32_t id, const uint8_t *src, const uint8_t *dst,
                     uint16_t size, PacketPriority priority);
void destroy_packet(Packet *packet);
void print_packet(const Packet *packet);
double get_packet_age_ms(const Packet *packet);

#endif // PACKET_H
