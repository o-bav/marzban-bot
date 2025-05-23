# SHM Integrated Telegram Bot

## Overview

This Telegram bot provides an interface to interact with a Server Hosting Manager (SHM) system. It allows users to perform actions such as checking their account balance, listing services, and ordering new services directly through Telegram.

## Prerequisites

*   Python 3.9+
*   Docker (optional, for containerized deployment)

## Setup & Configuration

1.  **Get the Code:**
    *   Clone the repository containing this bot, or otherwise obtain the `telegram_bot` directory.

2.  **Navigate to Directory:**
    ```bash
    cd path/to/your/telegram_bot
    ```

3.  **Create `.env` File:**
    *   In the `telegram_bot` directory, create a file named `.env`.
    *   Copy the contents of `.env.example` into your new `.env` file.
    *   Modify the `.env` file with your actual credentials:
        *   `TELEGRAM_BOT_TOKEN`: Your Telegram Bot's API token.
        *   `SHM_API_URL`: The base URL for the SHM API.
    *   *Note:* The current bot implementation primarily uses the Telegram username for SHM user identification. Future enhancements might require additional credentials like `SHM_API_USER` or `SHM_API_PASSWORD`, which would be added to the `.env` file.

4.  **Install Dependencies:**
    *   It's highly recommended to use a Python virtual environment.
        ```bash
        python3 -m venv venv
        source venv/bin/activate  # On Windows use `venv\Scripts\activate`
        ```
    *   Install the required packages:
        ```bash
        pip install -r requirements.txt
        ```

## Running the Bot

### Locally

Once dependencies are installed and the `.env` file is configured:

```bash
python bot.py
```

### With Docker

Ensure Docker is installed and running. These commands should be run from within the `telegram_bot` directory.

1.  **Build the Docker Image:**
    ```bash
    docker build -t shm_telegram_bot .
    ```

2.  **Run the Docker Container:**
    *   You can pass the environment variables from your `.env` file directly:
        ```bash
        docker run -d --name shm-bot --env-file .env shm_telegram_bot
        ```
    *   Alternatively, pass environment variables individually:
        ```bash
        docker run -d --name shm-bot \
          -e TELEGRAM_BOT_TOKEN='your_actual_telegram_token' \
          -e SHM_API_URL='your_actual_shm_api_url' \
          shm_telegram_bot
        ```
    *   The `-d` flag runs the container in detached mode. Use `docker logs shm-bot` to view logs.

## Available Commands

*   `/start`: Displays a welcome message and quick action buttons.
*   `/help`: Shows a help message listing all available commands.
*   `/balance`: Checks your SHM account balance.
*   `/services`: Lists your active SHM services.
*   `/order_service <service_id>`: Orders a new SHM service (e.g., `/order_service basic_hosting`).
    *   *Note:* This command relies on a hypothetical `api/order_service` endpoint being available on the SHM server.

## SHM API Interaction

This bot interacts with a backend SHM (Server Hosting Manager) / billing system API to retrieve user-specific information and perform actions. For more details on the specific API endpoints the bot uses or expects, please refer to the `SHM_API_INTERACTIONS.md` document within this directory.

---

*This README provides a basic guide. Ensure your SHM API is correctly configured and accessible for the bot to function as expected.*
