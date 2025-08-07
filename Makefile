# Makefile for Reverse Shell

# Variables
HOST ?= 127.0.0.1
PORT ?= 4444
KEY ?= mykey

# Phony targets
.PHONY: all clean listener client build-client

all: listener

# Target: install - Install dependencies
install:
	pip install -r requirements.txt

# Target: clean - Clean up build files
clean:
	rm -rf build dist
	rm -f client.spec

# Target: listener - Run the listener
listener:
	python3 listener.py

# Target: client - Run the client (for testing)
client:
	python3 client.py

# Target: build-client - Build the client executable for Windows
build-client:
	pyinstaller --onefile --windowed --name client client.py

# Target: run-client - Run the client with specific host, port, and key
run-client:
	python3 client.py --host $(HOST) --port $(PORT) --key $(KEY)
