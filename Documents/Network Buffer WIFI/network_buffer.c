#include "network_buffer.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// Initialize a circular queue
static bool init_circular_queue(CircularQueue *queue, uint32_t capacity) {
    queue->packets = (Packet**)calloc(capacity, sizeof(Packet*));
    if (!queue->packets) return false;

    queue->head = 0;
    queue->tail = 0;
    queue->count = 0;
    queue->capacity = capacity;
    return true;
}

// Destroy a circular queue
static void destroy_circular_queue(CircularQueue *queue) {
    if (queue->packets) {
        // Free any remaining packets
        for (uint32_t i = 0; i < queue->count; i++) {
            uint32_t idx = (queue->head + i) % queue->capacity;
            if (queue->packets[idx]) {
                destroy_packet(queue->packets[idx]);
            }
        }
        free(queue->packets);
        queue->packets = NULL;
    }
}

// Enqueue to circular queue
static bool circular_queue_enqueue(CircularQueue *queue, Packet *packet) {
    if (queue->count >= queue->capacity) {
        return false; // Queue full
    }

    queue->packets[queue->tail] = packet;
    queue->tail = (queue->tail + 1) % queue->capacity;
    queue->count++;
    return true;
}

// Dequeue from circular queue
static Packet* circular_queue_dequeue(CircularQueue *queue) {
    if (queue->count == 0) {
        return NULL; // Queue empty
    }

    Packet *packet = queue->packets[queue->head];
    queue->packets[queue->head] = NULL;
    queue->head = (queue->head + 1) % queue->capacity;
    queue->count--;
    return packet;
}

// Peek at front of circular queue
static Packet* circular_queue_peek(CircularQueue *queue) {
    if (queue->count == 0) {
        return NULL;
    }
    return queue->packets[queue->head];
}

NetworkBuffer* create_network_buffer(uint32_t capacity, bool drop_on_overflow) {
    NetworkBuffer *buffer = (NetworkBuffer*)malloc(sizeof(NetworkBuffer));
    if (!buffer) return NULL;

    // Distribute capacity among priority queues
    // Higher priority queues get more space
    uint32_t capacities[NUM_PRIORITY_QUEUES] = {
        capacity / 8,      // Background: 12.5%
        capacity / 4,      // Best effort: 25%
        capacity / 4,      // Video: 25%
        capacity * 3 / 8   // Voice: 37.5%
    };

    // Initialize priority queues
    for (int i = 0; i < NUM_PRIORITY_QUEUES; i++) {
        if (!init_circular_queue(&buffer->queues[i], capacities[i])) {
            // Cleanup on failure
            for (int j = 0; j < i; j++) {
                destroy_circular_queue(&buffer->queues[j]);
            }
            free(buffer);
            return NULL;
        }
    }

    // Initialize statistics
    memset(&buffer->stats, 0, sizeof(BufferStats));

    // Initialize mutex
    pthread_mutex_init(&buffer->mutex, NULL);

    buffer->total_capacity = capacity;
    buffer->drop_on_overflow = drop_on_overflow;

    return buffer;
}

void destroy_network_buffer(NetworkBuffer *buffer) {
    if (!buffer) return;

    pthread_mutex_lock(&buffer->mutex);

    // Destroy all priority queues
    for (int i = 0; i < NUM_PRIORITY_QUEUES; i++) {
        destroy_circular_queue(&buffer->queues[i]);
    }

    pthread_mutex_unlock(&buffer->mutex);
    pthread_mutex_destroy(&buffer->mutex);

    free(buffer);
}

bool enqueue_packet(NetworkBuffer *buffer, Packet *packet) {
    if (!buffer || !packet) return false;

    pthread_mutex_lock(&buffer->mutex);

    // Get the appropriate queue based on priority
    CircularQueue *queue = &buffer->queues[packet->priority];

    bool success = circular_queue_enqueue(queue, packet);

    if (success) {
        buffer->stats.total_enqueued++;
        buffer->stats.bytes_enqueued += packet->payload_size;
        buffer->stats.current_size++;

        if (buffer->stats.current_size > buffer->stats.peak_size) {
            buffer->stats.peak_size = buffer->stats.current_size;
        }
    } else {
        // Buffer overflow
        buffer->stats.total_dropped++;

        if (buffer->drop_on_overflow) {
            destroy_packet(packet);
        }
    }

    pthread_mutex_unlock(&buffer->mutex);
    return success;
}

Packet* dequeue_packet(NetworkBuffer *buffer) {
    if (!buffer) return NULL;

    pthread_mutex_lock(&buffer->mutex);

    Packet *packet = NULL;

    // Dequeue from highest priority queue first (strict priority scheduling)
    for (int i = NUM_PRIORITY_QUEUES - 1; i >= 0; i--) {
        packet = circular_queue_dequeue(&buffer->queues[i]);
        if (packet) {
            buffer->stats.total_dequeued++;
            buffer->stats.bytes_dequeued += packet->payload_size;
            buffer->stats.current_size--;

            // Update average queue time
            double queue_time = get_packet_age_ms(packet);
            buffer->stats.avg_queue_time_ms =
                (buffer->stats.avg_queue_time_ms * (buffer->stats.total_dequeued - 1) + queue_time) /
                buffer->stats.total_dequeued;

            break;
        }
    }

    pthread_mutex_unlock(&buffer->mutex);
    return packet;
}

Packet* peek_packet(NetworkBuffer *buffer) {
    if (!buffer) return NULL;

    pthread_mutex_lock(&buffer->mutex);

    Packet *packet = NULL;

    // Peek at highest priority queue
    for (int i = NUM_PRIORITY_QUEUES - 1; i >= 0; i--) {
        packet = circular_queue_peek(&buffer->queues[i]);
        if (packet) break;
    }

    pthread_mutex_unlock(&buffer->mutex);
    return packet;
}

void flush_buffer(NetworkBuffer *buffer) {
    if (!buffer) return;

    pthread_mutex_lock(&buffer->mutex);

    for (int i = 0; i < NUM_PRIORITY_QUEUES; i++) {
        CircularQueue *queue = &buffer->queues[i];

        while (queue->count > 0) {
            Packet *packet = circular_queue_dequeue(queue);
            if (packet) {
                destroy_packet(packet);
            }
        }
    }

    buffer->stats.current_size = 0;

    pthread_mutex_unlock(&buffer->mutex);
}

uint32_t get_buffer_size(NetworkBuffer *buffer) {
    if (!buffer) return 0;

    pthread_mutex_lock(&buffer->mutex);
    uint32_t size = buffer->stats.current_size;
    pthread_mutex_unlock(&buffer->mutex);

    return size;
}

bool is_buffer_empty(NetworkBuffer *buffer) {
    return get_buffer_size(buffer) == 0;
}

bool is_buffer_full(NetworkBuffer *buffer) {
    if (!buffer) return true;

    pthread_mutex_lock(&buffer->mutex);

    // Check if all queues are full
    bool full = true;
    for (int i = 0; i < NUM_PRIORITY_QUEUES; i++) {
        if (buffer->queues[i].count < buffer->queues[i].capacity) {
            full = false;
            break;
        }
    }

    pthread_mutex_unlock(&buffer->mutex);
    return full;
}

void print_buffer_stats(NetworkBuffer *buffer) {
    if (!buffer) return;

    pthread_mutex_lock(&buffer->mutex);

    printf("\n========== Network Buffer Statistics ==========\n");
    printf("Total Capacity:       %u packets\n", buffer->total_capacity);
    printf("Current Size:         %u packets\n", buffer->stats.current_size);
    printf("Peak Size:            %u packets\n", buffer->stats.peak_size);
    printf("Utilization:          %.2f%%\n", get_buffer_utilization(buffer));
    printf("\n");
    printf("Packets Enqueued:     %llu\n", (unsigned long long)buffer->stats.total_enqueued);
    printf("Packets Dequeued:     %llu\n", (unsigned long long)buffer->stats.total_dequeued);
    printf("Packets Dropped:      %llu (%.2f%%)\n",
           (unsigned long long)buffer->stats.total_dropped,
           buffer->stats.total_enqueued > 0 ?
           (100.0 * buffer->stats.total_dropped) / (buffer->stats.total_enqueued + buffer->stats.total_dropped) : 0);
    printf("\n");
    printf("Bytes Enqueued:       %llu\n", (unsigned long long)buffer->stats.bytes_enqueued);
    printf("Bytes Dequeued:       %llu\n", (unsigned long long)buffer->stats.bytes_dequeued);
    printf("Avg Queue Time:       %.3f ms\n", buffer->stats.avg_queue_time_ms);
    printf("\n");

    // Per-queue statistics
    const char *priority_names[] = {"Background", "Best Effort", "Video", "Voice"};
    printf("Queue Occupancy:\n");
    for (int i = 0; i < NUM_PRIORITY_QUEUES; i++) {
        printf("  %s: %u / %u (%.1f%%)\n",
               priority_names[i],
               buffer->queues[i].count,
               buffer->queues[i].capacity,
               (100.0 * buffer->queues[i].count) / buffer->queues[i].capacity);
    }
    printf("==============================================\n\n");

    pthread_mutex_unlock(&buffer->mutex);
}

void reset_buffer_stats(NetworkBuffer *buffer) {
    if (!buffer) return;

    pthread_mutex_lock(&buffer->mutex);
    memset(&buffer->stats, 0, sizeof(BufferStats));
    buffer->stats.current_size = get_buffer_size(buffer);
    pthread_mutex_unlock(&buffer->mutex);
}

double get_buffer_utilization(NetworkBuffer *buffer) {
    if (!buffer || buffer->total_capacity == 0) return 0.0;

    return (100.0 * buffer->stats.current_size) / buffer->total_capacity;
}
