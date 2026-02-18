import logging

from aiokafka import ConsumerRebalanceListener

log = logging.getLogger(__name__)


class RebalanceHandler(ConsumerRebalanceListener):
    """
    A listener that handles partition assignment changes during a consumer group
    rebalance. It signals the consumer manager when a rebalance is in progress
    to allow the manager to pause processing.
    """

    def __init__(self, consumer_manager):
        """
        Args:
            consumer_manager: An instance of the ConsumerManager.
        """
        self.consumer_manager = consumer_manager

    async def on_partitions_revoked(self, revoked):
        """
        Called when partitions are revoked from the consumer.
        Sets the 'rebalance_in_progress' flag to True.
        """
        log.warning(f"Rebalance detected: Revoking partitions {revoked}")
        self.consumer_manager._rebalance_in_progress = True

    async def on_partitions_assigned(self, assigned):
        """
        Called when new partitions are assigned to the consumer.
        Sets the 'rebalance_in_progress' flag to False.
        """
        log.info(f"Rebalance detected: Assigned partitions {assigned}")
        self.consumer_manager._rebalance_in_progress = False
