# Welcome to Kafkify

**Kafkify** is a lightweight, opinionated wrapper around `aiokafka` designed to simplify the integration of Kafka consumers and producers into Python applications, particularly those built with **FastAPI**.

It provides a structured way to handle Kafka messages, manage configuration, and route messages to specific handlers based on topics and codes.

## Key Features

*   **Easy Configuration**: Uses Pydantic models for type-safe and clear configuration.
*   **Routing**: Decorator-based routing similar to FastAPI for handling specific topics and message codes.
*   **Resilience**: Built-in handling for rebalancing and offset management.
*   **FastAPI Integration**: Designed to work seamlessly with FastAPI's lifespan events.

## Getting Started

Check out the **User Guide** to understand how to use the Consumer and Producer components, or jump straight into the **Examples** to see them in action.
