from pydantic import BaseModel, ConfigDict, Field


class KafkaProducerConfig(BaseModel):
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
