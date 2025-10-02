# WiFi Router Network Buffer Simulation

A low-level implementation of a network buffer for WiFi routers, providing hands-on learning experience with packet queuing, buffer management, and Quality of Service (QoS) mechanisms.

## Features

- **Circular Buffer Implementation**: Efficient ring buffer for packet storage
- **Priority Queue System**: 4-level QoS based on IEEE 802.11e standard
  - Voice (Highest priority)
  - Video
  - Best Effort
  - Background (Lowest priority)
- **Thread-Safe Operations**: Mutex-protected buffer operations
- **Realistic Packet Simulation**: Simulates WiFi frame structure with MAC addresses
- **Comprehensive Statistics**: Track throughput, latency, packet loss, and buffer utilization
- **Overflow Handling**: Configurable drop policies

## Architecture

### Components

1. **Packet Structure** (`packet.h/c`)
   - WiFi packet representation with MAC addresses
   - Priority levels for QoS
   - Timestamp tracking for latency measurement

2. **Network Buffer** (`network_buffer.h/c`)
   - Circular queue implementation
   - Priority-based scheduling
   - Buffer statistics and monitoring
   - Thread-safe operations

3. **Simulation Driver** (`simulation.c`)
   - Multi-threaded packet producer/consumer
   - Realistic packet generation
   - Real-time monitoring
   - Performance metrics

## Building

```bash
# Build the simulation
make

# Build and run
make run

# Clean build artifacts
make clean

# Rebuild from scratch
make rebuild
```

## Running the Simulation

```bash
./wifi_buffer_sim
```

The simulation will:
1. Create a network buffer with 1024 packet capacity
2. Start producer thread (generates packets every 5ms)
3. Start consumer thread (processes packets every 10ms)
4. Start monitor thread (prints stats every 2 seconds)
5. Run for 10 seconds (or until Ctrl+C)
6. Display final statistics

## Understanding the Output

### Real-time Monitoring
```
[MONITOR] Real-time statistics:
  Buffer size: 345 packets (33.7% utilization)
```

### Final Statistics
```
========== Network Buffer Statistics ==========
Total Capacity:       1024 packets
Current Size:         345 packets
Peak Size:            512 packets
Utilization:          33.69%

Packets Enqueued:     1234
Packets Dequeued:     889
Packets Dropped:      0 (0.00%)

Bytes Enqueued:       987654
Bytes Dequeued:       712340
Avg Queue Time:       12.345 ms

Queue Occupancy:
  Background: 45 / 128 (35.2%)
  Best Effort: 120 / 256 (46.9%)
  Video: 90 / 256 (35.2%)
  Voice: 90 / 384 (23.4%)
```

## Key Concepts

### Priority Scheduling
The buffer uses **strict priority scheduling**:
- Packets are dequeued from highest priority queue first
- Ensures low-latency for voice/video traffic
- Background traffic only processed when higher queues are empty

### Buffer Capacity Distribution
- Voice: 37.5% (highest allocation)
- Video: 25%
- Best Effort: 25%
- Background: 12.5% (lowest allocation)

### Packet Generation Distribution
- Voice: 20% (small packets, 100-300 bytes)
- Video: 30% (large packets, 500-1500 bytes)
- Best Effort: 40% (variable, 300-1500 bytes)
- Background: 10% (medium, 200-1000 bytes)

## Learning Objectives

This simulation demonstrates:
1. **Low-level buffer management** using circular queues
2. **QoS mechanisms** in network routers
3. **Producer-consumer pattern** with multiple threads
4. **Memory management** in C (malloc/free)
5. **Thread synchronization** using mutexes
6. **Performance monitoring** and statistics
7. **Overflow handling** and packet dropping policies
8. **Latency measurement** using timestamps

## Customization

Edit these parameters in `simulation.c`:
```c
#define SIMULATION_DURATION_SEC 10     // Simulation runtime
#define PACKET_ARRIVAL_RATE_MS 5       // Packet generation rate
#define PACKET_PROCESSING_RATE_MS 10   // Packet processing rate
#define MAX_PACKET_SIZE 1500           // Maximum packet size
```

## Requirements

- GCC compiler with C11 support
- POSIX threads (pthread) library
- macOS, Linux, or Unix-like system

## Project Structure

```
Network Buffer WIFI/
├── packet.h              # Packet structure definitions
├── packet.c              # Packet operations
├── network_buffer.h      # Buffer interface
├── network_buffer.c      # Buffer implementation
├── simulation.c          # Main simulation driver
├── Makefile             # Build configuration
└── README.md            # This file
```

## Future Enhancements

Potential improvements:
- Weighted Fair Queuing (WFQ) algorithm
- Token bucket rate limiting
- Dynamic buffer resizing
- Packet retransmission simulation
- Network congestion simulation
- Visual real-time graphs
- Configuration file support

## License

Educational project - free to use and modify.
