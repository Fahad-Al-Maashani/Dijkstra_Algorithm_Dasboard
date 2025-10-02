#ifndef NETWORK_BUFFER_H
#define NETWORK_BUFFER_H

#include "packet.h"
#include <stdbool.h>
#include <pthread.h>

// Buffer configuration
#define MAX_BUFFER_SIZE 1024
#define NUM_PRIORITY_QUEUES 4

// Buffer statistics
typedef struct {
    uint64_t total_enqueued;      // Total packets enqueued
    uint64_t total_dequeued;      // Total packets dequeued
    uint64_t total_dropped;       // Packets dropped due to overflow
    uint64_t bytes_enqueued;      // Total bytes enqueued
    uint64_t bytes_dequeued;      // Total bytes dequeued
    double avg_queue_time_ms;     // Average time packets spend in queue
    uint32_t current_size;        // Current number of packets in buffer
    uint32_t peak_size;           // Maximum buffer occupancy reached
} BufferStats;

// Circular buffer for each priority queue
typedef struct {
    Packet **packets;             // Array of packet pointers
    uint32_t head;                // Head index (dequeue position)
    uint32_t tail;                // Tail index (enqueue position)
    uint32_t count;               // Number of packets in queue
    uint32_t capacity;            // Maximum capacity
} CircularQueue;

// Network buffer with priority queues
typedef struct {
    CircularQueue queues[NUM_PRIORITY_QUEUES];  // One queue per priority
    BufferStats stats;                          // Buffer statistics
    pthread_mutex_t mutex;                      // Thread safety
    uint32_t total_capacity;                    // Total buffer capacity
    bool drop_on_overflow;                      // Drop policy
} NetworkBuffer;

// Function prototypes
NetworkBuffer* create_network_buffer(uint32_t capacity, bool drop_on_overflow);
void destroy_network_buffer(NetworkBuffer *buffer);

// Buffer operations
bool enqueue_packet(NetworkBuffer *buffer, Packet *packet);
Packet* dequeue_packet(NetworkBuffer *buffer);
Packet* peek_packet(NetworkBuffer *buffer);

// Buffer management
void flush_buffer(NetworkBuffer *buffer);
uint32_t get_buffer_size(NetworkBuffer *buffer);
bool is_buffer_empty(NetworkBuffer *buffer);
bool is_buffer_full(NetworkBuffer *buffer);

// Statistics
void print_buffer_stats(NetworkBuffer *buffer);
void reset_buffer_stats(NetworkBuffer *buffer);
double get_buffer_utilization(NetworkBuffer *buffer);

#endif // NETWORK_BUFFER_H
