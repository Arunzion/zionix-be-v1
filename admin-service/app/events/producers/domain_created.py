import json
import logging
from typing import Optional

# Import Kafka producer (assuming a Kafka client is set up)
# This is a placeholder and should be replaced with actual Kafka implementation
# such as aiokafka or confluent-kafka-python
from app.events.kafka_client import get_producer

logger = logging.getLogger(__name__)

async def publish_domain_created_event(domain_id: int, domain_name: str) -> None:
    """
    Publishes a domain created event to Kafka
    
    Args:
        domain_id: The ID of the created domain
        domain_name: The name of the created domain
    """
    try:
        # Create event payload
        event_data = {
            "event_type": "domain_created",
            "domain_id": domain_id,
            "domain_name": domain_name,
        }
        
        # Serialize to JSON
        event_json = json.dumps(event_data)
        
        # Get Kafka producer
        producer = await get_producer()
        
        # Send message to Kafka topic
        await producer.send_and_wait(
            topic="domain-events",
            value=event_json.encode("utf-8"),
            key=str(domain_id).encode("utf-8")
        )
        
        logger.info(f"Published domain_created event for domain {domain_id}")
    except Exception as e:
        logger.error(f"Failed to publish domain_created event: {str(e)}")
        # In a production system, you might want to implement retry logic
        # or store failed events for later processing