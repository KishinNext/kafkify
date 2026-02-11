# Kafkify: Dual-Server Architecture Example

This project demonstrates a robust Kafka Producer and Consumer implementation using FastAPI, separated into two independent servers to ensure non-blocking operations and scalability.

## 🏗️ Architecture

- **Producer Server (Port 8000):** REST API for sending messages to Kafka.
- **Consumer Server (Port 8001):** Background service for continuous message consumption.

Both interact independently with a Kafka Broker (Docker).

## 📋 Prerequisites

- **Just** (task runner): `brew install just`
- **jq** (JSON processor): `brew install jq`
- **Python Dependencies**: `pip install uv && uv sync`

## 🚀 Quick Start

1.  **Start Kafka:**
    ```bash
    docker-compose up -d
    ```

2.  **Start Servers** (in separate terminals):
    ```bash
    just run-producer  # http://localhost:8000
    just run-consumer  # http://localhost:8001
    ```

3.  **Produce & Consume:**
    ```bash
    just create-people 10    # Generate 10 events
    ```

## 🛠️ Key Commands

| Command | Description |
| :--- | :--- |
| `just health-producer` | Check Producer status |
| `just health-consumer` | Check Consumer status |

## 🔌 API Documentation

- [https://kishinnext.github.io/kafkify.github.io/](https://kishinnext.github.io/kafkify.github.io/)
