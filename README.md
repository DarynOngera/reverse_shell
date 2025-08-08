# Encrypted Reverse Shell

This project provides a basic, encrypted reverse shell for educational and testing purposes. It consists of two main components: a `listener` script that runs on the attacker's machine and an `updater` script that runs on the target machine.

## Features

*   **Encrypted Communication:** All communication between the listener and the updater is encrypted using Fernet (AES-128 in CBC mode).
*   **Cross-Platform (with caveats):** The listener is platform-independent. The updater is designed for Windows and includes Windows-specific features like persistence.
*   **File Upload:** Upload files from the target machine to the listener.
*   **Screenshot Capture:** Take a screenshot of the target machine's desktop.
*   **Directory Navigation:** The `cd` command is implemented to allow navigation of the target's file system.
*   **Stealthy Execution:** The updater is compiled into a single executable with no console window, and the icon can be changed to disguise the file type.
*   **Traffic Blending:** The updater attempts to blend in with normal network traffic by making periodic requests to a legitimate website.

## Components

### `listener.py`

This script runs on the attacker's machine and waits for incoming connections from the updater. It provides a shell interface for sending commands to the target and receiving output.

### `updater.py`

This script runs on the target machine. It connects back to the listener, receives and executes commands, and sends back the results. It also includes features for persistence and evasion.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd reverse_shell
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Start the listener:**
    ```bash
    python3 listener.py
    ```
    The listener will start and print the AES key that will be used for communication.

2.  **Build the updater:**
    To build the updater executable for Windows, run the following command:
    ```bash
    make build-client
    ```
    This will create a single executable file in the `dist` directory.

3.  **Run the updater on the target machine:**
    Transfer the `updater.exe` file to the target Windows machine and execute it. The updater will connect back to the listener, and you will see a connection message in the listener's terminal.

4.  **Interact with the shell:**
    Once the connection is established, you can run commands in the listener's terminal. The following special commands are available:
    *   `screenshot`: Take a screenshot of the target's desktop.
    *   `upload:<file_path>`: Upload a file from the target to the listener.
    *   `cd <directory>`: Change the current working directory on the target.

## Makefile Targets

*   `install`: Install the required Python packages.
*   `clean`: Remove build artifacts.
*   `listener`: Start the listener script.
*   `client`: Run the updater script directly with Python (for testing).
*   `build-client`: Build the updater executable for Windows.
*   `run-client`: Run the updater script with specific host, port, and key arguments.

## Disclaimer

This tool is intended for educational and authorized testing purposes only. Unauthorized use of this tool on any system is illegal. The author is not responsible for any damage caused by the use of this tool.
