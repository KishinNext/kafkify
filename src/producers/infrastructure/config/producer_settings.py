from pydantic import BaseModel, ConfigDict, Field


class KafkaProducerConfig(BaseModel):
    """
    Configuration settings for Kafka Producer.

    Attributes:
        bootstrap_servers (str): Comma-separated list of Kafka servers.
        client_id (str): Client identifier for traceability.
        acks (str): Acknowledgment level for message delivery.
        request_timeout_ms (int): Timeout for requests in milliseconds.
        max_batch_size (int): Maximum batch size in bytes.
        linger_ms (int): Time to wait before sending a batch.
        enable_idempotence (bool): Enables idempotent message delivery.

    Adds extra fields to allow future extensions without breaking changes.
    """

    model_config = ConfigDict(extra="allow")

    bootstrap_servers: str = Field(
        ..., description="Kafka servers separated by commas."
    )
    client_id: str = Field(
        default="my-app-producer", description="Client ID for traceability."
    )
    acks: str = Field(default="all", description="Acknowledgment level (0, 1, all).")
    request_timeout_ms: int = Field(
        default=40000, description="Request timeout in milliseconds."
    )
    max_batch_size: int = Field(default=16384, description="Batch size in bytes.")
    linger_ms: int = Field(default=0, description="Wait time before sending batch.")
    enable_idempotence: bool = Field(
        default=True, description="Prevents duplicates (requires acks=all)."
    )
    retry_backoff_ms: int = Field(
        default=100, description="Time to wait before retrying a failed request."
    )
    metadata_max_age_ms: int = Field(
        default=30000, description="Metadata refresh interval in milliseconds."
    )
