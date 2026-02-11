from pydantic import BaseModel, ConfigDict, Field


class KafkaConsumerConfig(BaseModel):
    """
    Configuration model for Kafka consumer settings.

    Attributes:
        bootstrap_servers (str): Kafka servers separated by commas.
        group_id (str): Consumer group ID.
        enable_auto_commit (bool): Enable automatic offset committing.
        auto_offset_reset (str): Offset reset policy (earliest or latest).
        isolation_level (str): Isolation level for consuming messages.
        max_poll_interval_ms (int): Maximum delay between invocations of poll().
        retry_backoff_ms (int): Time to wait before retrying a failed fetch.
    
    Adds extra fields to allow future extensions without breaking changes.
    """
    model_config = ConfigDict(extra="allow")

    bootstrap_servers: str = Field(
        ..., description="Kafka servers separated by commas."
    )
    group_id: str = Field(default="my-app-consumer", description="Consumer group ID.")
    enable_auto_commit: bool = Field(
        default=False, description="Enable automatic offset committing."
    )
    auto_offset_reset: str = Field(
        default="earliest", description="Offset reset policy (earliest or latest)."
    )
    isolation_level: str = Field(
        default="read_committed", description="Isolation level for consuming messages."
    )
    max_poll_interval_ms: int = Field(
        default=300000, description="Maximum delay between invocations of poll()."
    )
    retry_backoff_ms: int = Field(
        default=2000, description="Time to wait before retrying a failed fetch."
    )