#include "visualization.h"
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

// Initialize ncurses and create beautiful layout
VisualizationContext* init_visualization(void) {
    VisualizationContext *ctx = (VisualizationContext*)malloc(sizeof(VisualizationContext));
    if (!ctx) return NULL;

    memset(ctx, 0, sizeof(VisualizationContext));
    ctx->start_time = time(NULL);

    // Initialize ncurses
    initscr();
    cbreak();
    noecho();
    curs_set(0);
    nodelay(stdscr, TRUE);

    // Initialize colors
    if (has_colors()) {
        start_color();
        use_default_colors();

        // Define color pairs
        init_pair(1, COLOR_GREEN, -1);      // Success/Normal
        init_pair(2, COLOR_YELLOW, -1);     // Warning
        init_pair(3, COLOR_RED, -1);        // Critical/Error
        init_pair(4, COLOR_CYAN, -1);       // Info/Headers
        init_pair(5, COLOR_MAGENTA, -1);    // Voice
        init_pair(6, COLOR_BLUE, -1);       // Video
        init_pair(7, COLOR_WHITE, -1);      // Best Effort
        init_pair(8, COLOR_BLACK, COLOR_GREEN);   // Bright backgrounds
        init_pair(9, COLOR_BLACK, COLOR_YELLOW);
        init_pair(10, COLOR_BLACK, COLOR_RED);
    }

    // Get screen dimensions
    int max_y, max_x;
    getmaxyx(stdscr, max_y, max_x);

    // Create windows with better spacing
    int y_pos = 0;

    // Header (3 lines)
    ctx->header_win = newwin(3, max_x, y_pos, 0);
    y_pos += 3;

    // Buffer graph (main visualization - 22 lines)
    ctx->buffer_graph_win = newwin(22, max_x, y_pos, 0);
    y_pos += 22;

    // Stats panel (7 lines)
    ctx->stats_win = newwin(7, max_x / 2, y_pos, 0);

    // Priority queues (7 lines)
    ctx->priority_win = newwin(7, max_x / 2, y_pos, max_x / 2);
    y_pos += 7;

    // Legend (4 lines)
    ctx->legend_win = newwin(4, max_x, y_pos, 0);

    ctx->initialized = true;

    // Initial draw
    draw_header(ctx);
    draw_legend(ctx);

    refresh();
    return ctx;
}

// Cleanup visualization
void cleanup_visualization(VisualizationContext *ctx) {
    if (!ctx) return;

    if (ctx->initialized) {
        if (ctx->header_win) delwin(ctx->header_win);
        if (ctx->buffer_graph_win) delwin(ctx->buffer_graph_win);
        if (ctx->stats_win) delwin(ctx->stats_win);
        if (ctx->priority_win) delwin(ctx->priority_win);
        if (ctx->legend_win) delwin(ctx->legend_win);
        endwin();
    }

    free(ctx);
}

// Draw header with title and runtime
void draw_header(VisualizationContext *ctx) {
    if (!ctx || !ctx->header_win) return;

    WINDOW *win = ctx->header_win;
    werase(win);

    // Draw double-line border
    wattron(win, COLOR_PAIR(4) | A_BOLD);
    box(win, 0, 0);

    // Title
    int max_x = getmaxx(win);
    const char *title = "WiFi NETWORK BUFFER SIMULATION - REAL-TIME MONITORING";
    mvwprintw(win, 1, (max_x - strlen(title)) / 2, "%s", title);

    // Runtime
    time_t now = time(NULL);
    int runtime = (int)difftime(now, ctx->start_time);
    mvwprintw(win, 1, max_x - 20, "Runtime: %02d:%02d", runtime / 60, runtime % 60);

    wattroff(win, COLOR_PAIR(4) | A_BOLD);
    wrefresh(win);
}

// Draw beautiful buffer utilization graph
void draw_buffer_graph(VisualizationContext *ctx) {
    if (!ctx || !ctx->buffer_graph_win) return;

    WINDOW *win = ctx->buffer_graph_win;
    werase(win);

    wattron(win, COLOR_PAIR(4));
    box(win, 0, 0);
    wattroff(win, COLOR_PAIR(4));

    // Title
    wattron(win, COLOR_PAIR(4) | A_BOLD);
    mvwprintw(win, 0, 3, "[ BUFFER UTILIZATION - LIVE GRAPH ]");
    wattroff(win, COLOR_PAIR(4) | A_BOLD);

    // Find max value for proper scaling
    uint32_t max_val = ctx->data.max_buffer_seen;
    if (max_val == 0) max_val = 100;

    // Draw Y-axis labels
    wattron(win, COLOR_PAIR(7) | A_DIM);
    mvwprintw(win, 2, 2, "%4u", max_val);
    mvwprintw(win, 2 + GRAPH_HEIGHT / 2, 2, "%4u", max_val / 2);
    mvwprintw(win, 2 + GRAPH_HEIGHT, 2, "   0");
    mvwprintw(win, 2 + GRAPH_HEIGHT / 4, 2, "%4u", (max_val * 3) / 4);
    mvwprintw(win, 2 + (GRAPH_HEIGHT * 3) / 4, 2, "%4u", max_val / 4);

    // Y-axis line
    for (int y = 2; y <= 2 + GRAPH_HEIGHT; y++) {
        mvwprintw(win, y, 7, "|");
    }
    wattroff(win, COLOR_PAIR(7) | A_DIM);

    // Draw graph area with grid
    wattron(win, A_DIM);
    for (int y = 2; y <= 2 + GRAPH_HEIGHT; y += GRAPH_HEIGHT / 4) {
        for (int x = 8; x < 8 + GRAPH_WIDTH; x += 10) {
            mvwprintw(win, y, x, ".");
        }
    }
    wattroff(win, A_DIM);

    // Draw the actual graph
    for (int x = 0; x < HISTORY_SIZE && x < GRAPH_WIDTH; x++) {
        int idx = (ctx->data.history_index + x) % HISTORY_SIZE;
        uint32_t value = ctx->data.buffer_history[idx];
        double util = ctx->data.utilization_history[idx];

        if (max_val > 0) {
            int height = (value * GRAPH_HEIGHT) / max_val;

            // Choose color based on utilization
            int color = 1; // Green
            const char *symbol = "#";

            if (util >= 90.0) {
                color = 3; // Red
                symbol = "#";
            } else if (util >= 70.0) {
                color = 2; // Yellow
                symbol = "#";
            } else if (util >= 50.0) {
                color = 2; // Yellow
                symbol = ":";
            } else if (util >= 30.0) {
                color = 1; // Green
                symbol = ".";
            } else {
                color = 1; // Green
                symbol = ".";
            }

            // Draw vertical bar from bottom up
            wattron(win, COLOR_PAIR(color) | A_BOLD);
            for (int y = 0; y < height && y < GRAPH_HEIGHT; y++) {
                mvwprintw(win, 2 + GRAPH_HEIGHT - y, 8 + x, "%s", symbol);
            }
            wattroff(win, COLOR_PAIR(color) | A_BOLD);
        }
    }

    // X-axis
    wattron(win, COLOR_PAIR(7) | A_DIM);
    mvwprintw(win, 2 + GRAPH_HEIGHT + 1, 7, "+");
    for (int x = 0; x < GRAPH_WIDTH; x++) {
        mvwprintw(win, 2 + GRAPH_HEIGHT + 1, 8 + x, "-");
    }
    mvwprintw(win, 2 + GRAPH_HEIGHT + 1, 20, "< Time (older)");
    mvwprintw(win, 2 + GRAPH_HEIGHT + 1, GRAPH_WIDTH - 20, "(newer) >");
    wattroff(win, COLOR_PAIR(7) | A_DIM);

    wrefresh(win);
}

// Draw statistics panel
void draw_stats_panel(VisualizationContext *ctx, NetworkBuffer *buffer) {
    if (!ctx || !ctx->stats_win || !buffer) return;

    WINDOW *win = ctx->stats_win;
    werase(win);

    wattron(win, COLOR_PAIR(4));
    box(win, 0, 0);
    wattroff(win, COLOR_PAIR(4));

    // Title
    wattron(win, COLOR_PAIR(4) | A_BOLD);
    mvwprintw(win, 0, 2, "[ STATISTICS ]");
    wattroff(win, COLOR_PAIR(4) | A_BOLD);

    // Get stats
    uint32_t current_size = get_buffer_size(buffer);
    double utilization = get_buffer_utilization(buffer);

    // Current buffer size
    wattron(win, A_BOLD);
    mvwprintw(win, 2, 2, "Buffer Size:");
    wattroff(win, A_BOLD);

    int color = 1;
    if (utilization >= 90.0) color = 3;
    else if (utilization >= 70.0) color = 2;

    wattron(win, COLOR_PAIR(color) | A_BOLD);
    mvwprintw(win, 2, 16, "%u packets", current_size);
    wattroff(win, COLOR_PAIR(color) | A_BOLD);

    // Utilization percentage
    wattron(win, A_BOLD);
    mvwprintw(win, 3, 2, "Utilization:");
    wattroff(win, A_BOLD);

    wattron(win, COLOR_PAIR(color) | A_BOLD);
    mvwprintw(win, 3, 16, "%.1f%%", utilization);

    // Visual bar
    int bar_length = 25;
    int filled = (int)(utilization * bar_length / 100.0);
    mvwprintw(win, 4, 2, "[");
    for (int i = 0; i < bar_length; i++) {
        if (i < filled) {
            mvwprintw(win, 4, 3 + i, "=");
        } else {
            wattron(win, A_DIM);
            mvwprintw(win, 4, 3 + i, "-");
            wattroff(win, A_DIM);
        }
    }
    mvwprintw(win, 4, 3 + bar_length, "]");
    wattroff(win, COLOR_PAIR(color) | A_BOLD);

    // Peak size
    wattron(win, A_DIM);
    mvwprintw(win, 5, 2, "Peak: %u packets", ctx->data.max_buffer_seen);
    wattroff(win, A_DIM);

    wrefresh(win);
}

// Draw priority queue visualization
void draw_priority_queues(VisualizationContext *ctx, NetworkBuffer *buffer) {
    if (!ctx || !ctx->priority_win || !buffer) return;

    WINDOW *win = ctx->priority_win;
    werase(win);

    wattron(win, COLOR_PAIR(4));
    box(win, 0, 0);
    wattroff(win, COLOR_PAIR(4));

    // Title
    wattron(win, COLOR_PAIR(4) | A_BOLD);
    mvwprintw(win, 0, 2, "[ PRIORITY QUEUES ]");
    wattroff(win, COLOR_PAIR(4) | A_BOLD);

    const char *queue_names[] = {"Voice", "Video", "Best Effort", "Background"};
    int colors[] = {5, 6, 7, 3};

    for (int i = 0; i < 4; i++) {
        int y = 2 + i;

        // Queue name with color
        wattron(win, COLOR_PAIR(colors[i]) | A_BOLD);
        mvwprintw(win, y, 2, "%-12s", queue_names[i]);
        wattroff(win, COLOR_PAIR(colors[i]) | A_BOLD);

        // Simple visual indicator (bar)
        wattron(win, COLOR_PAIR(colors[i]));
        int bar_size = 20;
        mvwprintw(win, y, 15, "[");
        for (int j = 0; j < bar_size; j++) {
            mvwprintw(win, y, 16 + j, "=");
        }
        mvwprintw(win, y, 16 + bar_size, "]");
        wattroff(win, COLOR_PAIR(colors[i]));
    }

    wrefresh(win);
}

// Draw legend
void draw_legend(VisualizationContext *ctx) {
    if (!ctx || !ctx->legend_win) return;

    WINDOW *win = ctx->legend_win;
    werase(win);

    wattron(win, COLOR_PAIR(4));
    box(win, 0, 0);
    wattroff(win, COLOR_PAIR(4));

    wattron(win, COLOR_PAIR(4) | A_BOLD);
    mvwprintw(win, 0, 2, "[ LEGEND ]");
    wattroff(win, COLOR_PAIR(4) | A_BOLD);

    int x_pos = 3;

    // Green indicator
    wattron(win, COLOR_PAIR(1) | A_BOLD);
    mvwprintw(win, 1, x_pos, "#");
    wattroff(win, COLOR_PAIR(1) | A_BOLD);
    mvwprintw(win, 1, x_pos + 2, "Normal (<50%%)");
    x_pos += 20;

    // Yellow indicator
    wattron(win, COLOR_PAIR(2) | A_BOLD);
    mvwprintw(win, 1, x_pos, "#");
    wattroff(win, COLOR_PAIR(2) | A_BOLD);
    mvwprintw(win, 1, x_pos + 2, "Warning (50-90%%)");
    x_pos += 25;

    // Red indicator
    wattron(win, COLOR_PAIR(3) | A_BOLD);
    mvwprintw(win, 1, x_pos, "#");
    wattroff(win, COLOR_PAIR(3) | A_BOLD);
    mvwprintw(win, 1, x_pos + 2, "Critical (>90%%)");
    x_pos += 25;

    // Instructions
    wattron(win, A_DIM);
    mvwprintw(win, 2, 3, "Press Ctrl+C to stop simulation");
    wattroff(win, A_DIM);

    wrefresh(win);
}

// Update all graphs
void update_graphs(VisualizationContext *ctx, NetworkBuffer *buffer) {
    if (!ctx || !buffer) return;

    // Get current stats
    uint32_t current_size = get_buffer_size(buffer);
    double utilization = get_buffer_utilization(buffer);

    // Update max seen
    if (current_size > ctx->data.max_buffer_seen) {
        ctx->data.max_buffer_seen = current_size;
    }

    // Update history
    ctx->data.buffer_history[ctx->data.history_index] = current_size;
    ctx->data.utilization_history[ctx->data.history_index] = utilization;
    ctx->data.history_index = (ctx->data.history_index + 1) % HISTORY_SIZE;

    // Redraw all components
    draw_header(ctx);
    draw_buffer_graph(ctx);
    draw_stats_panel(ctx, buffer);
    draw_priority_queues(ctx, buffer);

    // Refresh
    doupdate();
}
