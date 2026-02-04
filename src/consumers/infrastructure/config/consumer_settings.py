from pydantic import BaseModel, ConfigDict, Field


class KafkaConsumerConfig(BaseModel):
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
