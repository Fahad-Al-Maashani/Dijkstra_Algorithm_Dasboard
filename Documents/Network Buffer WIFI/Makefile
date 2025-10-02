# Makefile for WiFi Network Buffer Simulation

CC = gcc
CFLAGS = -Wall -Wextra -O2 -pthread -std=c11
LDFLAGS = -pthread -lncurses

# Target executable
TARGET = wifi_buffer_sim

# Source files
SOURCES = packet.c network_buffer.c visualization.c simulation.c
OBJECTS = $(SOURCES:.c=.o)

# Header files
HEADERS = packet.h network_buffer.h visualization.h

# Default target
all: $(TARGET)

# Build the executable
$(TARGET): $(OBJECTS)
	@echo "Linking $(TARGET)..."
	$(CC) $(LDFLAGS) -o $@ $^
	@echo "Build complete!"

# Compile source files
%.o: %.c $(HEADERS)
	@echo "Compiling $<..."
	$(CC) $(CFLAGS) -c $< -o $@

# Run the simulation
run: $(TARGET)
	@echo "Running simulation..."
	./$(TARGET)

# Clean build artifacts
clean:
	@echo "Cleaning build files..."
	rm -f $(OBJECTS) $(TARGET)
	@echo "Clean complete!"

# Rebuild everything
rebuild: clean all

# Help target
help:
	@echo "WiFi Network Buffer Simulation - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all      - Build the simulation (default)"
	@echo "  run      - Build and run the simulation"
	@echo "  clean    - Remove build artifacts"
	@echo "  rebuild  - Clean and rebuild everything"
	@echo "  help     - Show this help message"

.PHONY: all run clean rebuild help
