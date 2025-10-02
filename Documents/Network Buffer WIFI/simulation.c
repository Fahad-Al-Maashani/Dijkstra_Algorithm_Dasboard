#include "network_buffer.h"
#include "visualization.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <signal.h>

// Simulation parameters
#define SIMULATION_DURATION_SEC 10
#define PACKET_ARRIVAL_RATE_MS 5      // New packet every 5ms
#define PACKET_PROCESSING_RATE_MS 10  // Process packet every 10ms
#define MAX_PACKET_SIZE 1500          // Maximum packet size (MTU)

// Global variables
static volatile bool running = true;
static NetworkBuffer *global_buffer = NULL;
static VisualizationContext *global_viz = NULL;
static uint32_t next_packet_id = 1;

// Signal handler for graceful shutdown
void signal_handler(int signum) {
    running = false;
    if (global_viz) {
        cleanup_visualization(global_viz);
        global_viz = NULL;
    }
    printf("\n\nReceived signal %d. Shutting down simulation...\n", signum);
}

// Generate random MAC address
void generate_random_mac(uint8_t *mac) {
    for (int i = 0; i < 6; i++) {
        mac[i] = rand() % 256;
    }
}

// Generate random packet with realistic distribution
Packet* generate_random_packet(void) {
    uint8_t src_mac[6], dst_mac[6];
    generate_random_mac(src_mac);
    generate_random_mac(dst_mac);

    // Generate packet with weighted priority distribution
    // Voice: 20%, Video: 30%, Best Effort: 40%, Background: 10%
    int priority_rand = rand() % 100;
    PacketPriority priority;

    if (priority_rand < 10) {
        priority = PRIORITY_BACKGROUND;
    } else if (priority_rand < 50) {
        priority = PRIORITY_BEST_EFFORT;
    } else if (priority_rand < 80) {
        priority = PRIORITY_VIDEO;
    } else {
        priority = PRIORITY_VOICE;
    }

    // Generate packet size based on priority
    uint16_t size;
    switch (priority) {
        case PRIORITY_VOICE:
            size = 100 + rand() % 200;  // Small voice packets (100-300 bytes)
            break;
        case PRIORITY_VIDEO:
            size = 500 + rand() % 1000; // Large video packets (500-1500 bytes)
            break;
        case PRIORITY_BEST_EFFORT:
            size = 300 + rand() % 1200; // Variable size (300-1500 bytes)
            break;
        case PRIORITY_BACKGROUND:
            size = 200 + rand() % 800;  // Medium size (200-1000 bytes)
            break;
        default:
            size = 500;
    }

    return create_packet(next_packet_id++, src_mac, dst_mac, size, priority);
}

// Producer thread - simulates incoming packets
void* packet_producer(void *arg) {
    NetworkBuffer *buffer = (NetworkBuffer*)arg;
    uint32_t packets_generated = 0;

    printf("[PRODUCER] Started - generating packets every %d ms\n", PACKET_ARRIVAL_RATE_MS);

    while (running) {
        Packet *packet = generate_random_packet();

        if (packet) {
            bool success = enqueue_packet(buffer, packet);

            if (!success) {
                printf("[PRODUCER] WARNING: Packet %u dropped (buffer full)\n", packet->packet_id);
            }

            packets_generated++;
        }

        usleep(PACKET_ARRIVAL_RATE_MS * 1000);
    }

    printf("[PRODUCER] Stopped - generated %u packets\n", packets_generated);
    return NULL;
}

// Consumer thread - simulates packet processing/transmission
void* packet_consumer(void *arg) {
    NetworkBuffer *buffer = (NetworkBuffer*)arg;
    uint32_t packets_processed = 0;

    printf("[CONSUMER] Started - processing packets every %d ms\n", PACKET_PROCESSING_RATE_MS);

    while (running) {
        Packet *packet = dequeue_packet(buffer);

        if (packet) {
            packets_processed++;

            // Simulate packet transmission
            double queue_time = get_packet_age_ms(packet);

            if (packets_processed % 100 == 0) {
                printf("[CONSUMER] Processed packet %u (queued for %.2f ms)\n",
                       packet->packet_id, queue_time);
            }

            destroy_packet(packet);
        }

        usleep(PACKET_PROCESSING_RATE_MS * 1000);
    }

    printf("[CONSUMER] Stopped - processed %u packets\n", packets_processed);
    return NULL;
}

// Visualization thread - updates graphs in real-time
void* visualization_thread(void *arg) {
    NetworkBuffer *buffer = (NetworkBuffer*)arg;

    while (running) {
        if (global_viz) {
            update_graphs(global_viz, buffer);
        }
        usleep(UPDATE_INTERVAL_MS * 1000);
    }

    return NULL;
}

int main(void) {
    printf("=================================================\n");
    printf("  WiFi Router Network Buffer Simulation\n");
    printf("=================================================\n\n");

    // Set up signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    // Seed random number generator
    srand(time(NULL));

    // Create network buffer (1024 packets capacity, drop on overflow)
    global_buffer = create_network_buffer(1024, true);
    if (!global_buffer) {
        fprintf(stderr, "Failed to create network buffer\n");
        return 1;
    }

    printf("Network buffer created:\n");
    printf("  Total capacity: 1024 packets\n");
    printf("  Priority queues: 4 (Voice, Video, Best Effort, Background)\n");
    printf("  Drop policy: Drop on overflow\n\n");

    // Initialize visualization
    printf("Initializing real-time visualization...\n");
    sleep(1); // Brief pause before starting ncurses
    global_viz = init_visualization();
    if (!global_viz) {
        fprintf(stderr, "Failed to initialize visualization\n");
        destroy_network_buffer(global_buffer);
        return 1;
    }

    // Create threads
    pthread_t producer_thread, consumer_thread, viz_thread;

    pthread_create(&producer_thread, NULL, packet_producer, global_buffer);
    pthread_create(&consumer_thread, NULL, packet_consumer, global_buffer);
    pthread_create(&viz_thread, NULL, visualization_thread, global_buffer);

    // Run simulation
    sleep(SIMULATION_DURATION_SEC);
    running = false;

    // Wait for threads to finish
    pthread_join(producer_thread, NULL);
    pthread_join(consumer_thread, NULL);
    pthread_join(viz_thread, NULL);

    // Cleanup visualization
    if (global_viz) {
        cleanup_visualization(global_viz);
        global_viz = NULL;
    }

    // Print final statistics
    printf("\n=================================================\n");
    printf("  Simulation Complete - Final Results\n");
    printf("=================================================\n");
    print_buffer_stats(global_buffer);

    // Cleanup
    destroy_network_buffer(global_buffer);

    printf("Simulation ended successfully.\n");
    return 0;
}
