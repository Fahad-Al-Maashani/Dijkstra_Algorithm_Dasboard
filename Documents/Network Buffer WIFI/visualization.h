#ifndef VISUALIZATION_H
#define VISUALIZATION_H

#include "network_buffer.h"
#include <ncurses.h>
#include <stdbool.h>

// Graph configuration
#define GRAPH_WIDTH 100
#define GRAPH_HEIGHT 18
#define HISTORY_SIZE 100
#define UPDATE_INTERVAL_MS 200

// Graph data structure
typedef struct {
    uint32_t buffer_history[HISTORY_SIZE];
    double utilization_history[HISTORY_SIZE];
    uint64_t enqueued_last;
    uint64_t dequeued_last;
    uint64_t dropped_last;
    int history_index;
    uint32_t max_buffer_seen;
} GraphData;

// Visualization context
typedef struct {
    WINDOW *header_win;
    WINDOW *buffer_graph_win;
    WINDOW *stats_win;
    WINDOW *priority_win;
    WINDOW *legend_win;
    GraphData data;
    bool initialized;
    time_t start_time;
} VisualizationContext;

// Function prototypes
VisualizationContext* init_visualization(void);
void cleanup_visualization(VisualizationContext *ctx);

// Graph updates
void update_graphs(VisualizationContext *ctx, NetworkBuffer *buffer);
void draw_header(VisualizationContext *ctx);
void draw_buffer_graph(VisualizationContext *ctx);
void draw_stats_panel(VisualizationContext *ctx, NetworkBuffer *buffer);
void draw_priority_queues(VisualizationContext *ctx, NetworkBuffer *buffer);
void draw_legend(VisualizationContext *ctx);

#endif // VISUALIZATION_H
